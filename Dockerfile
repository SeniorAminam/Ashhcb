# Project: Ashhcb Bot - Image to Trend Transform
# File Path: Dockerfile
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-23
# Version: 2.0.0
# Purpose: Docker image for Ashhcb Bot
# License: MIT
# Copyright: (c) Amin Davodian

# ========================
# Builder Stage
# ========================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================
# Production Stage
# ========================
FROM python:3.11-slim

WORKDIR /app

# Install runtime deps (for Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libwebp7 libjpeg62-turbo libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with data/logs dirs
RUN addgroup --system --gid 1001 appuser \
    && adduser --system --uid 1001 appuser \
    && mkdir -p /app/data /app/logs \
    && chown -R appuser:appuser /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Copy application files
COPY src/ ./src/
COPY .env.example ./.env.example
COPY requirements.txt .

# Labels
LABEL maintainer="Amin Davodian" \
      org.opencontainers.image.authors="Amin Davodian" \
      org.opencontainers.image.url="https://senioramin.com" \
      org.opencontainers.image.source="https://github.com/SeniorAminam/Ashhcb" \
      org.opencontainers.image.title="Ashhcb Bot" \
      org.opencontainers.image.description="Bale bot for AI image transformation (Agnes AI)" \
      org.opencontainers.image.version="2.0.0"

# Switch to non-root user
USER appuser

# Health check — try importing the bot package
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "from src.config.settings import BOT_TOKEN; exit(0 if BOT_TOKEN else 1)"

# Run the bot
CMD ["python", "-m", "src.bot"]
