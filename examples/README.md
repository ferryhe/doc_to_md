# 基准测试示例 / Benchmark Examples

这个目录包含使用基准测试工具的示例代码。

This directory contains example code for using the benchmark tool.

## 文件说明 / Files

- `benchmark_examples.py` - Python编程示例 / Python programming examples

## 运行示例 / Running Examples

### 方式1：运行示例脚本 / Method 1: Run example script

```bash
cd /home/runner/work/doc_to_md/doc_to_md
python examples/benchmark_examples.py
```

这将运行基本示例并在 `examples/test_output/` 目录生成报告。

This will run basic examples and generate reports in the `examples/test_output/` directory.

### 方式2：直接使用命令行工具 / Method 2: Use command-line tool directly

```bash
cd /home/runner/work/doc_to_md/doc_to_md

# 测试单个引擎
python benchmark.py --engines local

# 测试多个引擎
python benchmark.py --engines local markitdown paddleocr
```

## 示例说明 / Example Descriptions

### 示例1：基本使用 / Example 1: Basic Usage

展示如何：
- 创建测试文件
- 初始化基准测试对象
- 运行测试
- 生成和保存报告

Shows how to:
- Create test files
- Initialize benchmark object
- Run tests
- Generate and save reports

## 自定义示例 / Custom Examples

你可以基于这些示例创建自己的测试脚本：

You can create your own test scripts based on these examples:

```python
from pathlib import Path
from benchmark import EngineBenchmark, ChineseReportGenerator

# 创建你的测试文件
test_file = Path("my_document.pdf")

# 选择要测试的引擎
benchmark = EngineBenchmark(
    engines_to_test=[
        ("local", None),
        ("markitdown", None),
        # 添加更多引擎...
    ]
)

# 运行测试
result = benchmark.run_benchmark(test_file)

# 生成报告
generator = ChineseReportGenerator(result)
generator.save_report(Path("my_report.md"))
```

## 输出 / Output

示例运行后会在 `examples/test_output/` 目录生成以下文件：

After running examples, the following files are generated in `examples/test_output/`:

- `sample_test.txt` - 示例测试文件 / Sample test file
- `example1_report.md` - 示例1的报告 / Report from example 1
- 其他报告文件 / Other report files

## 故障排除 / Troubleshooting

### 找不到模块错误 / Module Not Found Error

确保从项目根目录运行示例：

Make sure to run examples from the project root directory:

```bash
cd /home/runner/work/doc_to_md/doc_to_md
python examples/benchmark_examples.py
```

### 引擎失败 / Engine Failures

如果某些引擎测试失败，检查：
- 是否安装了必要的依赖
- 是否配置了API密钥（对于远程引擎）
- 查看生成报告中的"失败详情"部分

If some engine tests fail, check:
- Are necessary dependencies installed?
- Are API keys configured (for remote engines)?
- See "Failure Details" section in generated reports

## 更多信息 / More Information

查看完整文档：
- 主README: `../README.md`
- 基准测试指南: `../README_BENCHMARK.md`
- 基准测试代码: `../benchmark.py`

See full documentation:
- Main README: `../README.md`
- Benchmark guide: `../README_BENCHMARK.md`
- Benchmark code: `../benchmark.py`
