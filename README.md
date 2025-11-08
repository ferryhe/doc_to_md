# doc-to-markdown-converter

Proof-of-concept CLI that ingests docs, routes them through pluggable engines (Mistral, SiliconFlow/DeepSeek-OCR, local), and emits Markdown.

## Usage

1. `cp .env.example .env` and populate API keys. You can also set `DEFAULT_ENGINE`, `MISTRAL_DEFAULT_MODEL`, or `SILICONFLOW_DEFAULT_MODEL` here to change the default engine/model without editing code.
2. `pip install -r requirements.txt`
3. `python -m doc_to_md.cli convert --input data/input --output data/output`

