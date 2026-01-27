# Deployment Guide

This guide covers containerized deployment using Docker and Docker Compose.

## Prerequisites

- Docker 20.10 or later
- Docker Compose 2.0 or later (optional, for orchestration)
- At least 2GB of available RAM
- At least 5GB of disk space

## Quick Start with Docker

### 1. Build the Docker Image

```bash
docker build -t doc-to-md:latest .
```

### 2. Run a Simple Conversion

```bash
# Create data directories
mkdir -p data/input data/output

# Place your documents in data/input/

# Run conversion with local engine
docker run --rm \
  -v $(pwd)/data:/app/data \
  doc-to-md:latest \
  doc-to-md convert \
  --input-path /app/data/input \
  --output-path /app/data/output \
  --engine local
```

### 3. Using Remote Engines (Mistral, DeepSeek)

```bash
# With environment variables
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e MISTRAL_API_KEY="your-api-key-here" \
  doc-to-md:latest \
  doc-to-md convert \
  --input-path /app/data/input \
  --output-path /app/data/output \
  --engine mistral
```

## Using Docker Compose (Recommended)

Docker Compose simplifies multi-container deployments and environment management.

### 1. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (optional, only needed for remote engines)
MISTRAL_API_KEY=your-mistral-key
SILICONFLOW_API_KEY=your-siliconflow-key

# Default engine (local, mistral, deepseekocr, etc.)
DEFAULT_ENGINE=local

# Timeouts and limits
MISTRAL_TIMEOUT_SECONDS=120
SILICONFLOW_TIMEOUT_SECONDS=120
```

### 2. Run with Docker Compose

```bash
# Start the default local engine service
docker-compose up doc-to-md

# Run with Mistral OCR (requires API key)
docker-compose --profile mistral up doc-to-md-mistral

# Run with DeepSeek OCR (requires API key)
docker-compose --profile deepseek up doc-to-md-deepseek
```

### 3. One-Time Conversions

```bash
# Run a single conversion and stop
docker-compose run --rm doc-to-md \
  doc-to-md convert \
  --input-path /app/data/input \
  --output-path /app/data/output \
  --engine local
```

## Production Deployment Considerations

### Resource Limits

Add resource limits to your docker-compose.yml:

```yaml
services:
  doc-to-md:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Persistent Storage

For production, use named volumes or bind mounts:

```yaml
volumes:
  input_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/persistent/input
  output_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/persistent/output
```

### Health Checks

The Dockerfile includes a basic health check. Monitor container health:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' doc-to-md-converter

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' doc-to-md-converter
```

### Logging

Configure logging drivers in docker-compose.yml:

```yaml
services:
  doc-to-md:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

View logs:

```bash
# Follow logs
docker-compose logs -f doc-to-md

# View last 100 lines
docker-compose logs --tail=100 doc-to-md
```

### Security Best Practices

1. **API Keys**: Never commit API keys. Use environment variables or secrets management.

2. **File Permissions**: Ensure proper file permissions on mounted volumes.

3. **Network Security**: If exposing services, use proper network isolation:

```yaml
networks:
  doc-to-md-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

4. **Read-Only Filesystem**: Consider making the container filesystem read-only:

```yaml
services:
  doc-to-md:
    read_only: true
    tmpfs:
      - /tmp
```

## Kubernetes Deployment

For Kubernetes deployments, create a ConfigMap and Secret:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: doc-to-md-config
data:
  DEFAULT_ENGINE: "local"
---
apiVersion: v1
kind: Secret
metadata:
  name: doc-to-md-secrets
type: Opaque
stringData:
  MISTRAL_API_KEY: "your-key-here"
  SILICONFLOW_API_KEY: "your-key-here"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: doc-to-md
spec:
  replicas: 1
  selector:
    matchLabels:
      app: doc-to-md
  template:
    metadata:
      labels:
        app: doc-to-md
    spec:
      containers:
      - name: doc-to-md
        image: doc-to-md:latest
        envFrom:
        - configMapRef:
            name: doc-to-md-config
        - secretRef:
            name: doc-to-md-secrets
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m"
          requests:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: doc-to-md-pvc
```

## Monitoring

### Prometheus Metrics

To add Prometheus metrics, extend the application with a metrics endpoint.

### Log Aggregation

Send logs to a centralized logging system:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  --log-driver=syslog \
  --log-opt syslog-address=tcp://logserver:514 \
  doc-to-md:latest
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs doc-to-md-converter

# Inspect container
docker inspect doc-to-md-converter
```

### Out of Memory Errors

Increase Docker memory limits:

```bash
# Check current memory limit
docker stats doc-to-md-converter

# Increase in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

### File Permission Issues

```bash
# Run with user permissions
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd)/data:/app/data \
  doc-to-md:latest
```

## Scaling

For processing large volumes of documents:

1. **Horizontal Scaling**: Run multiple containers with a shared input queue
2. **Batch Processing**: Use `--since` flag to process only new files
3. **Engine Selection**: Use faster engines (local) for simple documents, advanced engines (Mistral, DeepSeek) for complex ones

## Backup and Recovery

```bash
# Backup output data
docker run --rm \
  -v doc-to-md-output:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/output-$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm \
  -v doc-to-md-output:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/output-20250127.tar.gz -C /
```
