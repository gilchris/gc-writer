@echo off
echo Building gc-writer for Windows...

REM 가상환경 활성화 (선택사항)
REM call venv\Scripts\activate.bat

REM 기존 빌드 파일 정리
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

REM PyInstaller로 빌드
pyinstaller build.spec

REM 빌드 완료 확인
if exist "dist\gc-writer\gc-writer.exe" (
    echo Build successful! Executable created at dist\gc-writer\gc-writer.exe
) else (
    echo Build failed!
    exit /b 1
)

REM NSIS 설치 프로그램 생성 (NSIS가 설치된 경우)
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo Creating Windows installer...
    "C:\Program Files (x86)\NSIS\makensis.exe" installer_windows.nsi
) else (
    echo NSIS not found. Skipping installer creation.
)

echo Build process completed.
pause