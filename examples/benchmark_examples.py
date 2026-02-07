#!/usr/bin/env python3
"""
示例：如何使用基准测试工具 / Example: How to use the benchmark tool

这个脚本展示了如何在Python代码中使用基准测试工具。
This script demonstrates how to use the benchmark tool in Python code.
"""
from pathlib import Path
import sys

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from benchmark import EngineBenchmark, ChineseReportGenerator, create_sample_test_file


def example_1_basic_usage():
    """示例1：基本使用 / Example 1: Basic usage"""
    print("=" * 60)
    print("示例1：基本使用")
    print("Example 1: Basic usage")
    print("=" * 60)
    
    # 创建示例测试文件
    test_file = create_sample_test_file(Path("examples/test_output"))
    
    # 创建基准测试对象，只测试本地引擎
    benchmark = EngineBenchmark(
        engines_to_test=[
            ("local", None),
        ]
    )
    
    # 运行测试
    result = benchmark.run_benchmark(test_file)
    
    # 生成并保存报告
    generator = ChineseReportGenerator(result)
    report_path = Path("examples/test_output/example1_report.md")
    generator.save_report(report_path)
    
    print(f"\n✅ 报告已保存: {report_path}")


def main():
    """主函数 / Main function"""
    print("\n" + "=" * 60)
    print("基准测试工具示例程序")
    print("Benchmark Tool Example Program")
    print("=" * 60)
    
    # 运行示例
    try:
        example_1_basic_usage()
        
        print("\n" + "=" * 60)
        print("示例运行完成！")
        print("Example completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误 / Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
