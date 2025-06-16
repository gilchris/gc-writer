> [!CAUTION]
> !!! 주의! 이 내용은 Claude Code가 자동으로 생성한 내용 **그대로**입니다. 이상한 내용이 있을 수 있습니다 !!!

# 🚀 설치 가이드

## 📖 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [사전 준비](#사전-준비)
3. [설치 방법](#설치-방법)
4. [초기 설정](#초기-설정)
5. [설치 확인](#설치-확인)
6. [문제 해결](#문제-해결)
7. [제거 방법](#제거-방법)

---

## 💻 시스템 요구사항

### 최소 요구사항
| 구분 | Windows | macOS | Linux |
|------|---------|--------|-------|
| **OS 버전** | Windows 10 (1903+) | macOS 10.14+ | Ubuntu 18.04+ |
| **메모리** | 2GB RAM | 2GB RAM | 2GB RAM |
| **저장공간** | 500MB | 500MB | 500MB |
| **Python** | 3.8+ (소스 설치시) | 3.8+ (소스 설치시) | 3.8+ (소스 설치시) |

### 권장 요구사항
| 구분 | Windows | macOS | Linux |
|------|---------|--------|-------|
| **OS 버전** | Windows 11 | macOS 12+ | Ubuntu 20.04+ |
| **메모리** | 8GB RAM | 8GB RAM | 8GB RAM |
| **저장공간** | 2GB | 2GB | 2GB |
| **프로세서** | Intel i5 또는 동급 | Intel i5 또는 Apple M1+ | Intel i5 또는 동급 |

### 필수 하드웨어
- **마이크**: 내장 또는 외장 마이크 (노이즈 캔슬링 권장)
- **오디오 드라이버**: ASIO 호환 오디오 드라이버 권장

---

## 🛠️ 사전 준비

### Windows 사용자

#### 1. Microsoft Visual C++ 재배포 가능 패키지
```powershell
# PowerShell (관리자 권한)에서 실행
# 또는 Microsoft 홈페이지에서 직접 다운로드
winget install Microsoft.VCRedist.2015+.x64
```

#### 2. Windows Media Feature Pack (N/KN 에디션)
Windows N 또는 KN 에디션 사용자는 추가 설치 필요:
1. 설정 > 앱 > 선택적 기능 > 기능 추가
2. "미디어 기능 팩" 검색 후 설치

### macOS 사용자

#### 1. Xcode Command Line Tools
```bash
xcode-select --install
```

#### 2. Homebrew (Python 소스 설치시)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux 사용자

#### 1. 시스템 패키지 업데이트
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL/Fedora
sudo dnf update -y
# 또는 (구버전)
sudo yum update -y
```

#### 2. 필수 패키지 설치
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv \
                    python3-dev build-essential \
                    portaudio19-dev libasound2-dev \
                    libpulse-dev libx11-dev \
                    libxtst6 libxss1 libgconf-2-4

# CentOS/RHEL/Fedora
sudo dnf install -y python3 python3-pip python3-devel \
                     gcc gcc-c++ make \
                     portaudio-devel alsa-lib-devel \
                     pulseaudio-libs-devel \
                     libX11-devel libXtst-devel
```

---

## 📦 설치 방법

### 방법 1: 독립 실행파일 (권장) 🌟

가장 간단한 설치 방법으로, Python 설치 없이 바로 사용할 수 있습니다.

#### Windows
1. **다운로드**
   - [릴리스 페이지](https://github.com/your-repo/speech-to-text/releases)에서 최신 `SpeechToText-Windows-x64.zip` 다운로드

2. **압축 해제**
   ```cmd
   # 원하는 위치에 압축 해제 (예: C:\Program Files\SpeechToText)
   ```

3. **실행**
   ```cmd
   # speech-to-text.exe 더블클릭 또는 명령어로 실행
   .\speech-to-text.exe
   ```

#### macOS
1. **다운로드**
   - [릴리스 페이지](https://github.com/your-repo/speech-to-text/releases)에서 최신 `SpeechToText-macOS.dmg` 다운로드

2. **설치**
   ```bash
   # DMG 파일 마운트
   open SpeechToText-macOS.dmg
   
   # Applications 폴더로 드래그
   # 또는 터미널에서:
   cp -R "/Volumes/Speech to Text/Speech to Text.app" /Applications/
   ```

3. **권한 설정** (필수)
   - 시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호
   - "접근성"에서 Speech to Text 앱 권한 허용
   - "마이크"에서 Speech to Text 앱 권한 허용

#### Linux
1. **다운로드**
   ```bash
   # 최신 릴리스 다운로드
   wget https://github.com/your-repo/speech-to-text/releases/latest/download/SpeechToText-Linux-x64.tar.gz
   ```

2. **설치**
   ```bash
   # 압축 해제
   tar -xzf SpeechToText-Linux-x64.tar.gz
   
   # 설치 디렉토리로 이동
   sudo mv speech-to-text /opt/
   
   # 실행 권한 부여
   sudo chmod +x /opt/speech-to-text/speech-to-text
   
   # 심볼릭 링크 생성 (선택사항)
   sudo ln -s /opt/speech-to-text/speech-to-text /usr/local/bin/speech-to-text
   ```

### 방법 2: Python 소스코드 설치

개발자이거나 소스코드를 수정하고 싶은 경우 사용합니다.

#### 1. 저장소 클론
```bash
git clone https://github.com/your-repo/speech-to-text.git
cd speech-to-text
```

#### 2. 가상환경 생성 (권장)
```bash
# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. 의존성 설치
```bash
# 기본 설치
pip install -r requirements.txt

# 개발자 도구 포함 설치
pip install -r requirements-dev.txt
```

#### 4. 실행
```bash
cd src
python main.py
```

### 방법 3: PyPI 패키지 설치 (예정)

```bash
# PyPI에서 설치 (향후 제공 예정)
pip install speech-to-text-app
speech-to-text
```

---

## ⚙️ 초기 설정

### 1. 첫 실행 시 설정

프로그램을 처음 실행하면 자동으로 기본 설정이 생성됩니다.

#### 설정 파일 위치
- **Windows**: `%APPDATA%\speech-to-text\settings.json`
- **macOS**: `~/Library/Application Support/speech-to-text/settings.json`
- **Linux**: `~/.config/speech-to-text/settings.json`

### 2. 마이크 설정

#### 자동 마이크 감지
프로그램이 자동으로 최적의 마이크를 선택합니다. 수동으로 변경하려면:

```json
{
  "audio": {
    "device_index": null,  // null = 자동 선택
    "sample_rate": 16000,
    "channels": 1
  }
}
```

#### 마이크 목록 확인
```bash
# Python 환경에서 마이크 목록 확인
python -c "
import sounddevice as sd
print('사용 가능한 마이크:')
for i, device in enumerate(sd.query_devices()):
    if device['max_input_channels'] > 0:
        print(f'{i}: {device[\"name\"]}')
"
```

### 3. 단축키 설정

기본 단축키: `Ctrl+Alt+Space`

변경하려면 설정 파일에서:
```json
{
  "hotkey": {
    "combination": ["ctrl", "alt", "space"],
    "enabled": true
  }
}
```

**사용 가능한 키**:
- 수정키: `ctrl`, `alt`, `shift`, `cmd` (macOS)
- 기능키: `f1`~`f12`, `space`, `enter`, `tab`
- 문자키: `a`~`z`, `0`~`9`

### 4. Whisper 모델 설정

#### 모델 크기 선택
```json
{
  "whisper": {
    "model_name": "base",  // tiny, base, small, medium, large
    "language": "ko",      // 한국어 고정 또는 "auto"
    "fp16": false          // GPU 가속 (CUDA 필요)
  }
}
```

#### 첫 실행 시 모델 다운로드
처음 실행할 때 선택한 모델이 자동으로 다운로드됩니다:
- `tiny`: 39MB
- `base`: 74MB (권장)
- `small`: 244MB
- `medium`: 769MB
- `large`: 1550MB

---

## ✅ 설치 확인

### 1. 기본 동작 테스트

1. **트레이 아이콘 확인**
   - 시스템 트레이에 마이크 아이콘이 표시되는지 확인
   - 아이콘이 초록색(대기상태)인지 확인

2. **단축키 테스트**
   ```
   1. Ctrl+Alt+Space 누르고 유지
   2. "안녕하세요 테스트입니다" 말하기
   3. 키에서 손 떼기
   4. 몇 초 후 알림 메시지 확인
   5. 메모장에서 Ctrl+V로 붙여넣기 테스트
   ```

3. **로그 확인**
   ```bash
   # 로그 파일 위치
   # Windows: %APPDATA%\speech-to-text\logs\
   # macOS: ~/Library/Application Support/speech-to-text/logs/
   # Linux: ~/.config/speech-to-text/logs/
   ```

### 2. 성능 테스트

#### 메모리 사용량 확인
```bash
# Windows
tasklist | findstr speech-to-text

# macOS/Linux
ps aux | grep speech-to-text
```

#### 응답 시간 측정
- 녹음 시작: 단축키 누름 → 아이콘 빨간색 변경 (< 0.1초)
- 음성 처리: 녹음 종료 → 텍스트 복사 완료 (모델별 차이)
  - `tiny`: 1-3초
  - `base`: 2-5초
  - `small`: 3-8초

---

## 🆘 문제 해결

### 자주 발생하는 설치 문제

#### 1. "No module named 'torch'" 오류
```bash
# PyTorch 수동 설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 2. PortAudio 관련 오류 (Linux)
```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev

# CentOS/RHEL/Fedora
sudo dnf install portaudio-devel
```

#### 3. Qt platform plugin 오류
```bash
# Linux에서 Qt 관련 패키지 설치
sudo apt install qt5-qmltooling-plugins
export QT_QPA_PLATFORM=xcb
```

#### 4. 권한 오류 (macOS)
```bash
# 시스템 환경설정에서 권한 허용 후
sudo xattr -rd com.apple.quarantine "/Applications/Speech to Text.app"
```

#### 5. 바이러스 백신 오류 (Windows)
- Windows Defender에서 실행파일 예외 추가
- 실시간 보호 일시 비활성화 후 설치

### 고급 문제 해결

#### 디버그 모드 실행
```bash
# 상세 로그와 함께 실행
python main.py --debug --verbose

# 또는 환경변수 설정
export SPEECH_TO_TEXT_DEBUG=1
```

#### 설정 초기화
```bash
# 설정 파일 삭제 (자동으로 기본값 재생성)
# Windows
del "%APPDATA%\speech-to-text\settings.json"

# macOS
rm "~/Library/Application Support/speech-to-text/settings.json"

# Linux
rm ~/.config/speech-to-text/settings.json
```

#### 캐시 정리
```bash
# 모델 캐시 정리
# Windows
rmdir /s "%USERPROFILE%\.cache\whisper"

# macOS/Linux
rm -rf ~/.cache/whisper
```

---

## 🗑️ 제거 방법

### 완전 제거

#### Windows
1. **프로그램 제거**
   ```cmd
   # 설치 폴더 삭제
   rmdir /s "C:\Program Files\SpeechToText"
   
   # 또는 제어판에서 제거 (설치 프로그램 사용시)
   ```

2. **설정 및 데이터 삭제**
   ```cmd
   rmdir /s "%APPDATA%\speech-to-text"
   rmdir /s "%USERPROFILE%\.cache\whisper"
   ```

3. **레지스트리 정리** (설치 프로그램 사용시)
   ```cmd
   reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SpeechToText" /f
   ```

#### macOS
1. **앱 삭제**
   ```bash
   rm -rf "/Applications/Speech to Text.app"
   ```

2. **설정 및 데이터 삭제**
   ```bash
   rm -rf "~/Library/Application Support/speech-to-text"
   rm -rf "~/Library/Logs/speech-to-text"
   rm -rf "~/.cache/whisper"
   ```

#### Linux
1. **프로그램 삭제**
   ```bash
   sudo rm -rf /opt/speech-to-text
   sudo rm -f /usr/local/bin/speech-to-text
   ```

2. **설정 및 데이터 삭제**
   ```bash
   rm -rf ~/.config/speech-to-text
   rm -rf ~/.cache/whisper
   ```

### 부분 제거 (설정 보존)
프로그램만 제거하고 설정을 유지하려면 위의 1단계만 실행하세요.

---

## 📞 추가 지원

### 문서 링크
- 📖 [사용자 매뉴얼](USER_MANUAL.md)
- 🛠️ [개발자 가이드](DEVELOPER_GUIDE.md)
- 🆘 [문제 해결 가이드](TROUBLESHOOTING.md)

### 온라인 지원
- 🐛 [버그 리포트](https://github.com/your-repo/speech-to-text/issues)
- 💬 [커뮤니티 토론](https://github.com/your-repo/speech-to-text/discussions)
- 📧 [이메일 지원](mailto:support@example.com)

### 시스템 정보 수집
문제 발생 시 다음 정보를 함께 제공해 주세요:

```bash
# 시스템 정보 수집 스크립트
python -c "
import platform
import sys
import torch
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA 사용 가능: {torch.cuda.is_available()}')
"
```

---

**작성자**: Installation Team  
**최종 업데이트**: 2024년 12월 17일  
**버전**: 1.0.0