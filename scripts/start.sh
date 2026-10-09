#!/bin/bash
cd "$(dirname "$0")/.."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
python3 run.py
