# Multi-stage Dockerfile for RepoChat Backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development tools
RUN pip install --no-cache-dir debugpy ipdb

# Copy source code
COPY . .

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/temp

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Expose ports
EXPOSE 8000 5678

# Command for development (with debugger support)
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash repochat
RUN chown -R repochat:repochat /app

# Switch to non-root user
USER repochat

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/temp

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "from src.orchestrator.orchestrator_agent import OrchestratorAgent; print('Backend healthy')" || exit 1

# Command for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 