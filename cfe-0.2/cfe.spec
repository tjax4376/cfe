# PyInstaller spec for CFE interpreter standalone executable.
# Build: from cfe-0.2/ run: pyinstaller cfe.spec   (or use build_standalone.sh from repo root)
# Output: dist/cfe (Unix) or dist/cfe.exe (Windows)

import os
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    [os.path.join(spec_dir, 'cfe_run.py')],
    pathex=[spec_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cfe',
        'cfe.lexer',
        'cfe.parser',
        'cfe.typesystem',
        'cfe.interpreter',
        'cfe.cfe_gui',
        'cfe.agent',
        'cfe.agent.gateway',
        'cfe.agent.config',
        'cfe.agent.message',
        'cfe.agent.session',
        'cfe.agent.adapters',
        'cfe.agent.adapters.base',
        'cfe.agent.adapters.openai_adapter',
        'cfe.agent.adapters.anthropic_adapter',
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
    name='cfe',
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
