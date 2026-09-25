#!/usr/bin/env bash
# Khởi chạy AURA AI Launcher trên Linux
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

if [ -f ".venv/bin/python" ]; then
    .venv/bin/python launcher.py
else
    python3 launcher.py
fi
