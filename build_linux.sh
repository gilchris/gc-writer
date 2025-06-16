#!/bin/bash

echo "Building gc-writer for Linux..."

# 가상환경 활성화 (선택사항)
# source venv/bin/activate

# 기존 빌드 파일 정리
rm -rf dist build

# PyInstaller로 빌드
pyinstaller build.spec

# 빌드 완료 확인
if [ -f "dist/gc-writer/gc-writer" ]; then
    echo "Build successful! Executable created at dist/gc-writer/gc-writer"
    
    # 실행 권한 부여
    chmod +x dist/gc-writer/gc-writer
    
    # DEB 패키지 생성 (dpkg-deb가 있는 경우)
    if command -v dpkg-deb &> /dev/null; then
        echo "Creating DEB package..."
        ./create_deb.sh
    else
        echo "dpkg-deb not found. Skipping DEB package creation."
    fi
    
    # AppImage 생성 (appimagetool이 있는 경우)
    if command -v appimagetool &> /dev/null; then
        echo "Creating AppImage..."
        ./create_appimage.sh
    else
        echo "appimagetool not found. Skipping AppImage creation."
    fi
    
else
    echo "Build failed!"
    exit 1
fi

echo "Build process completed."