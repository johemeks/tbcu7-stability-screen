#!/usr/bin/env bash
# Rebuild every output from the raw snapshot (no internet needed).
set -e
cd "$(dirname "$0")/code"
python3 02_build.py
python3 03_proxy.py
python3 04_validate.py
python3 05_figures.py "$@"
python3 06_document.py "$@"
