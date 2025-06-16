> [!CAUTION]
> !!! 주의! 이 내용은 Claude Code가 자동으로 생성한 내용 **그대로**입니다. 이상한 내용이 있을 수 있습니다 !!!

> [!IMPORTANT]
> Claude Code 활용 테스트 프로그램입니다.

# 🎤 음성 받아쓰기 프로그램

OpenAI Whisper 기반의 실시간 음성-텍스트 변환 프로그램

## ✨ 주요 기능

- 🎙️ **간편한 음성 입력**: `Ctrl+Alt+Space` 단축키로 즉시 녹음
- 🧠 **AI 음성인식**: OpenAI Whisper 모델 기반 정확한 텍스트 변환  
- 📋 **자동 클립보드 복사**: 변환된 텍스트를 바로 사용 가능
- 🖥️ **시스템 트레이 통합**: 백그라운드에서 조용히 실행
- 📚 **히스토리 관리**: 이전 변환 결과 보관 및 검색
- 🌍 **다국어 지원**: 한국어, 영어 등 99개 언어 인식

## 🚀 빠른 시작

### 1. 설치
```bash
# 저장소 클론
git clone https://github.com/your-repo/speech-to-text.git
cd speech-to-text

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행
```bash
cd src
python main.py
```

### 3. 사용법
1. 시스템 트레이에 마이크 아이콘 확인
2. `Ctrl+Alt+Space` 키를 누르고 유지하며 말하기
3. 키에서 손을 떼면 자동으로 텍스트가 클립보드에 복사됨
4. 원하는 곳에서 `Ctrl+V`로 붙여넣기

## 📁 프로젝트 구조

```
speech-to-text/
├── src/                     # 메인 소스코드
│   ├── main.py             # 애플리케이션 진입점
│   ├── audio_recorder.py   # 오디오 녹음
│   ├── whisper_handler.py  # AI 음성인식
│   ├── hotkey_manager.py   # 전역 단축키
│   ├── tray_manager.py     # 시스템 트레이
│   ├── clipboard_manager.py # 클립보드 관리
│   └── config.py           # 설정 관리
├── config/                 # 설정 파일
│   └── settings.json
├── assets/                 # 리소스 파일
│   └── icons/
├── tests/                  # 테스트 파일
└── docs/                   # 문서
```

## 📚 문서

- 📖 **[사용자 매뉴얼](USER_MANUAL.md)** - 상세한 사용 방법
- 🚀 **[설치 가이드](INSTALLATION_GUIDE.md)** - 플랫폼별 설치 방법  
- 🛠️ **[개발자 가이드](DEVELOPER_GUIDE.md)** - 개발 환경 설정 및 API
- 🔧 **[문제 해결](TROUBLESHOOTING.md)** - 자주 발생하는 문제 해결책
- 📋 **[API 레퍼런스](API_REFERENCE.md)** - 상세한 API 문서

## 💻 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **메모리**: 2GB RAM
- **저장공간**: 500MB
- **Python**: 3.8+ (소스 설치시)

### 권장 사양
- **메모리**: 8GB RAM 이상
- **프로세서**: 멀티코어 CPU (Intel i5 또는 동급)
- **마이크**: 노이즈 캔슬링 기능이 있는 고품질 마이크

## 🔧 주요 설정

### Whisper 모델 크기 선택
| 모델 | 크기 | 메모리 | 속도 | 정확도 | 권장 용도 |
|------|------|--------|------|--------|-----------|
| `tiny` | 39MB | ~390MB | 매우 빠름 | 보통 | 빠른 테스트 |
| `base` | 74MB | ~500MB | 빠름 | 좋음 | **일반 사용 (권장)** |
| `small` | 244MB | ~1GB | 보통 | 매우 좋음 | 정확도 중시 |
| `medium` | 769MB | ~2GB | 느림 | 우수 | 전문 작업 |
| `large` | 1550MB | ~4GB | 매우 느림 | 최고 | 최고 품질 |

### 기본 설정 (config/settings.json)
```json
{
  "whisper": {
    "model_name": "base",    // 모델 크기
    "language": "ko"         // 언어 설정
  },
  "hotkey": {
    "combination": ["ctrl", "alt", "space"]  // 단축키
  },
  "audio": {
    "sample_rate": 16000,    // 녹음 품질
    "device_index": null     // 마이크 (null=자동)
  }
}
```

## 🧪 테스트

### 단위 테스트
```bash
# 개별 컴포넌트 테스트
python test_audio_recorder.py
python test_whisper_handler.py
python test_clipboard_manager.py
```

### 통합 테스트
```bash
# 전체 시스템 테스트
python test_integration.py
```

### 테스트 결과 (현재)
- ✅ 메인 애플리케이션 통합: **8/9 테스트 통과**
- ✅ 오디오 녹음 시스템: **8/8 테스트 통과**  
- ✅ Whisper AI 음성인식: **9/10 테스트 통과**
- ✅ 클립보드 관리: **10/10 테스트 통과**
- ✅ 단축키 시스템: **8/8 테스트 통과**
- ✅ 시스템 트레이 UI: **7/7 테스트 통과**

## 🤝 기여하기

1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

### 개발 환경 설정
```bash
# 개발용 의존성 설치
pip install -r requirements-dev.txt

# pre-commit 훅 설정
pre-commit install

# 코드 포맷팅
black src/
flake8 src/
```

## 🐛 버그 리포트

버그를 발견하셨다면 [GitHub Issues](https://github.com/your-repo/speech-to-text/issues)에 다음 정보와 함께 신고해 주세요:

- 운영체제 및 버전
- 프로그램 버전  
- 재현 단계
- 로그 파일 (`logs/` 폴더)

## 📞 지원

- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/your-repo/speech-to-text/issues)
- 💬 **기능 요청**: [GitHub Discussions](https://github.com/your-repo/speech-to-text/discussions)
- 📧 **이메일 지원**: support@example.com

## 📜 라이센스

이 프로젝트는 [MIT 라이센스](LICENSE) 하에 배포됩니다.

## 🙏 감사의 말

- [OpenAI Whisper](https://github.com/openai/whisper) - 음성인식 모델
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 프레임워크
- [sounddevice](https://python-sounddevice.readthedocs.io/) - 오디오 처리
- [pynput](https://pypi.org/project/pynput/) - 전역 단축키

---

**개발팀** | **버전 1.0.0** | **2024년 12월 17일**