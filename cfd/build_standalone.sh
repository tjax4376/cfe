#!/usr/bin/env bash
# Build standalone CFD executable with PyInstaller.
# Requires: pip install pyinstaller
# Run from repo root: ./cfd/build_standalone.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pyinstaller &>/dev/null; then
  echo "PyInstaller not found. Install with: pip install pyinstaller" >&2
  exit 1
fi

# Run from cfd/ so cfd.py and cfd_gui.py are in the same directory (spec uses pathex=['.'])
cd "$SCRIPT_DIR"
pyinstaller --clean --noconfirm cfd.spec

echo "Done. Executable: $SCRIPT_DIR/dist/cfd (or dist/cfd.exe on Windows)"
