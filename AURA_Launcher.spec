# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('ICON', 'ICON'),
    ('data', 'data'),
    ('core', 'core'),
    ('models', 'models'),
    ('routers', 'routers'),
    ('services', 'services'),
    ('main.py', '.'),
    ('requirements.txt', '.'),
    # LƯU Ý: KHÔNG đóng gói license.key nữa.
    # Key được quản lý REMOTE trên GitHub Private Repo (data/keys.json).
    # Token GitHub được obfuscate trong services/_embedded_token.py (sinh bởi build script).
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespans',
        'uvicorn.lifespans.on',
        'uvicorn.lifespans.off',
        'pydantic',
        'jinja2',
        'PIL',
        'groq',
        'requests',
        'dotenv',
        'multipart',
        'asyncio'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AURA_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ICON/LOGO_HAURA.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AURA_Launcher',
)
