# PyInstaller spec for CFD interpreter standalone executable.
# Build: from cfd/ run: pyinstaller cfd.spec   (or use build_standalone.sh from repo root)
# Output: dist/cfd (Unix) or dist/cfd.exe (Windows)

import os
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
parent_dir = os.path.dirname(spec_dir)

a = Analysis(
    [os.path.join(spec_dir, 'cfd.py')],
    pathex=[parent_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cfd',
        'cfd.lexer',
        'cfd.parser',
        'cfd.typesystem',
        'cfd.interpreter',
        'cfd.cfd_gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cfd',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
