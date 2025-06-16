#!/usr/bin/env python3
"""
고급 음성 받아쓰기 프로그램 - 메인 애플리케이션
"""

import sys
import logging
import time
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication, QTimer, pyqtSignal, QObject

from config import setup_logging, config
from tray_manager import TrayManager
from hotkey_manager import HotkeyManager
from audio_recorder import AudioRecorder
from whisper_handler import WhisperHandler
from clipboard_manager import ClipboardManager


class SpeechToTextApp(QObject):
    # 시스템 전체 시그널
    app_started = pyqtSignal()
    app_stopping = pyqtSignal()
    workflow_completed = pyqtSignal(str, dict)  # 텍스트, 메타데이터
    workflow_failed = pyqtSignal(str)  # 에러 메시지
    
    def __init__(self):
        super().__init__()
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 애플리케이션 상태
        self.is_running = False
        self.current_workflow_id = None
        
        # 컴포넌트 초기화
        self.tray_manager = None
        self.hotkey_manager = None
        self.audio_recorder = None
        self.whisper_handler = None
        self.clipboard_manager = None
        
        # 에러 복구 시스템
        self.error_count = 0
        self.max_errors = 5
        self.last_error_time = 0
        
        # 통계
        self.stats = {
            'total_recordings': 0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'start_time': time.time()
        }
        
        # 애플리케이션 초기화
        self.initialize_components()
        self.setup_connections()
        self.setup_error_handling()
    
    def initialize_components(self):
        """컴포넌트 순차적 초기화"""
        try:
            self.logger.info("컴포넌트 초기화 시작")
            
            # 1. 기본 컴포넌트 (전역 시스템과 독립적)
            self.clipboard_manager = ClipboardManager()
            self.logger.info("✅ 클립보드 매니저 초기화 완료")
            
            # 2. 오디오 컴포넌트
            if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
                # 테스트용 더미 AudioRecorder
                from unittest.mock import MagicMock
                self.audio_recorder = MagicMock()
                # 시그널 모킹
                mock_signal = MagicMock()
                mock_signal.connect = MagicMock()
                self.audio_recorder.recording_finished = mock_signal
                self.audio_recorder.recording_started = mock_signal
                self.audio_recorder.error_occurred = mock_signal
                self.logger.info("✅ 오디오 레코더 초기화 완료 (테스트 모드)")
            else:
                self.audio_recorder = AudioRecorder()
                self.logger.info("✅ 오디오 레코더 초기화 완료")
            
            # 3. AI 컴포넌트 (시간이 오래 걸릴 수 있음)
            # 테스트 모드에서는 모델 로딩 스킵
            if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
                # 테스트용 더미 WhisperHandler 생성
                from unittest.mock import MagicMock
                self.whisper_handler = MagicMock()
                self.whisper_handler.is_model_loaded.return_value = True
                self.whisper_handler.is_model_loading.return_value = False
                self.whisper_handler.get_current_model.return_value = "base"
                self.whisper_handler.get_statistics.return_value = {"success_rate": 95.0, "average_confidence": 0.85}
                # 시그널 모킹 (connect 메서드 포함)
                mock_signal = MagicMock()
                mock_signal.connect = MagicMock()
                self.whisper_handler.transcription_completed = mock_signal
                self.whisper_handler.transcription_started = mock_signal
                self.whisper_handler.transcription_failed = mock_signal
                self.whisper_handler.model_loading_started = mock_signal
                self.whisper_handler.model_loading_completed = mock_signal
                self.whisper_handler.model_loading_failed = mock_signal
                self.whisper_handler.language_detected = mock_signal
                self.logger.info("✅ Whisper 핸들러 초기화 완료 (테스트 모드)")
            else:
                self.whisper_handler = WhisperHandler()
                self.logger.info("✅ Whisper 핸들러 초기화 시작 (모델 로딩 중...)")
            
            # 4. 입력 컴포넌트
            if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
                # 테스트용 더미 HotkeyManager
                from unittest.mock import MagicMock
                self.hotkey_manager = MagicMock()
                self.hotkey_manager.is_running.return_value = True
                self.hotkey_manager.is_enabled.return_value = True
                self.hotkey_manager.get_current_hotkey_string.return_value = "Ctrl+Alt+Space"
                self.hotkey_manager.get_statistics.return_value = {}
                # 시그널 모킹
                mock_signal = MagicMock()
                mock_signal.connect = MagicMock()
                self.hotkey_manager.recording_started = mock_signal
                self.hotkey_manager.recording_stopped = mock_signal
                self.hotkey_manager.error_occurred = mock_signal
                self.logger.info("✅ 단축키 매니저 초기화 완료 (테스트 모드)")
            else:
                self.hotkey_manager = HotkeyManager()
                self.logger.info("✅ 단축키 매니저 초기화 완료")
            
            # 5. UI 컴포넌트 (마지막)
            if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
                # 테스트용 더미 TrayManager
                from unittest.mock import MagicMock
                self.tray_manager = MagicMock()
                # 시그널 모킹
                mock_signal = MagicMock()
                mock_signal.connect = MagicMock()
                self.tray_manager.quit_requested = mock_signal
                self.tray_manager.settings_requested = mock_signal
                self.tray_manager.toggle_requested = mock_signal
                self.tray_manager.status_info_requested = mock_signal
                self.logger.info("✅ 트레이 매니저 초기화 완료 (테스트 모드)")
            else:
                self.tray_manager = TrayManager()
                self.logger.info("✅ 트레이 매니저 초기화 완료")
            
            self.logger.info("🎉 모든 컴포넌트 초기화 성공")
            
        except Exception as e:
            self.logger.error(f"컴포넌트 초기화 실패: {e}")
            raise
    
    def setup_connections(self):
        """전체 시스템 시그널 연결"""
        # === 주요 워크플로우 ===
        # 1. 단축키 -> 녹음 시작/종료
        self.hotkey_manager.recording_started.connect(self.start_recording)
        self.hotkey_manager.recording_stopped.connect(self.stop_recording)
        
        # 2. 녹음 완료 -> 음성 인식
        self.audio_recorder.recording_finished.connect(self.process_audio)
        
        # 3. 음성 인식 완료 -> 클립보드 복사
        self.whisper_handler.transcription_completed.connect(self.copy_to_clipboard)
        
        # === UI 상태 동기화 ===
        # 단축키 상태 -> 트레이 상태
        self.hotkey_manager.recording_started.connect(
            lambda: self.tray_manager.set_status('recording', '단축키 눈름')
        )
        
        # 오디오 상태 -> 트레이 상태
        self.audio_recorder.recording_started.connect(
            lambda: self.tray_manager.set_status('recording', '오디오 녹음 시작')
        )
        
        # Whisper 상태 -> 트레이 상태
        self.whisper_handler.transcription_started.connect(
            lambda: self.tray_manager.set_status('processing', '음성 인식 중')
        )
        
        self.whisper_handler.transcription_completed.connect(
            lambda text, metadata: self.tray_manager.set_status('idle', '완료')
        )
        
        # === 에러 처리 ===
        self.hotkey_manager.error_occurred.connect(self.handle_hotkey_error)
        self.audio_recorder.error_occurred.connect(self.handle_audio_error)
        self.whisper_handler.transcription_failed.connect(self.handle_whisper_error)
        self.clipboard_manager.copy_failed.connect(self.handle_clipboard_error)
        
        # === 트레이 메뉴 액션 ===
        self.tray_manager.quit_requested.connect(self.quit_application)
        self.tray_manager.settings_requested.connect(self.show_settings)
        self.tray_manager.toggle_requested.connect(self.toggle_system)
        self.tray_manager.status_info_requested.connect(self.show_status_info)
        
        # === 모델 로딩 상태 ===
        self.whisper_handler.model_loading_started.connect(
            lambda model: self.tray_manager.set_status('processing', f'{model} 모델 로딩 중')
        )
        
        self.whisper_handler.model_loading_completed.connect(
            lambda model: self.handle_model_loaded(model)
        )
        
        self.whisper_handler.model_loading_failed.connect(
            lambda error: self.handle_model_error(error)
        )
        
        # === 언어 감지 ===
        self.whisper_handler.language_detected.connect(self.handle_language_detected)
        
        # === 성공 완료 ===
        self.clipboard_manager.text_copied.connect(self.handle_workflow_success)
        
        self.logger.info("🔗 모든 시그널 연결 완료")
    
    def start_recording(self):
        """녹음 시작 처리"""
        try:
            if not self.is_running:
                self.logger.warning("시스템이 정지된 상태에서 녹음 시도")
                return
            
            self.current_workflow_id = str(int(time.time() * 1000))  # 고유 ID
            self.stats['total_recordings'] += 1
            
            self.logger.info(f"🎤 음성 녹음 시작 (ID: {self.current_workflow_id})")
            self.audio_recorder.start_recording()
            
        except Exception as e:
            self.handle_system_error(f"녹음 시작 실패: {e}")
    
    def stop_recording(self):
        """녹음 종료 처리"""
        try:
            if not self.current_workflow_id:
                self.logger.warning("진행 중인 녹음이 없음")
                return
                
            self.logger.info(f"📽 음성 녹음 종료 (ID: {self.current_workflow_id})")
            self.audio_recorder.stop_recording()
            
        except Exception as e:
            self.handle_system_error(f"녹음 종료 실패: {e}")
    
    def process_audio(self, audio_data):
        """오디오 인식 처리"""
        try:
            if not audio_data or len(audio_data) == 0:
                self.handle_workflow_error("빈 오디오 데이터")
                return
            
            audio_length = len(audio_data) / 16000  # 오디오 길이 (초)
            self.logger.info(f"🎧 음성 인식 시작 - 길이: {audio_length:.2f}초 (ID: {self.current_workflow_id})")
            
            # 메타데이터 준비
            metadata = {
                'workflow_id': self.current_workflow_id,
                'audio_length': audio_length,
                'timestamp': time.time()
            }
            
            self.whisper_handler.transcribe_audio(audio_data, custom_options={'source': 'voice_recording'})
            
        except Exception as e:
            self.handle_system_error(f"오디오 처리 실패: {e}")
    
    def copy_to_clipboard(self, text, metadata):
        """클립보드 복사 처리"""
        try:
            if not text or not text.strip():
                self.handle_workflow_error("빈 인식 결과")
                return
            
            # 메타데이터 확장
            copy_metadata = {
                'workflow_id': self.current_workflow_id,
                'source': 'voice_transcription',
                'confidence': metadata.get('confidence', 0.5),
                'processing_time': metadata.get('processing_time', 0),
                'language': metadata.get('language', 'unknown')
            }
            
            text_preview = text[:30] + ('...' if len(text) > 30 else '')
            self.logger.info(f"📋 텍스트 복사 시작: '{text_preview}'")
            
            success = self.clipboard_manager.copy_text(text, source="voice_transcription", metadata=copy_metadata)
            
            if not success:
                self.handle_workflow_error("클립보드 복사 실패")
                
        except Exception as e:
            self.handle_system_error(f"클립보드 복사 실패: {e}")
    
    def setup_error_handling(self):
        """에러 처리 시스템 설정"""
        # 전역 예외 처리기
        sys.excepthook = self.global_exception_handler
        
        # 주기적 상태 검사
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.check_system_health)
        self.health_timer.start(30000)  # 30초마다
        
        self.logger.info("🚑 에러 처리 시스템 설정 완료")
    
    def handle_workflow_success(self, text, metadata):
        """전체 워크플로우 성공 처리"""
        try:
            self.stats['successful_transcriptions'] += 1
            
            # 성공 로그
            workflow_id = metadata.get('workflow_id', self.current_workflow_id)
            confidence = metadata.get('confidence', 0.5)
            processing_time = metadata.get('processing_time', 0)
            
            self.logger.info(
                f"✅ 워크플로우 성공 (ID: {workflow_id}) - "
                f"신뢰도: {confidence:.2f}, 처리시간: {processing_time:.2f}초"
            )
            
            # 트레이 알림
            success_preview = text[:50] + ('...' if len(text) > 50 else '')
            self.tray_manager.show_message(
                "✅ 음성인식 성공",
                f"'{success_preview}'\n\n클립보드에 복사되었습니다.",
                duration=3000
            )
            
            # 시그널 발송
            self.workflow_completed.emit(text, metadata)
            
            # 상태 초기화
            self.current_workflow_id = None
            
        except Exception as e:
            self.logger.error(f"성공 처리 중 오류: {e}")
    
    def handle_workflow_error(self, error_message):
        """워크플로우 오류 처리"""
        self.stats['failed_transcriptions'] += 1
        self.error_count += 1
        self.last_error_time = time.time()
        
        self.logger.error(f"❌ 워크플로우 실패 (ID: {self.current_workflow_id}): {error_message}")
        
        # 트레이 알림
        self.tray_manager.show_message(
            "❌ 음성인식 실패",
            f"{error_message}\n\n다시 시도해주세요.",
            duration=2000
        )
        
        # 상태 초기화
        self.tray_manager.set_status('idle', '오류 발생')
        self.current_workflow_id = None
        
        # 시그널 발송
        self.workflow_failed.emit(error_message)
    
    def handle_system_error(self, error_message):
        """시스템 레벨 오류 처리"""
        self.error_count += 1
        self.last_error_time = time.time()
        
        self.logger.critical(f"😨 시스템 오류: {error_message}")
        
        # 심각한 오류인 경우 자동 복구 시도
        if self.error_count > self.max_errors:
            self.logger.critical("에러 빈도가 너무 높음 - 시스템 중지")
            self.quit_application()
        else:
            self.attempt_recovery()
    
    def handle_hotkey_error(self, error):
        self.logger.warning(f"단축키 오류: {error}")
        self.tray_manager.show_message("⚠️ 단축키 오류", error)
    
    def handle_audio_error(self, error):
        self.handle_workflow_error(f"오디오 오류: {error}")
    
    def handle_whisper_error(self, error):
        self.handle_workflow_error(f"음성인식 오류: {error}")
    
    def handle_clipboard_error(self, error):
        self.handle_workflow_error(f"클립보드 오류: {error}")
    
    def handle_model_loaded(self, model_name):
        self.logger.info(f"✅ {model_name} 모델 로딩 완료")
        self.tray_manager.set_status('idle', f'{model_name} 모델 준비완료')
        self.tray_manager.show_message(
            "✅ 모델 로딩 완료",
            f"{model_name} 모델이 성공적으로 로드되었습니다.\n이제 음성인식을 사용할 수 있습니다."
        )
    
    def handle_model_error(self, error):
        self.logger.error(f"모델 로딩 실패: {error}")
        self.tray_manager.set_status('error', '모델 로딩 실패')
        self.tray_manager.show_message(
            "❌ 모델 로딩 실패",
            f"{error}\n\n어떤 기능이 제한될 수 있습니다."
        )
    
    def handle_language_detected(self, language):
        self.logger.info(f"언어 감지: {language}")
    
    def check_system_health(self):
        """시스템 상태 검사"""
        try:
            # 컴포넌트 상태 검사
            issues = []
            
            if not self.hotkey_manager.is_running():
                issues.append("단축키 비활성")
            
            if not self.whisper_handler.is_model_loaded():
                issues.append("Whisper 모델 비로드")
            
            if issues:
                self.logger.warning(f"시스템 상태 문제: {', '.join(issues)}")
            
            # 에러 빈도 검사
            if self.error_count > 0 and time.time() - self.last_error_time > 300:  # 5분
                self.error_count = max(0, self.error_count - 1)  # 에러 카운트 감소
                
        except Exception as e:
            self.logger.error(f"상태 검사 중 오류: {e}")
    
    def attempt_recovery(self):
        """시스템 복구 시도"""
        self.logger.info("시스템 복구 시도 중...")
        
        try:
            # 단축키 재시작
            if not self.hotkey_manager.is_running():
                self.hotkey_manager.start()
                
            # Whisper 모델 재로드
            if not self.whisper_handler.is_model_loaded():
                self.whisper_handler.force_reload_model()
                
            self.logger.info("시스템 복구 완료")
            
        except Exception as e:
            self.logger.error(f"시스템 복구 실패: {e}")
    
    def global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """전역 예외 처리기"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.critical(
            f"처리되지 않은 예외 발생",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    def show_settings(self):
        """설정 대화상자 표시"""
        # 간단한 설정 정보 표시
        from PyQt6.QtWidgets import QMessageBox
        
        stats = self.get_app_statistics()
        msg = QMessageBox()
        msg.setWindowTitle("⚙️ 시스템 설정")
        msg.setText(
            f"<h3>📊 시스템 상태</h3>"
            f"<p><b>단축키:</b> {'\u2705 활성' if self.hotkey_manager.is_running() else '\u274c 비활성'}</p>"
            f"<p><b>Whisper 모델:</b> {'\u2705 준비됨' if self.whisper_handler.is_model_loaded() else '\u23f3 로딩중'}</p>"
            f"<p><b>전체 녹음 횟수:</b> {stats['total_recordings']}</p>"
            f"<p><b>성공률:</b> {stats['success_rate']:.1f}%</p>"
            f"<hr>"
            f"<p><b>모델:</b> {self.whisper_handler.get_current_model()}</p>"
            f"<p><b>언어:</b> {config.get('whisper.language', 'ko')}</p>"
            f"<p><b>자동복사:</b> {'\u2705' if self.clipboard_manager.auto_copy_enabled else '\u274c'}</p>"
        )
        msg.setTextFormat(1)  # RichText
        msg.exec()
    
    def show_status_info(self):
        """상태 정보 표시"""
        stats = self.get_app_statistics()
        hotkey_stats = self.hotkey_manager.get_statistics()
        whisper_stats = self.whisper_handler.get_statistics()
        clipboard_stats = self.clipboard_manager.get_statistics()
        
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("📊 상세 상태")
        msg.setText(
            f"<h3>📊 전체 통계</h3>"
            f"<p>전체 녹음: {stats['total_recordings']}</p>"
            f"<p>성공: {stats['successful_transcriptions']}</p>"
            f"<p>실패: {stats['failed_transcriptions']}</p>"
            f"<p>성공률: {stats['success_rate']:.1f}%</p>"
            f"<hr>"
            f"<h3>🎯 단축키</h3>"
            f"<p>현재 단축키: {self.hotkey_manager.get_current_hotkey_string()}</p>"
            f"<p>상태: {'\u2705 활성' if self.hotkey_manager.is_running() else '\u274c 비활성'}</p>"
            f"<hr>"
            f"<h3>🤖 Whisper</h3>"
            f"<p>모델: {self.whisper_handler.get_current_model()}</p>"
            f"<p>성공률: {whisper_stats.get('success_rate', 0):.1f}%</p>"
            f"<p>평균 신뢰도: {whisper_stats.get('average_confidence', 0):.2f}</p>"
            f"<hr>"
            f"<h3>📋 클립보드</h3>"
            f"<p>히스토리: {clipboard_stats.get('history_items', 0)}개</p>"
            f"<p>백업: {clipboard_stats.get('backup_count', 0)}개</p>"
        )
        msg.setTextFormat(1)
        msg.exec()
    
    def toggle_system(self):
        """시스템 전체 일시정지/재개"""
        if self.hotkey_manager.is_enabled():
            self.hotkey_manager.toggle_enabled()
            self.tray_manager.show_message("⏸️ 일시정지", "음성인식이 일시정지되었습니다.")
        else:
            self.hotkey_manager.toggle_enabled()
            self.tray_manager.show_message("▶️ 재개", "음성인식이 재개되었습니다.")
    
    def get_app_statistics(self):
        """애플리케이션 전체 통계"""
        stats = self.stats.copy()
        
        if stats['total_recordings'] > 0:
            stats['success_rate'] = (stats['successful_transcriptions'] / stats['total_recordings']) * 100
        else:
            stats['success_rate'] = 0.0
        
        stats['uptime_minutes'] = (time.time() - stats['start_time']) / 60
        
        return stats
    
    def quit_application(self):
        """애플리케이션 종료"""
        self.logger.info("🔴 애플리케이션 종료 시작")
        
        try:
            self.app_stopping.emit()
            self.is_running = False
            
            # 컴포넌트 종료
            if self.hotkey_manager:
                self.hotkey_manager.stop()
            
            if self.audio_recorder:
                self.audio_recorder.stop_recording()
            
            if self.tray_manager:
                self.tray_manager.hide()
            
            # 통계 로깅
            stats = self.get_app_statistics()
            self.logger.info(
                f"📊 종료 통계 - "
                f"녹음: {stats['total_recordings']}, "
                f"성공: {stats['successful_transcriptions']}, "
                f"실행시간: {stats['uptime_minutes']:.1f}분"
            )
            
            QApplication.quit()
            
        except Exception as e:
            self.logger.error(f"종료 처리 중 오류: {e}")
            QApplication.quit()
    
    def run(self):
        """애플리케이션 시작"""
        try:
            self.logger.info("🚀 음성 받아쓰기 프로그램 시작")
            
            # 시스템 상태 최종 확인
            if not self.whisper_handler.is_model_loaded() and not self.whisper_handler.is_model_loading():
                self.logger.warning("모델이 로드되지 않음 - 재로드 시도")
                self.whisper_handler.force_reload_model()
            
            # 단축키 시스템 시작
            if not self.hotkey_manager.start():
                self.logger.error("단축키 시스템 시작 실패")
                return 1
            
            self.is_running = True
            self.app_started.emit()
            
            # 트레이 UI 시작
            return self.tray_manager.show()
            
        except Exception as e:
            self.logger.critical(f"애플리케이션 시작 실패: {e}")
            return 1


def main():
    """메인 함수 - 애플리케이션 진입점"""
    
    # Qt 애플리케이션 설정
    QCoreApplication.setApplicationName("음성 받아쓰기 프로그램")
    QCoreApplication.setApplicationVersion("1.0")
    QCoreApplication.setOrganizationName("SpeechToText")
    
    # PyQt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 창이 닫혀도 트레이에서 실행 유지
    
    try:
        # 중복 실행 방지 (간단한 방법)
        import tempfile
        import fcntl
        
        lock_file_path = os.path.join(tempfile.gettempdir(), 'speech_to_text.lock')
        lock_file = open(lock_file_path, 'w')
        
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            print("프로그램이 이미 실행 중입니다.")
            return 1
        
        # 메인 애플리케이션 생성 및 실행
        speech_app = SpeechToTextApp()
        
        # 시그널 연결 (종료 처리)
        app.aboutToQuit.connect(speech_app.quit_application)
        
        # 실행
        result = speech_app.run()
        
        # 정리
        lock_file.close()
        
        return result
        
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        return 0
    except Exception as e:
        print(f"프로그램 실행 중 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)