#!/usr/bin/env bash
set -e

echo "=== Packaging Pac-man Project ==="
OUTPUT_DIR="package"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"


# Package source files into a distribution zip archive
zip -r "$OUTPUT_DIR/pacman-package.zip" . \
    -x '.venv/*' \
    -x '__pycache__/*' \
    -x '.git/*' \
    -x '.mypy_cache/*' \
    -x 'dist/*'

echo "Package created successfully at: $OUTPUT_DIR/pacman-package.zip"
