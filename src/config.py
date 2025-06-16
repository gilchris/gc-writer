"""
설정 관리 및 상수 정의 모듈
"""

import json
import os
import logging
from typing import Dict, Any, Optional


class Config:
    """설정 관리 클래스"""
    
    # 기본 설정값
    DEFAULT_SETTINGS = {
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "dtype": "float32",
            "device_index": None,
            "silence_threshold": 0.01,
            "remove_silence": True
        },
        "whisper": {
            "model_name": "base",
            "language": "ko",
            "task": "transcribe",
            "fp16": False,
            "temperature": 0.0,
            "best_of": 5,
            "beam_size": 5
        },
        "hotkey": {
            "combination": ["ctrl", "alt", "space"],
            "enabled": True
        },
        "ui": {
            "show_notifications": True,
            "notification_duration": 3000,
            "minimize_to_tray": True,
            "start_minimized": True
        },
        "clipboard": {
            "auto_copy": True,
            "history_enabled": True,
            "max_history": 50,
            "backup_previous": True
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "console_enabled": True,
            "max_file_size": 10485760,  # 10MB
            "backup_count": 5
        },
        "advanced": {
            "gpu_acceleration": False,
            "thread_pool_size": 4,
            "audio_buffer_size": 1024,
            "auto_start": False
        }
    }
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self.settings = {}
        self.logger = logging.getLogger(__name__)
        
        self.load_settings()
    
    def load_settings(self) -> None:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    
                # 기본값과 병합 (누락된 설정 추가)
                self.settings = self._merge_settings(self.DEFAULT_SETTINGS, self.settings)
                
                self.logger.info(f"설정 파일 로드됨: {self.config_file}")
            else:
                self.logger.info("설정 파일이 없습니다. 기본값을 사용합니다.")
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.save_settings()  # 기본 설정 파일 생성
                
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> bool:
        """설정 파일 저장"""
        try:
            # 디렉터리 생성
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"설정 파일 저장됨: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 파일 저장 실패: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """점 표기법으로 설정값 가져오기 (예: 'audio.sample_rate')"""
        try:
            keys = key_path.split('.')
            value = self.settings
            
            for key in keys:
                value = value[key]
                
            return value
            
        except (KeyError, TypeError):
            if default is not None:
                return default
            
            # 기본값에서 찾기
            try:
                keys = key_path.split('.')
                value = self.DEFAULT_SETTINGS
                
                for key in keys:
                    value = value[key]
                    
                return value
                
            except (KeyError, TypeError):
                return None
    
    def set(self, key_path: str, value: Any) -> bool:
        """점 표기법으로 설정값 설정"""
        try:
            keys = key_path.split('.')
            current = self.settings
            
            # 마지막 키를 제외한 모든 키로 이동
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 마지막 키에 값 설정
            current[keys[-1]] = value
            
            return True
            
        except Exception as e:
            self.logger.error(f"설정값 설정 실패 ({key_path}): {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """설정 섹션 전체 가져오기"""
        return self.settings.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]) -> bool:
        """설정 섹션 전체 설정"""
        try:
            self.settings[section] = values
            return True
        except Exception as e:
            self.logger.error(f"설정 섹션 설정 실패 ({section}): {e}")
            return False
    
    def reset_to_default(self, section: Optional[str] = None) -> bool:
        """기본값으로 초기화"""
        try:
            if section:
                if section in self.DEFAULT_SETTINGS:
                    self.settings[section] = self.DEFAULT_SETTINGS[section].copy()
                    self.logger.info(f"설정 섹션 '{section}'이 기본값으로 초기화됨")
                else:
                    self.logger.warning(f"알 수 없는 설정 섹션: {section}")
                    return False
            else:
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.logger.info("모든 설정이 기본값으로 초기화됨")
            
            return True
            
        except Exception as e:
            self.logger.error(f"설정 초기화 실패: {e}")
            return False
    
    @staticmethod
    def _merge_settings(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """기본 설정과 사용자 설정 병합"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_settings(result[key], value)
            else:
                result[key] = value
        
        return result


# 전역 설정 인스턴스
config = Config()


# 상수 정의
class Constants:
    """애플리케이션 상수"""
    
    # 애플리케이션 정보
    APP_NAME = "Speech to Text"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "OpenAI Whisper를 사용한 음성 받아쓰기 프로그램"
    
    # 파일 경로
    LOG_FILE = "speech_to_text.log"
    CONFIG_FILE = "config/settings.json"
    HISTORY_FILE = "clipboard_history.json"
    
    # 오디오 관련
    WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]
    SUPPORTED_LANGUAGES = {
        "ko": "한국어",
        "en": "English",
        "ja": "日本語",
        "zh": "中文",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "ru": "Русский"
    }
    
    # UI 관련
    TRAY_TOOLTIP_DEFAULT = "음성 받아쓰기 프로그램\nCtrl+Alt+Space로 녹음"
    TRAY_TOOLTIP_RECORDING = "녹음 중...\nCtrl+Alt+Space를 놓으면 인식 시작"
    TRAY_TOOLTIP_PROCESSING = "음성 인식 중..."
    
    # 로그 레벨
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # 기본 단축키
    DEFAULT_HOTKEY = ["ctrl", "alt", "space"]
    
    # 파일 크기 제한
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_HISTORY_ITEMS = 100


def setup_logging():
    """로깅 설정"""
    log_level = config.get('logging.level', 'INFO')
    file_enabled = config.get('logging.file_enabled', True)
    console_enabled = config.get('logging.console_enabled', True)
    max_file_size = config.get('logging.max_file_size', Constants.MAX_LOG_FILE_SIZE)
    backup_count = config.get('logging.backup_count', 5)
    
    # 로그 포맷
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(Constants.LOG_LEVELS.get(log_level, logging.INFO))
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 파일 핸들러
    if file_enabled:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            Constants.LOG_FILE,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    logging.info("로깅 시스템이 설정되었습니다")


# 애플리케이션 시작 시 로깅 설정
setup_logging()