# 基准测试示例

这个目录包含使用基准测试工具的示例代码。

## 文件说明

- `benchmark_examples.py` - Python编程示例

## 运行示例

### 方式1：运行示例脚本

```bash
# 进入项目根目录
cd /path/to/doc_to_md
python examples/benchmark_examples.py
```

这将运行基本示例并在 `examples/test_output/` 目录生成报告。

### 方式2：直接使用命令行工具

```bash
# 进入项目根目录
cd /path/to/doc_to_md

# 测试单个引擎
python benchmark.py --engines local

# 测试多个引擎
python benchmark.py --engines local markitdown paddleocr
```

## 示例说明

### 示例1：基本使用

展示如何：
- 创建测试文件
- 初始化基准测试对象
- 运行测试
- 生成和保存报告

## 自定义示例

你可以基于这些示例创建自己的测试脚本：

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

## 输出

示例运行后会在 `examples/test_output/` 目录生成以下文件：

- `sample_test.txt` - 示例测试文件
- `example1_report.md` - 示例1的报告
- 其他报告文件

## 故障排除

### 找不到模块错误

确保从项目根目录运行示例：

```bash
cd /path/to/doc_to_md
python examples/benchmark_examples.py
```

### 引擎失败

如果某些引擎测试失败，检查：
- 是否安装了必要的依赖
- 是否配置了API密钥（对于远程引擎）
- 查看生成报告中的"失败详情"部分

## 更多信息

查看完整文档：
- 主README: `../README.md`
- 基准测试指南: `../README_BENCHMARK.md`
- 英文文档: `../README_BENCHMARK.md`
- 基准测试代码: `../benchmark.py`
