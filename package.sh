#!/bin/bash
set -e

PACKAGE_DIR="pacman-package"

rm -rf build dist __pycache__ Pac-Man.spec "$PACKAGE_DIR" "${PACKAGE_DIR}.zip"
mkdir -p "$PACKAGE_DIR/src"

cp -r src/assets src/jsons "$PACKAGE_DIR/src/"
cp src/jsons/config.json "$PACKAGE_DIR/"
cp INSTRUCTIONS.txt README.md "$PACKAGE_DIR/"

uv run pyinstaller \
    --onefile \
    --windowed \
    --name "Pac-Man" \
    --add-data "src/assets:src/assets" \
    --add-data "src/jsons:src/jsons" \
    --clean \
    pac-man.py

cp dist/Pac-Man "$PACKAGE_DIR/"
zip -r "${PACKAGE_DIR}.zip" "$PACKAGE_DIR"

rm -rf build dist __pycache__ Pac-Man.spec "$PACKAGE_DIR"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true