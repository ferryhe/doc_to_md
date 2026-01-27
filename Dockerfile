# Multi-stage Dockerfile for doc-to-markdown-converter
# Stage 1: Base image with Python and system dependencies
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libreoffice \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy only dependency files first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY config/ ./config/
COPY src/ ./src/
COPY tests/ ./tests/
COPY README.md ./

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p /app/data/input /app/data/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEFAULT_ENGINE=local

# Expose volume for input/output data
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import doc_to_md; print('OK')" || exit 1

# Default command - list engines
CMD ["doc-to-md", "list-engines"]
