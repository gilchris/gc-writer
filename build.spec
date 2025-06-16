# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

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
        'librosa',
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
    name='gc-writer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 모드로 실행
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app.ico',  # Windows용 아이콘
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gc-writer',
)

# macOS용 앱 번들 생성
app = BUNDLE(
    coll,
    name='gc-writer.app',
    icon='assets/icons/app.icns',  # macOS용 아이콘
    bundle_identifier='com.gcwriter.speechtotext',
    info_plist={
        'NSMicrophoneUsageDescription': 'This app needs microphone access for speech-to-text conversion.',
        'NSAccessibilityUsageDescription': 'This app needs accessibility access for global hotkeys.',
    },
)