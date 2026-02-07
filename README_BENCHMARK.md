# Engine Benchmark Tool Guide

## Introduction

This is a tool for testing and comparing the performance of different document conversion engines. It automatically tests multiple engines and generates detailed comparison reports.

> **Chinese Documentation**: For Chinese documentation, see [readme_cn/README_BENCHMARK_CN.md](readme_cn/README_BENCHMARK_CN.md)

## Features

- ✅ **Automated Testing** - Test multiple engines with a single command
- 📊 **Performance Metrics** - Conversion time, success rate, and output quality
- 📝 **Detailed Reports** - Generate comprehensive comparison reports
- 🎯 **Engine Analysis** - Pros/cons and use cases for each engine
- 🔧 **Flexible Configuration** - Custom test files and engine selection

## Quick Start

### Basic Usage

```bash
# Test all available engines
python benchmark.py

# Test specific engines
python benchmark.py --engines local markitdown

# Use custom test file
python benchmark.py --test-file path/to/your/document.pdf

# Save results in JSON format
python benchmark.py --save-json
```

### Advanced Usage

```bash
# Test multiple engines and save to specific directory
python benchmark.py \
  --engines local markitdown paddleocr docling \
  --output-dir my_test_results \
  --save-json

# Test OCR engines with PDF file
python benchmark.py \
  --test-file document.pdf \
  --engines mistral deepseekocr paddleocr

# Test all local engines (no API keys required)
python benchmark.py \
  --engines local markitdown paddleocr docling marker mineru
```

## Supported Engines

### Local Engines (No API Key Required)

1. **local** - Basic text extraction
2. **markitdown** - Microsoft MarkItDown (Install: `pip install markitdown`)
3. **paddleocr** - PaddleOCR (Install: `pip install ".[paddleocr]"`)
4. **docling** - IBM Docling (Install: `pip install ".[docling]"`)
5. **marker** - Marker PDF (Install: `pip install ".[marker]"`)
6. **mineru** - MinerU (Install: `pip install ".[mineru]"`)

### Cloud Engines (API Key Required)

7. **mistral** - Mistral OCR API (Set `MISTRAL_API_KEY` in `.env`)
8. **deepseekocr** - DeepSeek OCR API (Set `SILICONFLOW_API_KEY` in `.env`)

## Report Contents

The generated report includes:

1. **Test Information** - Timestamp, file info, size
2. **Overall Statistics** - Success/failure counts, success rate
3. **Performance Rankings** - Sorted by conversion time
4. **Detailed Results Table** - Status, time, output length, assets, ratings
5. **Engine Analysis** - Pros, cons, best use cases
6. **Usage Recommendations** - Speed vs quality, cost, document type suggestions
7. **Failure Details** - Error messages and troubleshooting

## Output Files

Generated in the output directory (default: `benchmark_results/`):

1. `comparison_report_YYYYMMDD_HHMMSS.md` - Comparison report
2. `benchmark_result_YYYYMMDD_HHMMSS.json` - Raw data (with `--save-json`)
3. `sample_test.txt` - Sample test file (if no custom file provided)

## Use Cases

### Scenario 1: Choosing the Right Engine
```bash
python benchmark.py --test-file your_document.pdf --save-json
```

### Scenario 2: Performance Validation
```bash
python benchmark.py \
  --test-file production_sample.pdf \
  --engines mistral deepseekocr \
  --output-dir validation_results
```

### Scenario 3: Quality Assessment
```bash
python benchmark.py \
  --test-file complex_document.pdf \
  --engines local markitdown mistral paddleocr docling marker
```

### Scenario 4: Cost Analysis
```bash
# Free engines
python benchmark.py --engines local markitdown paddleocr docling marker mineru

# Paid engines
python benchmark.py --engines mistral deepseekocr
```

## FAQ

### Why do some engines fail?
- Missing dependencies
- Unconfigured API keys
- Unsupported file format
- Insufficient resources

**Solutions**: Check report's "Failure Details", install dependencies, configure API keys.

### How to test only installed engines?
```bash
python benchmark.py --engines local markitdown
```

### Where are results saved?
Default: `benchmark_results/`. Customize with `--output-dir`.

### Performance ratings?
- ⭐⭐⭐⭐⭐ Excellent: < 5s
- ⭐⭐⭐⭐ Good: 5-15s
- ⭐⭐⭐ Average: 15-30s
- ⭐⭐ Slow: 30-60s
- ⭐ Very Slow: > 60s

### Can I test with my own documents?
```bash
python benchmark.py --test-file path/to/your/document.pdf
```
Supported: .pdf, .docx, .png, .jpg, .jpeg, .txt, .md

### Chinese document processing?
```bash
python benchmark.py \
  --test-file chinese_document.pdf \
  --engines deepseekocr paddleocr docling mistral
```

## Technical Details

### Test Metrics
- **Conversion Time**: Start to completion (seconds)
- **Markdown Length**: Character count in output
- **Asset Count**: Number of extracted images/resources
- **Success Rate**: Percentage of successful conversions

### Performance Optimization
- PaddleOCR: Use GPU (`use_gpu=True`)
- MinerU: Better with GPU
- Cloud engines: Adjust `*_TIMEOUT_SECONDS` and `*_RETRY_ATTEMPTS` in `.env`

## Contributing

Suggested improvements:
- More metrics (memory, CPU)
- Batch testing
- Visualization charts
- More output formats (HTML, Excel)

---

**More Information**:
- Main README: `README.md`
- Chinese Docs: `readme_cn/README_BENCHMARK_CN.md`
- Configuration: `.env.example`
- Code: `benchmark.py`
