# doc-to-markdown-converter

Proof-of-concept CLI that ingests docs, routes them through pluggable engines (Mistral, SiliconFlow/DeepSeek-OCR, local), and emits Markdown.

## Usage

1. `cp .env.example .env` and populate API keys.
2. `pip install -r requirements.txt`
3. `python -m doc_to_md.cli convert --input data/input --output data/output`

