#!/usr/bin/env bash
set -e

echo "=== Packaging Pac-man Project ==="
OUTPUT_DIR="dist"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Package source files into a distribution tarball
tar -czf "$OUTPUT_DIR/pacman-package.tar.gz" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='.mypy_cache' \
    --exclude='dist' \
    .

echo "Package created successfully at: $OUTPUT_DIR/pacman-package.tar.gz"
