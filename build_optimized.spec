# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 최적화된 excludes 리스트
excludes = [
    'test',
    'tests',
    'testing',
    'unittest',
    'doctest',
    'tkinter',
    'matplotlib',
    'PIL',
    'IPython',
    'jupyter',
    'notebook',
    'scipy',
    'pandas',
    'sklearn',
    'tensorflow',
    'tensorboard',
    'cv2',
    'sqlite3',
    '_sqlite3',
    'bz2',
    '_bz2',
    'lzma',
    '_lzma',
    'pydoc',
    'setuptools._vendor',
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icons', 'assets/icons'),
        ('config/settings.json', 'config'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'pynput',
        'whisper',
        'pyperclip',
        'sounddevice',
        'numpy',
        'torch',
        'torchaudio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 불필요한 파일 제거
a.datas = [x for x in a.datas if not any(exclude in x[0].lower() for exclude in ['test', 'example', 'doc', 'readme'])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gc-writer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 디버그 심볼 제거
    upx=True,    # UPX 압축 사용
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,   # 디버그 심볼 제거
    upx=True,     # UPX 압축 사용
    upx_exclude=[],
    name='gc-writer-optimized',
)