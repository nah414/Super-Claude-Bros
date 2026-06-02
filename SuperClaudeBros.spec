# -*- mode: python ; coding: utf-8 -*-
# Build recipe for the standalone game. Run from the project root:
#     python -m PyInstaller SuperClaudeBros.spec --noconfirm
# Produces a single self-contained file: dist/SuperClaudeBros.exe
# Paths are relative so this works from a fresh clone on any machine.

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('levels', 'levels'), ('music', 'music')],   # bundle level + music data
    hiddenimports=[],
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
    name='SuperClaudeBros',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # windowed app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['tools/claude.ico'],
)
