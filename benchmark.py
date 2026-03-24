#!/usr/bin/env python3
# ruff: noqa: E402
"""
Engine Comparison Benchmark Tool

This script tests and compares the performance of different document conversion engines,
measuring conversion time, output characteristics (Markdown length and asset count), 
and success rates.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any

# Ensure the package under src/ is importable when running from a source checkout.
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

settings_module = import_module("doc_to_md.config.settings")
logic_module = import_module("doc_to_md.apps.conversion.logic")
base_module = import_module("doc_to_md.engines.base")

EngineName = settings_module.EngineName
get_settings = settings_module.get_settings
ENGINE_REGISTRY = logic_module.ENGINE_REGISTRY
ENGINES_REQUIRING_MODEL = logic_module.ENGINES_REQUIRING_MODEL
Engine = base_module.Engine
EngineResponse = base_module.EngineResponse


@dataclass
class EngineResult:
    """Result from testing a single engine"""
    engine_name: str
    model: str
    success: bool
    conversion_time: float
    markdown_length: int = 0
    num_assets: int = 0
    error_message: str | None = None


@dataclass
class BenchmarkResult:
    """Complete benchmark test results"""
    timestamp: str
    test_file: str
    file_size_bytes: int
    results: list[EngineResult] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'timestamp': self.timestamp,
            'test_file': self.test_file,
            'file_size_bytes': self.file_size_bytes,
            'results': [asdict(r) for r in self.results]
        }


class EngineBenchmark:
    """Engine benchmark testing class"""
    
    def __init__(self, engines_to_test: list[tuple[EngineName, str | None]] | None = None):
        """
        Initialize benchmark testing
        
        Args:
            engines_to_test: List of engines to test, format: [(engine_name, model), ...]
                           If None, will test all available engines
        """
        self.settings = get_settings()
        
        if engines_to_test is None:
            # Default: test all engines
            self.engines_to_test = [
                ("local", None),
                ("markitdown", None),
                ("paddleocr", None),
                ("docling", None),
                ("marker", None),
                ("mineru", None),
                ("mistral", self.settings.mistral_default_model),
                ("deepseekocr", self.settings.siliconflow_default_model),
            ]
        else:
            self.engines_to_test = engines_to_test
    
    def _create_engine(self, engine_name: EngineName, model: str | None) -> tuple[Engine | None, str | None]:
        """
        Create engine instance
        
        Returns:
            Tuple of (engine_instance, error_message). If creation succeeds, error_message is None.
        """
        try:
            engine_cls = ENGINE_REGISTRY.get(engine_name)
            if engine_cls is None:
                return None, f"Engine '{engine_name}' not found in registry"
            
            # Some engines require a model parameter
            if engine_name in ENGINES_REQUIRING_MODEL:
                return engine_cls(model=model), None
            return engine_cls(), None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed to create engine {engine_name}: {error_msg}")
            return None, error_msg
    
    def test_engine(self, engine_name: EngineName, model: str | None, test_file: Path) -> EngineResult:
        """
        Test a single engine
        
        Args:
            engine_name: Engine name
            model: Model name (optional)
            test_file: Test file path
        
        Returns:
            EngineResult: Test results
        """
        print(f"\n📊 Testing engine: {engine_name} (model: {model or 'default'})")
        
        # Create engine instance
        engine, create_error = self._create_engine(engine_name, model)
        if engine is None:
            return EngineResult(
                engine_name=engine_name,
                model=model or "default",
                success=False,
                conversion_time=0.0,
                error_message=create_error or "Failed to create engine instance (missing dependencies or configuration)"
            )
        
        # Execute conversion and measure time
        try:
            start_time = time.time()
            response: EngineResponse = engine.convert(test_file)
            conversion_time = time.time() - start_time
            
            # Collect results
            result = EngineResult(
                engine_name=engine_name,
                model=response.model,
                success=True,
                conversion_time=conversion_time,
                markdown_length=len(response.markdown),
                num_assets=len(response.assets)
            )
            
            print(f"✅ Success - Time: {conversion_time:.2f}s, Markdown length: {result.markdown_length}, Assets: {result.num_assets}")
            return result
            
        except Exception as e:
            conversion_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed - {error_msg}")
            return EngineResult(
                engine_name=engine_name,
                model=model or "default",
                success=False,
                conversion_time=conversion_time,
                error_message=error_msg
            )
    
    def run_benchmark(self, test_file: Path) -> BenchmarkResult:
        """
        Run complete benchmark test
        
        Args:
            test_file: Test file path
        
        Returns:
            BenchmarkResult: Complete test results
        """
        print(f"\n{'='*60}")
        print("Starting benchmark test")
        print(f"Test file: {test_file}")
        print(f"File size: {test_file.stat().st_size / 1024:.2f} KB")
        print(f"{'='*60}")
        
        benchmark_result = BenchmarkResult(
            timestamp=datetime.now().isoformat(),
            test_file=str(test_file),
            file_size_bytes=test_file.stat().st_size
        )
        
        for engine_name, model in self.engines_to_test:
            result = self.test_engine(engine_name, model, test_file)
            benchmark_result.results.append(result)
        
        return benchmark_result


class ChineseReportGenerator:
    """Chinese comparison report generator"""
    
    def __init__(self, benchmark_result: BenchmarkResult):
        self.result = benchmark_result
    
    def _format_time(self, seconds: float) -> str:
        """Format time"""
        if seconds < 0.01:
            return "< 0.01秒"
        return f"{seconds:.2f}秒"
    
    def _format_size(self, bytes_size: int) -> str:
        """Format file size"""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.2f} KB"
        else:
            return f"{bytes_size / (1024 * 1024):.2f} MB"
    
    def _get_rating(self, time: float, success: bool) -> str:
        """Get performance rating"""
        if not success:
            return "❌ 失败"
        if time < 5:
            return "⭐⭐⭐⭐⭐ 优秀"
        elif time < 15:
            return "⭐⭐⭐⭐ 良好"
        elif time < 30:
            return "⭐⭐⭐ 一般"
        elif time < 60:
            return "⭐⭐ 较慢"
        else:
            return "⭐ 缓慢"
    
    def generate_markdown_report(self) -> str:
        """Generate Chinese comparison report in Markdown format"""
        lines = []
        
        # Title and basic information
        lines.append("# 文档转换引擎对比测试报告")
        lines.append("")
        lines.append("## 测试信息")
        lines.append("")
        lines.append(f"- **测试时间**: {self.result.timestamp}")
        lines.append(f"- **测试文件**: `{self.result.test_file}`")
        lines.append(f"- **文件大小**: {self._format_size(self.result.file_size_bytes)}")
        lines.append(f"- **测试引擎数量**: {len(self.result.results)}")
        lines.append("")
        
        # Success rate statistics
        successful = sum(1 for r in self.result.results if r.success)
        failed = len(self.result.results) - successful
        success_rate = (successful / len(self.result.results) * 100) if self.result.results else 0
        
        lines.append("## 整体统计")
        lines.append("")
        lines.append(f"- **成功**: {successful} 个引擎")
        lines.append(f"- **失败**: {failed} 个引擎")
        lines.append(f"- **成功率**: {success_rate:.1f}%")
        lines.append("")
        
        # Performance rankings
        successful_results = [r for r in self.result.results if r.success]
        if successful_results:
            lines.append("## 性能排名（按转换时间）")
            lines.append("")
            sorted_results = sorted(successful_results, key=lambda r: r.conversion_time)
            for i, result in enumerate(sorted_results, 1):
                lines.append(f"{i}. **{result.engine_name}** ({result.model})")
                lines.append(f"   - 转换时间: {self._format_time(result.conversion_time)}")
                lines.append(f"   - 输出长度: {result.markdown_length:,} 字符")
                lines.append(f"   - 资源数量: {result.num_assets}")
                lines.append("")
        
        # Detailed test results table
        lines.append("## 详细测试结果")
        lines.append("")
        lines.append("| 引擎名称 | 模型 | 状态 | 转换时间 | Markdown长度 | 资源数 | 性能评级 |")
        lines.append("|---------|------|------|---------|------------|-------|---------|")
        
        for result in self.result.results:
            status = "✅ 成功" if result.success else "❌ 失败"
            time_str = self._format_time(result.conversion_time) if result.success else "-"
            md_len = f"{result.markdown_length:,}" if result.success else "-"
            assets = str(result.num_assets) if result.success else "-"
            rating = self._get_rating(result.conversion_time, result.success)
            
            lines.append(
                f"| {result.engine_name} | {result.model} | {status} | "
                f"{time_str} | {md_len} | {assets} | {rating} |"
            )
        
        lines.append("")
        
        # Error information
        failed_results = [r for r in self.result.results if not r.success]
        if failed_results:
            lines.append("## 失败详情")
            lines.append("")
            for result in failed_results:
                lines.append(f"### {result.engine_name} ({result.model})")
                lines.append("")
                lines.append("```")
                lines.append(result.error_message or "未知错误")
                lines.append("```")
                lines.append("")
        
        # Engine characteristics analysis
        lines.append("## 引擎特点分析")
        lines.append("")
        
        engine_descriptions = {
            "local": {
                "name": "本地引擎",
                "pros": ["无需外部依赖", "快速简单", "适合纯文本文档", "无网络请求"],
                "cons": ["OCR能力有限", "格式支持较少", "输出质量一般"],
                "best_for": "纯文本文件、快速测试、离线环境"
            },
            "mistral": {
                "name": "Mistral OCR",
                "pros": ["强大的OCR能力", "支持图像提取", "高质量输出", "支持多种格式"],
                "cons": ["需要API密钥", "有网络延迟", "可能有成本", "依赖外部服务"],
                "best_for": "复杂PDF文档、高质量OCR需求、有预算的项目"
            },
            "deepseekocr": {
                "name": "DeepSeek OCR",
                "pros": ["优秀的中文OCR", "视觉理解能力强", "支持复杂布局", "输出质量高"],
                "cons": ["需要API密钥", "网络依赖", "处理速度可能较慢"],
                "best_for": "中文文档、复杂排版、需要高精度的场景"
            },
            "markitdown": {
                "name": "MarkItDown",
                "pros": ["支持多种Office格式", "本地处理", "快速", "保真度高"],
                "cons": ["对扫描PDF支持有限", "需要安装依赖", "插件可能不稳定"],
                "best_for": "Office文档（DOCX、PPTX、XLSX）、本地处理需求"
            },
            "paddleocr": {
                "name": "PaddleOCR",
                "pros": ["本地OCR", "支持多语言", "可GPU加速", "开源免费"],
                "cons": ["需要大量依赖", "首次使用需下载模型", "准确度中等"],
                "best_for": "本地OCR需求、批量处理、中文文档"
            },
            "docling": {
                "name": "Docling",
                "pros": ["IBM企业级方案", "结构化提取", "支持复杂文档", "高质量输出"],
                "cons": ["依赖较重", "处理速度较慢", "配置复杂"],
                "best_for": "企业文档、结构化提取、需要高质量的场景"
            },
            "marker": {
                "name": "Marker",
                "pros": ["专注PDF转换", "保留格式", "支持LLM增强", "图像提取"],
                "cons": ["依赖重", "可能需要GPU", "处理速度一般"],
                "best_for": "学术论文、复杂PDF、需要保留格式"
            },
            "mineru": {
                "name": "MinerU",
                "pros": ["多种解析方法", "GPU加速", "支持复杂布局", "开源"],
                "cons": ["依赖重", "配置复杂", "资源消耗大"],
                "best_for": "研究用途、批量处理、有GPU环境"
            }
        }
        
        for result in self.result.results:
            if result.engine_name in engine_descriptions:
                desc = engine_descriptions[result.engine_name]
                lines.append(f"### {desc['name']} (`{result.engine_name}`)")
                lines.append("")
                
                status_emoji = "✅" if result.success else "❌"
                lines.append(f"**测试状态**: {status_emoji} {'成功' if result.success else '失败'}")
                lines.append("")
                
                lines.append("**优点**:")
                for pro in desc["pros"]:
                    lines.append(f"- {pro}")
                lines.append("")
                
                lines.append("**缺点**:")
                for con in desc["cons"]:
                    lines.append(f"- {con}")
                lines.append("")
                
                lines.append(f"**最适合**: {desc['best_for']}")
                lines.append("")
        
        # Usage recommendations
        lines.append("## 使用建议")
        lines.append("")
        lines.append("根据测试结果，我们提供以下使用建议：")
        lines.append("")
        
        if successful_results:
            fastest = min(successful_results, key=lambda r: r.conversion_time)
            lines.append(f"1. **速度优先**: 使用 `{fastest.engine_name}` 引擎（{self._format_time(fastest.conversion_time)}）")
            lines.append("")
            
            # Find the engine with longest output (usually means most detailed)
            longest = max(successful_results, key=lambda r: r.markdown_length)
            lines.append(f"2. **输出详细度优先**: 使用 `{longest.engine_name}` 引擎（输出 {longest.markdown_length:,} 字符）")
            lines.append("")
        
        lines.append("3. **成本考虑**:")
        lines.append("   - 免费方案: `local`, `markitdown`, `paddleocr`, `docling`, `marker`, `mineru`")
        lines.append("   - 付费方案: `mistral`, `deepseekocr`（需要API密钥）")
        lines.append("")
        
        lines.append("4. **文档类型建议**:")
        lines.append("   - 纯文本/简单文档: `local` 或 `markitdown`")
        lines.append("   - Office文档: `markitdown`")
        lines.append("   - 扫描PDF/图片: `mistral`, `deepseekocr`, 或 `paddleocr`")
        lines.append("   - 复杂学术PDF: `marker` 或 `docling`")
        lines.append("   - 中文文档: `deepseekocr` 或 `paddleocr`")
        lines.append("")
        
        # Conclusion
        lines.append("## 结论")
        lines.append("")
        lines.append(f"本次测试共评估了 {len(self.result.results)} 个文档转换引擎，"
                    f"成功率为 {success_rate:.1f}%。")
        lines.append("")
        
        if successful_results:
            lines.append("每个引擎都有其特定的优势和适用场景。选择合适的引擎需要综合考虑：")
            lines.append("")
            lines.append("- 文档类型和复杂度")
            lines.append("- 处理速度要求")
            lines.append("- 输出详细度要求")
            lines.append("- 成本预算")
            lines.append("- 是否需要离线处理")
            lines.append("- 语言支持（特别是中文）")
        else:
            lines.append("⚠️ 所有引擎都失败了。请检查：")
            lines.append("- 测试文件是否有效")
            lines.append("- 必要的依赖是否已安装")
            lines.append("- API密钥是否已配置（对于远程引擎）")
        
        lines.append("")
        lines.append("---")
        lines.append(f"*报告生成时间: {self.result.timestamp}*")
        
        return "\n".join(lines)
    
    def save_report(self, output_path: Path) -> None:
        """Save report to file"""
        report = self.generate_markdown_report()
        output_path.write_text(report, encoding="utf-8")
        print(f"\n✅ Report saved to: {output_path}")


def create_sample_test_file(output_dir: Path) -> Path:
    """Create sample test file"""
    output_dir.mkdir(parents=True, exist_ok=True)
    test_file = output_dir / "sample_test.txt"
    
    content = """# Test Document - Document Conversion Test

This is a sample file for testing document conversion engines.

## Features

1. Multiple engine support
2. Performance comparison
3. Quality assessment

## Tech Stack

- Python 3.10+
- Typer (CLI framework)
- Pydantic (Configuration management)
- Multiple OCR/ML engines

## Mixed Chinese-English Content

Document conversion is a complex task that requires considering multiple factors:

1. Accuracy
2. Speed
3. Cost
4. Format support

Test content includes plain text, special characters (@#$%^&*), numbers (123456), etc.
"""
    
    test_file.write_text(content, encoding="utf-8")
    return test_file


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Engine Comparison Benchmark Tool"
    )
    parser.add_argument(
        "--test-file",
        type=Path,
        help="Path to test file (will create a sample if not provided)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark_results"),
        help="Output directory (default: benchmark_results)"
    )
    parser.add_argument(
        "--engines",
        type=str,
        nargs="+",
        help="List of engines to test (e.g., local mistral deepseekocr)"
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Also save results in JSON format"
    )
    
    args = parser.parse_args()
    
    # Prepare test file
    if args.test_file and args.test_file.exists():
        test_file = args.test_file
        print(f"Using test file: {test_file}")
    elif args.test_file:
        # User provided a file path but it doesn't exist - this is an error
        print(f"Error: Test file '{args.test_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    else:
        # No test file provided, create a sample
        print("Creating sample test file...")
        test_file = create_sample_test_file(args.output_dir)
        print(f"Sample test file created: {test_file}")
    
    # Prepare engine list
    engines_to_test = None
    if args.engines:
        settings = get_settings()
        engines_to_test = []
        for engine_name in args.engines:
            if engine_name in {"mistral"}:
                engines_to_test.append((engine_name, settings.mistral_default_model))
            elif engine_name in {"deepseekocr"}:
                engines_to_test.append((engine_name, settings.siliconflow_default_model))
            else:
                engines_to_test.append((engine_name, None))
        print(f"Will test engines: {', '.join(args.engines)}")
    else:
        print("Will test all available engines")
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run benchmark test
    benchmark = EngineBenchmark(engines_to_test)
    result = benchmark.run_benchmark(test_file)
    
    # Generate report
    print(f"\n{'='*60}")
    print("Generating Chinese comparison report...")
    print(f"{'='*60}")
    
    generator = ChineseReportGenerator(result)
    
    # Save Markdown report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = args.output_dir / f"comparison_report_{timestamp}.md"
    generator.save_report(report_path)
    
    # Optional: Save JSON format
    if args.save_json:
        json_path = args.output_dir / f"benchmark_result_{timestamp}.json"
        json_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✅ JSON results saved to: {json_path}")
    
    print(f"\n{'='*60}")
    print("Benchmark test completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
