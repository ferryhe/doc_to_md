# 引擎对比测试工具使用指南

## 简介

这是一个用于测试和对比不同文档转换引擎性能的工具。它可以自动测试多个引擎，并生成详细的中文对比报告。

## 功能特点

- ✅ **自动化测试** - 一键测试多个引擎
- 📊 **性能指标** - 转换时间、成功率、输出特征（Markdown长度和资源数等粗略质量代理指标）
- 📝 **中文报告** - 生成详细的中文对比分析报告
- 🎯 **引擎分析** - 每个引擎的优缺点和适用场景
- 🔧 **灵活配置** - 自定义测试文件和引擎选择

## 快速开始

### 基本用法

```bash
# 测试所有可用引擎
python benchmark.py

# 测试特定引擎
python benchmark.py --engines local markitdown

# 使用自定义测试文件
python benchmark.py --test-file path/to/your/document.pdf

# 保存JSON格式结果
python benchmark.py --save-json
```

### 高级用法

```bash
# 测试多个引擎并保存到指定目录
python benchmark.py \
  --engines local markitdown paddleocr docling \
  --output-dir my_test_results \
  --save-json

# 使用PDF文件测试OCR引擎
python benchmark.py \
  --test-file document.pdf \
  --engines mistral deepseekocr paddleocr

# 测试所有本地引擎（不需要API密钥）
python benchmark.py \
  --engines local markitdown paddleocr docling marker mineru
```

## 支持的引擎

### 本地引擎（无需API密钥）

1. **local** - 基础文本提取引擎
   - 优点：快速、无需依赖、适合纯文本
   - 缺点：OCR能力有限

2. **markitdown** - Microsoft MarkItDown引擎
   - 优点：支持Office格式、本地处理、保真度高
   - 缺点：需要安装依赖包
   - 安装：`pip install markitdown`

3. **paddleocr** - PaddleOCR引擎
   - 优点：本地OCR、支持多语言、可GPU加速
   - 缺点：需要下载模型
   - 安装：`pip install ".[paddleocr]"`

4. **docling** - IBM Docling引擎
   - 优点：企业级方案、结构化提取
   - 缺点：依赖较重
   - 安装：`pip install ".[docling]"`

5. **marker** - Marker PDF引擎
   - 优点：专注PDF、保留格式
   - 缺点：需要较多依赖
   - 安装：`pip install ".[marker]"`

6. **mineru** - MinerU引擎
   - 优点：多种解析方法、GPU加速
   - 缺点：资源消耗大
   - 安装：`pip install ".[mineru]"`

### 云端引擎（需要API密钥）

7. **mistral** - Mistral OCR API
   - 优点：强大的OCR能力、高质量输出
   - 缺点：需要API密钥和网络
   - 配置：在`.env`文件中设置`MISTRAL_API_KEY`

8. **deepseekocr** - DeepSeek OCR API
   - 优点：优秀的中文OCR、视觉理解能力强
   - 缺点：需要API密钥和网络
   - 配置：在`.env`文件中设置`SILICONFLOW_API_KEY`

## 报告内容

生成的中文对比报告包含以下内容：

### 1. 测试信息
- 测试时间
- 测试文件信息
- 文件大小
- 测试引擎数量

### 2. 整体统计
- 成功/失败引擎数量
- 成功率百分比

### 3. 性能排名
- 按转换时间排序
- 输出长度对比
- 资源数量统计

### 4. 详细测试结果表格
包含每个引擎的：
- 状态（成功/失败）
- 转换时间
- Markdown输出长度
- 资源数量
- 性能评级（⭐评分）

### 5. 引擎特点分析
每个引擎的详细分析，包括：
- 优点列表
- 缺点列表
- 最适合的使用场景

### 6. 使用建议
- 速度优先推荐
- 质量优先推荐
- 成本考虑（免费/付费）
- 按文档类型的建议

### 7. 失败详情
- 失败引擎的错误信息
- 故障诊断建议

## 示例报告

运行基准测试后，会生成类似以下的报告：

```markdown
# 文档转换引擎对比测试报告

## 测试信息
- **测试时间**: 2026-02-07T12:37:44.895027
- **测试文件**: `sample_test.txt`
- **文件大小**: 922 B
- **测试引擎数量**: 8

## 整体统计
- **成功**: 5 个引擎
- **失败**: 3 个引擎
- **成功率**: 62.5%

## 性能排名（按转换时间）
1. **local** (local-text-wrapper)
   - 转换时间: < 0.01秒
   - 输出长度: 724 字符
   - 资源数量: 0

2. **markitdown** (markitdown-default)
   - 转换时间: 0.52秒
   - 输出长度: 1,245 字符
   - 资源数量: 0

...
```

## 输出文件

运行基准测试后，会在输出目录（默认为`benchmark_results/`）生成以下文件：

1. **comparison_report_YYYYMMDD_HHMMSS.md** - 中文对比报告（Markdown格式）
2. **benchmark_result_YYYYMMDD_HHMMSS.json** - 原始测试数据（JSON格式，使用`--save-json`时生成）
3. **sample_test.txt** - 示例测试文件（如果未提供自定义测试文件）

## 使用场景

### 场景1：选择合适的引擎

如果你不确定应该使用哪个引擎，可以运行完整的基准测试：

```bash
python benchmark.py --test-file your_document.pdf --save-json
```

根据报告中的性能排名和特点分析，选择最适合你需求的引擎。

### 场景2：性能验证

在生产环境部署前，验证引擎性能：

```bash
python benchmark.py \
  --test-file production_sample.pdf \
  --engines mistral deepseekocr \
  --output-dir validation_results
```

### 场景3：质量评估

对比不同引擎的输出质量：

```bash
python benchmark.py \
  --test-file complex_document.pdf \
  --engines local markitdown mistral paddleocr docling marker
```

查看报告中的"Markdown长度"和"资源数量"，输出越详细通常质量越高。

### 场景4：成本分析

评估免费引擎和付费引擎的性能差异：

```bash
# 测试免费引擎
python benchmark.py --engines local markitdown paddleocr docling marker mineru

# 测试付费引擎
python benchmark.py --engines mistral deepseekocr
```

## 常见问题

### Q: 为什么某些引擎测试失败？

**A:** 可能的原因：
- 缺少必要的依赖包（如markitdown、paddleocr等）
- 未配置API密钥（对于mistral、deepseekocr）
- 测试文件格式不支持
- 系统资源不足（特别是GPU相关的引擎）

**解决方法**：
1. 查看报告中的"失败详情"部分
2. 安装缺失的依赖：`pip install markitdown` 或 `pip install ".[markitdown]"`
3. 配置API密钥：编辑`.env`文件
4. 确认测试文件格式正确

### Q: 如何只测试已安装的引擎？

**A:** 使用`--engines`参数明确指定要测试的引擎：

```bash
python benchmark.py --engines local markitdown
```

### Q: 测试结果保存在哪里？

**A:** 默认保存在`benchmark_results/`目录。可以使用`--output-dir`参数自定义：

```bash
python benchmark.py --output-dir my_results
```

### Q: 如何解读性能评级？

**A:** 性能评级基于转换时间：
- ⭐⭐⭐⭐⭐ 优秀：< 5秒
- ⭐⭐⭐⭐ 良好：5-15秒
- ⭐⭐⭐ 一般：15-30秒
- ⭐⭐ 较慢：30-60秒
- ⭐ 缓慢：> 60秒

### Q: 可以用自己的文档测试吗？

**A:** 当然可以！使用`--test-file`参数：

```bash
python benchmark.py --test-file path/to/your/document.pdf
```

支持的格式：.pdf, .docx, .png, .jpg, .jpeg, .txt, .md

### Q: 如何对比中文文档的处理能力？

**A:** 使用包含中文内容的测试文件，特别推荐测试这些引擎：

```bash
python benchmark.py \
  --test-file chinese_document.pdf \
  --engines deepseekocr paddleocr docling mistral
```

DeepSeek OCR 和 PaddleOCR 对中文支持较好。

## 技术细节

### 测试指标

1. **转换时间** (Conversion Time)
   - 从开始转换到完成的总时间
   - 不包括引擎初始化时间
   - 单位：秒

2. **Markdown长度** (Markdown Length)
   - 输出Markdown文本的字符数
   - 通常越长表示提取的内容越详细
   - 单位：字符

3. **资源数量** (Asset Count)
   - 提取的图像和其他资源文件数量
   - 包括OCR过程中提取的图片
   - 单位：个

4. **成功率** (Success Rate)
   - 成功转换的引擎数量占总测试引擎数的百分比
   - 单位：百分比

### 性能优化建议

1. **本地引擎**：
   - PaddleOCR可以使用GPU加速：设置环境变量`use_gpu=True`
   - MinerU在GPU环境下性能更好
   - Marker可以启用并行处理

2. **云端引擎**：
   - 调整超时设置：在`.env`中设置`*_TIMEOUT_SECONDS`
   - 调整重试次数：设置`*_RETRY_ATTEMPTS`
   - 大文档可能需要分块处理

3. **测试建议**：
   - 首次测试使用小文件（< 1MB）
   - 逐步增加文档复杂度
   - 监控系统资源使用情况

## 贡献

如果你想为基准测试工具添加新功能或改进，欢迎提交Pull Request！

建议的改进方向：
- 添加更多性能指标（内存使用、CPU占用等）
- 支持批量文档测试
- 添加可视化图表
- 支持更多输出格式（HTML、Excel等）

## 许可

本工具遵循项目的整体许可协议。

---

**更多信息**：
- 查看主README文件：`README.md`
- 查看英文文档：`README_BENCHMARK.md`
- 查看引擎配置：`.env.example`
- 查看代码实现：`benchmark.py`
