"""
고급 전역 단축키 관리 모듈
"""

import logging
import time
import platform
import os
from collections import defaultdict
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from pynput import keyboard
import threading
from config import config


class HotkeyManager(QObject):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    hotkey_changed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    permission_required = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 설정에서 단축키 로드
        hotkey_config = config.get('hotkey.combination', ['ctrl', 'alt', 'space'])
        self.hotkey_combination = self._parse_hotkey_config(hotkey_config)
        self.hotkey_enabled = config.get('hotkey.enabled', True)
        
        # 키 상태 관리
        self.currently_pressed = set()
        self.is_recording = False
        self.last_key_event_time = 0
        
        # 키보드 리스너
        self.listener = None
        self.running = False
        self.restart_attempts = 0
        self.max_restart_attempts = 3
        
        # 디바운싱 및 성능 최적화
        self.debounce_time = 0.05  # 50ms
        self.key_repeat_threshold = 0.1  # 100ms
        self.last_hotkey_trigger = 0
        
        # OS 특정 설정
        self.os_type = platform.system().lower()
        self.wayland_detected = self._detect_wayland()
        
        # 에러 복구 타이머
        self.recovery_timer = QTimer()
        self.recovery_timer.timeout.connect(self._attempt_recovery)
        self.recovery_timer.setSingleShot(True)
        
        # 키 통계 (디버깅용)
        self.key_stats = defaultdict(int)
        self.error_count = 0
    
    def _parse_hotkey_config(self, hotkey_config):
        """설정에서 단축키 조합 파싱"""
        combination = set()
        key_mapping = {
            'ctrl': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
            'cmd': keyboard.Key.cmd,
            'space': keyboard.Key.space,
            'enter': keyboard.Key.enter,
            'tab': keyboard.Key.tab,
            'esc': keyboard.Key.esc
        }
        
        for key_name in hotkey_config:
            key_name = key_name.lower()
            if key_name in key_mapping:
                combination.add(key_mapping[key_name])
            elif len(key_name) == 1:
                # 단일 문자 키
                combination.add(keyboard.KeyCode.from_char(key_name))
        
        return combination
    
    def _detect_wayland(self):
        """Wayland 환경 감지"""
        if self.os_type != 'linux':
            return False
        
        wayland_indicators = [
            os.environ.get('WAYLAND_DISPLAY'),
            os.environ.get('XDG_SESSION_TYPE') == 'wayland',
            'wayland' in os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        ]
        
        return any(wayland_indicators)
    
    def _check_permissions(self):
        """OS별 권한 확인"""
        if self.os_type == 'linux':
            if self.wayland_detected:
                self.logger.warning("Wayland 환경에서는 전역 단축키가 제한될 수 있습니다")
                return False
            
            # X11 환경에서의 권한 확인
            try:
                import subprocess
                result = subprocess.run(['xhost'], capture_output=True, text=True, timeout=2)
                if result.returncode != 0:
                    self.logger.warning("X11 권한 확인 실패")
                    return False
            except:
                pass  # xhost 명령이 없으면 무시
                
        return True
    
    def start(self):
        """향상된 단축키 리스너 시작"""
        if self.running:
            self.logger.warning("단축키 리스너가 이미 실행 중입니다")
            return False
        
        if not self.hotkey_enabled:
            self.logger.info("단축키가 비활성화되어 있습니다")
            return False
        
        # 권한 확인
        if not self._check_permissions():
            error_msg = "단축키 사용을 위한 권한이 부족합니다"
            self.logger.error(error_msg)
            self.permission_required.emit(error_msg)
            return False
        
        try:
            self.running = True
            self.restart_attempts = 0
            self.error_count = 0
            
            # 리스너 생성 및 시작
            self.listener = keyboard.Listener(
                on_press=self._safe_on_key_press,
                on_release=self._safe_on_key_release,
                suppress=False  # 다른 애플리케이션의 키 입력 방해하지 않음
            )
            
            self.listener.start()
            
            # 상태 업데이트
            hotkey_str = self._combination_to_string(self.hotkey_combination)
            status_msg = f"단축키 리스너 시작됨 ({hotkey_str})"
            self.logger.info(status_msg)
            self.status_changed.emit("active")
            
            return True
            
        except Exception as e:
            error_msg = f"단축키 리스너 시작 실패: {e}"
            self.logger.error(error_msg)
            self.running = False
            self.error_occurred.emit(error_msg)
            
            # 자동 복구 시도
            if self.restart_attempts < self.max_restart_attempts:
                self.logger.info(f"3초 후 자동 복구 시도 ({self.restart_attempts + 1}/{self.max_restart_attempts})")
                self.recovery_timer.start(3000)
            
            return False
    
    def stop(self):
        """단축키 리스너 중지"""
        if not self.running:
            return
        
        try:
            self.running = False
            self.recovery_timer.stop()
            
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            # 상태 초기화
            self.currently_pressed.clear()
            self.is_recording = False
            
            self.logger.info("단축키 리스너 중지됨")
            self.status_changed.emit("inactive")
            
        except Exception as e:
            self.logger.error(f"단축키 리스너 중지 실패: {e}")
    
    def _attempt_recovery(self):
        """자동 복구 시도"""
        self.restart_attempts += 1
        self.logger.info(f"단축키 리스너 자동 복구 시도 {self.restart_attempts}")
        
        # 이전 리스너 정리
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
            self.listener = None
        
        # 재시작 시도
        success = self.start()
        if not success and self.restart_attempts < self.max_restart_attempts:
            # 실패시 더 긴 간격으로 재시도
            retry_delay = min(10000, 3000 * self.restart_attempts)  # 최대 10초
            self.logger.info(f"{retry_delay/1000}초 후 다시 시도...")
            self.recovery_timer.start(retry_delay)
    
    def _safe_on_key_press(self, key):
        """안전한 키 눌림 이벤트 처리"""
        try:
            self.on_key_press(key)
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"키 눌림 처리 오류: {e}")
            
            # 너무 많은 에러 발생시 리스너 재시작
            if self.error_count > 10:
                self.logger.warning("키 이벤트 에러가 너무 많아 리스너를 재시작합니다")
                self._restart_listener()
    
    def _safe_on_key_release(self, key):
        """안전한 키 놓음 이벤트 처리"""
        try:
            self.on_key_release(key)
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"키 놓음 처리 오류: {e}")
            
            if self.error_count > 10:
                self.logger.warning("키 이벤트 에러가 너무 많아 리스너를 재시작합니다")
                self._restart_listener()
    
    def _restart_listener(self):
        """리스너 재시작"""
        self.stop()
        self.error_count = 0
        self.recovery_timer.start(1000)  # 1초 후 재시작
    
    def on_key_press(self, key):
        """향상된 키 눌림 이벤트 처리"""
        current_time = time.time()
        
        # 디바운싱 - 너무 빠른 키 반복 무시
        if current_time - self.last_key_event_time < self.debounce_time:
            return
        
        self.last_key_event_time = current_time
        
        # 키 통계 업데이트
        key_str = self._key_to_string(key)
        self.key_stats[key_str] += 1
        
        # 특수키 정규화
        normalized_key = self._normalize_key(key)
        
        # 현재 눌린 키 목록에 추가
        self.currently_pressed.add(normalized_key)
        
        # 단축키 조합 확인
        if self._is_hotkey_active():
            if not self.is_recording:
                # 중복 트리거 방지
                if current_time - self.last_hotkey_trigger < self.key_repeat_threshold:
                    return
                
                self.last_hotkey_trigger = current_time
                self.is_recording = True
                
                self.logger.debug(f"단축키 활성화: {self._combination_to_string(self.currently_pressed)}")
                self.recording_started.emit()
    
    def on_key_release(self, key):
        """향상된 키 놓음 이벤트 처리"""
        current_time = time.time()
        
        # 디바운싱
        if current_time - self.last_key_event_time < self.debounce_time:
            return
        
        self.last_key_event_time = current_time
        
        # 특수키 정규화
        normalized_key = self._normalize_key(key)
        
        # 눌린 키 목록에서 제거
        self.currently_pressed.discard(normalized_key)
        
        # 단축키 조합이 더 이상 활성화되지 않으면 녹음 중지
        if self.is_recording and not self._is_hotkey_active():
            self.is_recording = False
            self.logger.debug("단축키 비활성화 - 녹음 중지")
            self.recording_stopped.emit()
    
    def _normalize_key(self, key):
        """키 정규화 (좌/우 구분자 제거)"""
        if hasattr(key, 'name'):
            name = key.name.lower()
            # 좌우 구분자 제거
            if name.startswith('ctrl'):
                return keyboard.Key.ctrl
            elif name.startswith('alt'):
                return keyboard.Key.alt
            elif name.startswith('shift'):
                return keyboard.Key.shift
            elif name.startswith('cmd'):
                return keyboard.Key.cmd
        
        return key
    
    def _is_hotkey_active(self):
        """현재 단축키 조합이 활성화되었는지 확인"""
        if not self.hotkey_enabled:
            return False
        
        return self.hotkey_combination.issubset(self.currently_pressed)
    
    def _key_to_string(self, key):
        """키를 문자열로 변환 (개선된 버전)"""
        if hasattr(key, 'char') and key.char:
            return key.char.upper()
        elif hasattr(key, 'name'):
            name = key.name.replace('_', ' ').title()
            # 특수키 이름 정리
            if name.startswith('Ctrl'):
                return 'Ctrl'
            elif name.startswith('Alt'):
                return 'Alt'
            elif name.startswith('Shift'):
                return 'Shift'
            elif name.startswith('Cmd'):
                return 'Cmd'
            return name
        else:
            return str(key)
    
    def _combination_to_string(self, combination):
        """키 조합을 문자열로 변환 (개선된 버전)"""
        if not combination:
            return "없음"
        
        key_names = [self._key_to_string(key) for key in combination]
        # 특수키 순서 정렬 (Ctrl, Alt, Shift, 기타)
        special_order = ['Ctrl', 'Alt', 'Shift', 'Cmd']
        special_keys = [k for k in key_names if k in special_order]
        other_keys = [k for k in key_names if k not in special_order]
        
        # 정렬된 순서로 결합
        ordered_keys = []
        for special in special_order:
            if special in special_keys:
                ordered_keys.append(special)
        ordered_keys.extend(sorted(other_keys))
        
        return '+'.join(ordered_keys)
    
    def change_hotkey(self, new_combination):
        """단축키 조합 변경"""
        try:
            old_combination_str = self._combination_to_string(self.hotkey_combination)
            
            # 문자열 배열이면 파싱
            if isinstance(new_combination, list) and all(isinstance(x, str) for x in new_combination):
                new_combination = self._parse_hotkey_config(new_combination)
            elif isinstance(new_combination, (list, set)):
                new_combination = set(new_combination)
            else:
                raise ValueError("잘못된 단축키 형식입니다")
            
            # 유효성 검사
            if len(new_combination) == 0:
                raise ValueError("빈 단축키 조합은 설정할 수 없습니다")
            
            if len(new_combination) > 4:
                raise ValueError("단축키 조합은 최대 4개 키까지 지원됩니다")
            
            # 이전 상태 저장
            was_running = self.running
            
            # 리스너 중지
            if was_running:
                self.stop()
            
            # 새 조합 설정
            self.hotkey_combination = new_combination
            self.currently_pressed.clear()
            self.is_recording = False
            
            # 설정에 저장
            config_keys = []
            for key in new_combination:
                if key == keyboard.Key.ctrl:
                    config_keys.append('ctrl')
                elif key == keyboard.Key.alt:
                    config_keys.append('alt')
                elif key == keyboard.Key.shift:
                    config_keys.append('shift')
                elif key == keyboard.Key.space:
                    config_keys.append('space')
                elif hasattr(key, 'char') and key.char:
                    config_keys.append(key.char.lower())
            
            config.set('hotkey.combination', config_keys)
            config.save_settings()
            
            new_combination_str = self._combination_to_string(self.hotkey_combination)
            self.logger.info(f"단축키 변경: {old_combination_str} -> {new_combination_str}")
            self.hotkey_changed.emit(new_combination_str)
            
            # 리스너 재시작
            if was_running:
                self.start()
            
            return True
            
        except Exception as e:
            error_msg = f"단축키 변경 실패: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def toggle_enabled(self):
        """단축키 활성화/비활성화 토글"""
        self.hotkey_enabled = not self.hotkey_enabled
        config.set('hotkey.enabled', self.hotkey_enabled)
        config.save_settings()
        
        status = "활성화" if self.hotkey_enabled else "비활성화"
        self.logger.info(f"단축키 {status}")
        
        if self.hotkey_enabled and not self.running:
            self.start()
        elif not self.hotkey_enabled and self.running:
            self.stop()
        
        return self.hotkey_enabled
    
    def get_current_hotkey(self):
        """현재 단축키 조합 반환"""
        return self.hotkey_combination.copy()
    
    def get_current_hotkey_string(self):
        """현재 단축키를 문자열로 반환"""
        return self._combination_to_string(self.hotkey_combination)
    
    def is_running(self):
        """리스너 실행 상태 확인"""
        return self.running and self.listener is not None
    
    def is_enabled(self):
        """단축키 활성화 상태 확인"""
        return self.hotkey_enabled
    
    def get_status(self):
        """상세 상태 정보 반환"""
        return {
            'running': self.running,
            'enabled': self.hotkey_enabled,
            'hotkey': self.get_current_hotkey_string(),
            'is_recording': self.is_recording,
            'currently_pressed': self._combination_to_string(self.currently_pressed),
            'error_count': self.error_count,
            'restart_attempts': self.restart_attempts,
            'os_type': self.os_type,
            'wayland_detected': self.wayland_detected
        }
    
    def get_key_statistics(self):
        """키 통계 반환"""
        return dict(self.key_stats)
    
    def reset_statistics(self):
        """통계 초기화"""
        self.key_stats.clear()
        self.error_count = 0
        self.restart_attempts = 0
        self.logger.info("키 통계가 초기화되었습니다")
    
    def test_hotkey_detection(self):
        """단축키 감지 테스트"""
        if not self.running:
            return False, "리스너가 실행되지 않았습니다"
        
        # 현재 눌린 키와 설정된 단축키 비교
        if self._is_hotkey_active():
            return True, f"단축키 감지됨: {self._combination_to_string(self.currently_pressed)}"
        else:
            pressed_str = self._combination_to_string(self.currently_pressed) or "없음"
            expected_str = self._combination_to_string(self.hotkey_combination)
            return False, f"현재 눌린 키: {pressed_str}, 필요한 키: {expected_str}"
    
    def force_stop_recording(self):
        """강제로 녹음 중지"""
        if self.is_recording:
            self.is_recording = False
            self.currently_pressed.clear()
            self.logger.info("녹음이 강제로 중지되었습니다")
            self.recording_stopped.emit()
    
    def __del__(self):
        """소멸자 - 리스너 정리"""
        try:
            self.stop()
        except:
            pass