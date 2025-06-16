#!/bin/bash

# DEB 패키지 생성 스크립트

PACKAGE_NAME="gc-writer"
VERSION="1.0.0"
MAINTAINER="GC Writer Team <support@gcwriter.com>"
DESCRIPTION="Voice-to-text converter using OpenAI Whisper"

# 패키지 디렉토리 구조 생성
DEB_DIR="dist/deb-package"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/local/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/48x48/apps"

# DEBIAN/control 파일 생성
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: libc6, libxcb-cursor0
Maintainer: $MAINTAINER
Description: $DESCRIPTION
 A cross-platform voice-to-text application that runs in the system tray
 and converts speech to text using OpenAI Whisper when Ctrl+Alt+Space is pressed.
EOF

# 실행 파일 복사
cp -r "dist/gc-writer"/* "$DEB_DIR/usr/local/bin/"

# 데스크톱 파일 생성
cat > "$DEB_DIR/usr/share/applications/gc-writer.desktop" << EOF
[Desktop Entry]
Name=GC Writer
Comment=Voice-to-text converter
Exec=/usr/local/bin/gc-writer
Icon=gc-writer
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOF

# 아이콘 복사 (있는 경우)
if [ -f "assets/icons/app.png" ]; then
    cp "assets/icons/app.png" "$DEB_DIR/usr/share/icons/hicolor/48x48/apps/gc-writer.png"
fi

# postinst 스크립트 생성 (권한 설정)
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
chmod +x /usr/local/bin/gc-writer
update-desktop-database
gtk-update-icon-cache -f -t /usr/share/icons/hicolor
EOF

chmod +x "$DEB_DIR/DEBIAN/postinst"

# DEB 패키지 빌드
dpkg-deb --build "$DEB_DIR" "dist/${PACKAGE_NAME}_${VERSION}_amd64.deb"

if [ -f "dist/${PACKAGE_NAME}_${VERSION}_amd64.deb" ]; then
    echo "DEB package created successfully: dist/${PACKAGE_NAME}_${VERSION}_amd64.deb"
else
    echo "Failed to create DEB package"
    exit 1
fi