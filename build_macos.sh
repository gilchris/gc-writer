#!/bin/bash

echo "Building gc-writer for macOS..."

# 가상환경 활성화 (선택사항)
# source venv/bin/activate

# 기존 빌드 파일 정리
rm -rf dist build

# PyInstaller로 빌드
pyinstaller build.spec

# 빌드 완료 확인
if [ -d "dist/gc-writer.app" ]; then
    echo "Build successful! App bundle created at dist/gc-writer.app"
    
    # 코드 서명 (개발자 계정이 있는 경우)
    if [ ! -z "$CODESIGN_IDENTITY" ]; then
        echo "Code signing the app..."
        codesign --deep --force --verify --verbose --sign "$CODESIGN_IDENTITY" dist/gc-writer.app
    else
        echo "No code signing identity set. Skipping code signing."
    fi
    
    # DMG 생성
    if command -v create-dmg &> /dev/null; then
        echo "Creating DMG..."
        create-dmg \
            --volname "gc-writer" \
            --volicon "assets/icons/app.icns" \
            --window-pos 200 120 \
            --window-size 600 300 \
            --icon-size 100 \
            --icon "gc-writer.app" 175 120 \
            --hide-extension "gc-writer.app" \
            --app-drop-link 425 120 \
            "dist/gc-writer.dmg" \
            "dist/"
    else
        echo "create-dmg not found. Skipping DMG creation."
        echo "You can install it with: brew install create-dmg"
    fi
    
else
    echo "Build failed!"
    exit 1
fi

echo "Build process completed."