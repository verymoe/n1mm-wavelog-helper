# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['log_helper.py'],
    pathex=[],
    binaries=[('C:\\Users\\shiro\\anaconda3\\Library\\bin\\libssl-3-x64.dll', '.'), ('C:\\Users\\shiro\\anaconda3\\Library\\bin\\libcrypto-3-x64.dll', '.'), ('C:\\Users\\shiro\\anaconda3\\Library\\bin\\libmpdec-4.dll', '.')],
    datas=[('config.json', '.')],
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
    name='n1mm-wavelog-helper',
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
