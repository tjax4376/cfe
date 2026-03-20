#!/usr/bin/env bash
# Build standalone CFE executable with PyInstaller.
# Requires: pip install pyinstaller
# Run from repo root: ./cfe-0.2/build_standalone.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pyinstaller &>/dev/null; then
  echo "PyInstaller not found. Install with: pip install pyinstaller" >&2
  exit 1
fi

cd "$SCRIPT_DIR"
pyinstaller --clean --noconfirm cfe.spec

echo "Done. Executable: $SCRIPT_DIR/dist/cfe (or dist/cfe.exe on Windows)"
