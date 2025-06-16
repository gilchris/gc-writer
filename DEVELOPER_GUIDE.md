> [!CAUTION]
> !!! 주의! 이 내용은 Claude Code가 자동으로 생성한 내용 **그대로**입니다. 이상한 내용이 있을 수 있습니다 !!!

# 🛠️ 개발자 가이드

## 📖 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [개발 환경 설정](#개발-환경-설정)
4. [코드 구조](#코드-구조)
5. [컴포넌트 상세](#컴포넌트-상세)
6. [API 레퍼런스](#api-레퍼런스)
7. [테스트](#테스트)
8. [배포](#배포)

---

## 🌟 프로젝트 개요

### 기술 스택
- **언어**: Python 3.8+
- **GUI 프레임워크**: PyQt6
- **음성인식**: OpenAI Whisper
- **오디오 처리**: sounddevice, numpy
- **전역 단축키**: pynput
- **클립보드**: pyperclip
- **설정 관리**: JSON
- **로깅**: Python logging module

### 핵심 기능
- 실시간 음성 녹음 및 처리
- AI 기반 음성-텍스트 변환
- 시스템 트레이 통합
- 전역 단축키 처리
- 클립보드 자동 복사
- 설정 관리 및 히스토리

---

## 🏗️ 아키텍처

### 전체 아키텍처 다이어그램
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TrayManager   │    │  HotkeyManager  │    │  AudioRecorder  │
│                 │    │                 │    │                 │
│ - UI 상태 관리   │    │ - 전역 단축키    │    │ - 실시간 녹음    │
│ - 메뉴 처리      │    │ - 이벤트 감지    │    │ - 버퍼 관리      │
│ - 알림 표시      │    │ - 권한 처리      │    │ - 품질 제어      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │     SpeechToTextApp     │
                    │                         │
                    │   - 메인 컨트롤러        │
                    │   - 컴포넌트 통합        │
                    │   - 워크플로우 관리      │
                    │   - 에러 처리            │
                    │   - 통계 수집            │
                    └─────────────┬───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────┴───────┐    ┌─────────┴───────┐    ┌─────────┴───────┐
│ WhisperHandler  │    │ClipboardManager │    │   ConfigManager │
│                 │    │                 │    │                 │
│ - 모델 관리      │    │ - 클립보드 조작  │    │ - 설정 로드/저장 │
│ - 음성-텍스트    │    │ - 히스토리 관리  │    │ - 기본값 관리    │
│ - 언어 감지      │    │ - 백업/복원      │    │ - 검증 처리      │
│ - 성능 최적화    │    │ - 텍스트 정리    │    │ - 실시간 업데이트│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 데이터 플로우
```
사용자 입력 (Ctrl+Alt+Space)
         ↓
   HotkeyManager (이벤트 감지)
         ↓
   AudioRecorder (녹음 시작)
         ↓
   오디오 데이터 수집
         ↓
   WhisperHandler (AI 처리)
         ↓
   텍스트 변환 결과
         ↓
   ClipboardManager (클립보드 복사)
         ↓
   TrayManager (사용자 알림)
```

---

## 🔧 개발 환경 설정

### 1. 저장소 클론 및 환경 설정
```bash
# 저장소 클론
git clone https://github.com/your-repo/speech-to-text.git
cd speech-to-text

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 개발 도구 설정
```bash
# 개발용 추가 패키지 설치
pip install -r requirements-dev.txt

# pre-commit 훅 설정
pre-commit install

# 코드 포맷팅 도구 설정
black --line-length 100 src/
flake8 src/
```

### 3. IDE 설정 (VS Code 권장)

**`.vscode/settings.json`**:
```json
{
    "python.defaultInterpreter": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"]
}
```

---

## 📁 코드 구조

### 프로젝트 레이아웃
```
speech-to-text/
├── src/                          # 메인 소스코드
│   ├── main.py                   # 애플리케이션 진입점
│   ├── config.py                 # 설정 관리
│   ├── audio_recorder.py         # 오디오 녹음
│   ├── whisper_handler.py        # AI 음성인식
│   ├── hotkey_manager.py         # 전역 단축키
│   ├── tray_manager.py           # 시스템 트레이
│   ├── clipboard_manager.py      # 클립보드 관리
│   └── utils/                    # 유틸리티 모듈
│       ├── __init__.py
│       ├── audio_utils.py        # 오디오 처리 유틸
│       └── platform_utils.py     # 플랫폼별 유틸
├── tests/                        # 테스트 파일
│   ├── __init__.py
│   ├── test_audio_recorder.py
│   ├── test_whisper_handler.py
│   ├── test_hotkey_manager.py
│   ├── test_tray_manager.py
│   ├── test_clipboard_manager.py
│   └── test_integration.py
├── config/                       # 설정 파일
│   └── settings.json
├── assets/                       # 리소스 파일
│   └── icons/
│       ├── microphone.png
│       ├── microphone_active.png
│       └── microphone_error.png
├── docs/                         # 문서
│   ├── USER_MANUAL.md
│   ├── DEVELOPER_GUIDE.md
│   └── API_REFERENCE.md
├── logs/                         # 로그 파일 (런타임 생성)
├── requirements.txt              # 운영 의존성
├── requirements-dev.txt          # 개발 의존성
├── setup.py                      # 패키지 설정
├── pyproject.toml               # 프로젝트 메타데이터
└── README.md                     # 프로젝트 소개
```

### 코딩 컨벤션

#### 1. 네이밍 규칙
- **클래스**: PascalCase (`SpeechToTextApp`)
- **함수/변수**: snake_case (`get_audio_devices`)
- **상수**: UPPER_SNAKE_CASE (`MAX_RECORDING_DURATION`)
- **파일명**: snake_case (`audio_recorder.py`)

#### 2. 독스트링 형식
```python
def transcribe_audio(self, audio_data: np.ndarray, language: str = "auto") -> Dict[str, Any]:
    """
    오디오 데이터를 텍스트로 변환합니다.
    
    Args:
        audio_data: 16kHz, float32 형식의 오디오 배열
        language: 대상 언어 코드 (기본값: "auto")
    
    Returns:
        변환 결과를 담은 딕셔너리:
        - text: 변환된 텍스트
        - confidence: 신뢰도 (0.0-1.0)
        - language: 감지된 언어
        - processing_time: 처리 시간 (초)
    
    Raises:
        AudioProcessingError: 오디오 데이터가 유효하지 않을 때
        ModelNotLoadedError: Whisper 모델이 로드되지 않았을 때
    """
```

#### 3. 에러 처리
```python
# 구체적인 예외 클래스 사용
try:
    result = self.whisper_handler.transcribe(audio_data)
except ModelNotLoadedError:
    self.logger.error("Whisper 모델이 로드되지 않음")
    self.show_error_notification("모델 로딩 중입니다. 잠시 후 다시 시도하세요.")
except AudioProcessingError as e:
    self.logger.error(f"오디오 처리 실패: {e}")
    self.show_error_notification("오디오 처리에 실패했습니다.")
```

---

## 🧩 컴포넌트 상세

### 1. SpeechToTextApp (main.py)

메인 애플리케이션 컨트롤러로 모든 컴포넌트를 통합 관리합니다.

**주요 책임**:
- 컴포넌트 생명주기 관리
- 전체 워크플로우 조정
- 에러 처리 및 복구
- 통계 수집 및 모니터링

**핵심 메서드**:
```python
class SpeechToTextApp(QObject):
    def __init__(self):
        """애플리케이션 초기화"""
        
    def initialize_components(self):
        """모든 컴포넌트 순차 초기화"""
        
    def setup_connections(self):
        """컴포넌트 간 시그널 연결"""
        
    def start_recording(self):
        """음성 녹음 시작"""
        
    def stop_recording(self):
        """음성 녹음 종료"""
        
    def process_audio(self, audio_data: np.ndarray):
        """오디오 데이터 처리"""
        
    def copy_to_clipboard(self, text: str, metadata: dict):
        """텍스트 클립보드 복사"""
```

### 2. AudioRecorder (audio_recorder.py)

실시간 오디오 캡처 및 버퍼 관리를 담당합니다.

**주요 기능**:
- 마이크 장치 자동 감지
- 실시간 오디오 스트리밍
- 메모리 효율적 버퍼링
- 노이즈 감소 및 품질 향상

**핵심 메서드**:
```python
class AudioRecorder(QObject):
    def get_available_devices(self) -> List[Dict]:
        """사용 가능한 마이크 장치 목록 반환"""
        
    def start_recording(self) -> bool:
        """녹음 시작"""
        
    def stop_recording(self) -> np.ndarray:
        """녹음 종료 및 오디오 데이터 반환"""
        
    def _audio_callback(self, indata, frames, time, status):
        """실시간 오디오 콜백"""
```

### 3. WhisperHandler (whisper_handler.py)

OpenAI Whisper 모델을 사용한 음성-텍스트 변환을 처리합니다.

**주요 기능**:
- Whisper 모델 로딩 및 캐싱
- 비동기 음성 변환
- 언어 자동 감지
- GPU 가속 지원

**핵심 메서드**:
```python
class WhisperHandler(QObject):
    def load_model(self, model_name: str = "base") -> bool:
        """Whisper 모델 로드"""
        
    def transcribe_audio(self, audio_data: np.ndarray, **options) -> Dict:
        """오디오를 텍스트로 변환"""
        
    def get_supported_languages(self) -> List[str]:
        """지원되는 언어 목록 반환"""
        
    def _preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """오디오 전처리"""
```

### 4. HotkeyManager (hotkey_manager.py)

전역 단축키 감지 및 처리를 담당합니다.

**주요 기능**:
- 크로스 플랫폼 단축키 지원
- 키 조합 감지
- 권한 처리 및 에러 복구
- 백그라운드 모니터링

**핵심 메서드**:
```python
class HotkeyManager(QObject):
    def set_hotkey(self, combination: List[str]) -> bool:
        """단축키 조합 설정"""
        
    def start(self) -> bool:
        """단축키 모니터링 시작"""
        
    def stop(self):
        """단축키 모니터링 중지"""
        
    def _on_hotkey_press(self):
        """단축키 눌림 이벤트"""
        
    def _on_hotkey_release(self):
        """단축키 떼기 이벤트"""
```

### 5. TrayManager (tray_manager.py)

시스템 트레이 UI 및 상태 표시를 관리합니다.

**주요 기능**:
- 동적 트레이 아이콘
- 컨텍스트 메뉴 관리
- 상태 알림
- 사용자 상호작용 처리

**핵심 메서드**:
```python
class TrayManager(QObject):
    def setup_tray(self):
        """트레이 아이콘 및 메뉴 설정"""
        
    def set_status(self, status: str, message: str = ""):
        """트레이 상태 업데이트"""
        
    def show_message(self, title: str, message: str, duration: int = 3000):
        """시스템 알림 표시"""
        
    def create_microphone_icon(self, color: str, size: int = 22) -> QIcon:
        """마이크 모양 아이콘 생성"""
```

### 6. ClipboardManager (clipboard_manager.py)

클립보드 조작 및 히스토리 관리를 담당합니다.

**주요 기능**:
- 자동 클립보드 복사
- 이전 내용 백업/복원
- 히스토리 관리 및 검색
- 텍스트 검증 및 정리

**핵심 메서드**:
```python
class ClipboardManager(QObject):
    def copy_text(self, text: str, metadata: dict = None) -> bool:
        """텍스트를 클립보드에 복사"""
        
    def get_history(self, limit: int = None) -> List[Dict]:
        """클립보드 히스토리 반환"""
        
    def search_history(self, keyword: str) -> List[Dict]:
        """히스토리에서 키워드 검색"""
        
    def restore_previous_clipboard(self) -> bool:
        """이전 클립보드 내용 복원"""
```

---

## 🧪 테스트

### 테스트 구조
```
tests/
├── unit/                    # 단위 테스트
│   ├── test_audio_recorder.py
│   ├── test_whisper_handler.py
│   └── ...
├── integration/             # 통합 테스트
│   ├── test_workflow.py
│   └── test_component_integration.py
└── e2e/                     # 엔드투엔드 테스트
    └── test_full_system.py
```

### 테스트 실행
```bash
# 모든 테스트 실행
python -m pytest tests/

# 특정 테스트 파일 실행
python -m pytest tests/unit/test_audio_recorder.py

# 커버리지 포함 실행
python -m pytest --cov=src tests/

# 통합 테스트만 실행
python src/test_integration.py
```

### Mock 사용 예시
```python
import unittest.mock as mock
from unittest.mock import MagicMock, patch

class TestWhisperHandler(unittest.TestCase):
    def setUp(self):
        self.whisper_handler = WhisperHandler()
    
    @patch('whisper.load_model')
    def test_load_model_success(self, mock_load_model):
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        result = self.whisper_handler.load_model("base")
        
        self.assertTrue(result)
        mock_load_model.assert_called_once_with("base")
```

---

## 🚀 배포

### 1. PyInstaller를 사용한 바이너리 생성

**build.spec 파일**:
```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['./'],
    binaries=[],
    datas=[
        ('config/', 'config/'),
        ('assets/', 'assets/'),
    ],
    hiddenimports=[
        'whisper',
        'torch',
        'numpy',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='speech-to-text',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/microphone.ico'
)
```

**빌드 스크립트**:
```bash
#!/bin/bash
# build.sh

echo "🔨 빌드 시작..."

# 가상환경 활성화
source venv/bin/activate

# 의존성 확인
pip install -r requirements.txt

# 이전 빌드 정리
rm -rf build/ dist/

# PyInstaller 실행
pyinstaller build.spec

# 빌드 완료 확인
if [ -f "dist/speech-to-text" ]; then
    echo "✅ 빌드 성공: dist/speech-to-text"
    
    # 실행 파일 크기 확인
    du -h dist/speech-to-text
    
    # 간단한 실행 테스트
    ./dist/speech-to-text --version
else
    echo "❌ 빌드 실패"
    exit 1
fi
```

### 2. 배포 패키지 생성

**Windows (NSIS)**:
```nsis
# installer.nsi
Name "Speech to Text"
OutFile "SpeechToText-Installer.exe"
InstallDir "$PROGRAMFILES\SpeechToText"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\*"
    
    CreateDirectory "$SMPROGRAMS\Speech to Text"
    CreateShortCut "$SMPROGRAMS\Speech to Text\Speech to Text.lnk" "$INSTDIR\speech-to-text.exe"
    CreateShortCut "$DESKTOP\Speech to Text.lnk" "$INSTDIR\speech-to-text.exe"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SpeechToText" \
                     "DisplayName" "Speech to Text"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SpeechToText" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd
```

**macOS (DMG)**:
```bash
#!/bin/bash
# create_dmg.sh

APP_NAME="Speech to Text"
DMG_NAME="SpeechToText-1.0.0"

# 임시 디렉토리 생성
mkdir -p dmg_temp

# 앱 번들 복사
cp -R "dist/${APP_NAME}.app" dmg_temp/

# 심볼릭 링크 생성 (Applications 폴더)
ln -s /Applications dmg_temp/Applications

# DMG 생성
hdiutil create -volname "${APP_NAME}" -srcfolder dmg_temp -ov -format UDZO "${DMG_NAME}.dmg"

# 정리
rm -rf dmg_temp

echo "✅ DMG 생성 완료: ${DMG_NAME}.dmg"
```

### 3. CI/CD 파이프라인 (GitHub Actions)

**.github/workflows/build.yml**:
```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: pyinstaller build.spec
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: windows-build
        path: dist/

  build-macos:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: pyinstaller build.spec
    
    - name: Create DMG
      run: ./scripts/create_dmg.sh
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: macos-build
        path: "*.dmg"

  release:
    needs: [build-windows, build-macos]
    runs-on: ubuntu-latest
    steps:
    - name: Download all artifacts
      uses: actions/download-artifact@v3
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

---

## 🔍 디버깅 및 프로파일링

### 로깅 활용
```python
import logging

# 상세 디버그 로깅 활성화
logging.getLogger().setLevel(logging.DEBUG)

# 특정 컴포넌트만 디버그
logging.getLogger('whisper_handler').setLevel(logging.DEBUG)
```

### 메모리 프로파일링
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # 메모리 사용량을 모니터링할 함수
    pass
```

### 성능 측정
```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

@timer
def transcribe_audio(self, audio_data):
    # 성능을 측정할 함수
    pass
```

---

## 📝 기여 가이드

### 1. 코드 기여 프로세스
1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

### 2. 커밋 메시지 컨벤션
```
type(scope): description

feat(audio): 마이크 노이즈 캔슬링 기능 추가
fix(whisper): 모델 로딩 시 메모리 누수 수정
docs(readme): 설치 가이드 업데이트
test(integration): 워크플로우 테스트 추가
refactor(config): 설정 관리 코드 리팩토링
```

### 3. 코드 리뷰 체크리스트
- [ ] 코딩 컨벤션 준수
- [ ] 단위 테스트 작성
- [ ] 독스트링 추가
- [ ] 에러 처리 포함
- [ ] 성능 최적화 고려
- [ ] 보안 이슈 확인

---

**작성자**: Development Team  
**최종 업데이트**: 2024년 12월 17일  
**버전**: 1.0.0