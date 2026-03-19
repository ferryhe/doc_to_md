# Benchmark Examples

This directory contains example code for using the benchmark tool.

> **Chinese Documentation**: For Chinese version, see [../readme_cn/EXAMPLES_CN.md](../readme_cn/EXAMPLES_CN.md)

## Files

- `benchmark_examples.py` - Python programming examples

## Running Examples

### Method 1: Run example script

```bash
# Navigate to the project root directory
cd /path/to/doc_to_md
python examples/benchmark_examples.py
```

This will run basic examples and generate reports in the `examples/test_output/` directory.

### Method 2: Use command-line tool directly

```bash
# Navigate to the project root directory
cd /path/to/doc_to_md

# Test single engine
python benchmark.py --engines local

# Test multiple engines
python benchmark.py --engines local markitdown paddleocr
```

## Example Descriptions

### Example 1: Basic Usage

Shows how to:
- Create test files
- Initialize benchmark object
- Run tests
- Generate and save reports

## Custom Examples

You can create your own test scripts based on these examples:

```python
from pathlib import Path
from benchmark import EngineBenchmark, ChineseReportGenerator

# Create your test file
test_file = Path("my_document.pdf")

# Select engines to test
benchmark = EngineBenchmark(
    engines_to_test=[
        ("local", None),
        ("markitdown", None),
        # Add more engines...
    ]
)

# Run test
result = benchmark.run_benchmark(test_file)

# Generate report
generator = ChineseReportGenerator(result)
generator.save_report(Path("my_report.md"))
```

## Output

After running examples, the following files are generated in `examples/test_output/`:

- `sample_test.txt` - Sample test file
- `example1_report.md` - Report from example 1
- Other report files

## Troubleshooting

### Module Not Found Error

Make sure to run examples from the project root directory:

```bash
cd /path/to/doc_to_md
python examples/benchmark_examples.py
```

### Engine Failures

If some engine tests fail, check:
- Are necessary dependencies installed?
- Are API keys configured (for remote engines)?
- See "Failure Details" section in generated reports

## More Information

See full documentation:
- Main README: `../README.md`
- Benchmark guide: `../README_BENCHMARK.md`
- Chinese docs: `../readme_cn/`
- Benchmark code: `../benchmark.py`
