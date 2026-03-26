#!/usr/bin/env bash
set -euo pipefail

echo "=== Project Setup ==="

# Git init if needed
if [ ! -d .git ]; then
    echo "[1/5] Initializing git..."
    git init
    git add -A
    git commit -m "feat: initial project setup"
else
    echo "[1/5] Git already initialized, skipping."
fi

# Install Python deps
echo "[2/5] Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Pre-commit
echo "[3/5] Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
else
    echo "  pre-commit not found, install with: pip install pre-commit"
fi

# Docker services
echo "[4/5] Starting Docker services..."
if command -v docker &> /dev/null; then
    docker compose up -d postgres redis
    echo "  Waiting for services to be healthy..."
    sleep 5
else
    echo "  Docker not found, skipping."
fi

# Tests
echo "[5/5] Running tests..."
pytest tests/ -v --tb=short || echo "  Some tests failed (expected on first run without DB)."

echo ""
echo "=== Setup complete! ==="
echo "  Start dev server: uvicorn src.main:app --reload"
echo "  Run tests:        pytest tests/ -v"
echo "  Docker dev:       docker compose -f docker-compose.yml -f docker-compose.dev.yml up"
