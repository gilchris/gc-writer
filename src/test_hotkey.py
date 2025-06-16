#!/usr/bin/env python3
"""
전역 단축키 기능 테스트 스크립트
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 설정 로드
from config import setup_logging
from hotkey_manager import HotkeyManager

def test_hotkey_basic():
    """기본 단축키 기능 테스트"""
    print("=== 기본 단축키 기능 테스트 ===")
    
    try:
        # HotkeyManager 인스턴스 생성
        hotkey_manager = HotkeyManager()
        print("✅ HotkeyManager 초기화 성공")
        
        # 상태 정보 출력
        status = hotkey_manager.get_status()
        print(f"OS 타입: {status['os_type']}")
        print(f"Wayland 감지: {status['wayland_detected']}")
        print(f"현재 단축키: {status['hotkey']}")
        print(f"활성화 상태: {status['enabled']}")
        
        return hotkey_manager
        
    except Exception as e:
        print(f"❌ HotkeyManager 초기화 실패: {e}")
        return None

def test_hotkey_changes(hotkey_manager):
    """단축키 변경 테스트"""
    print("\n=== 단축키 변경 테스트 ===")
    
    try:
        original_hotkey = hotkey_manager.get_current_hotkey_string()
        print(f"원본 단축키: {original_hotkey}")
        
        # 다른 조합으로 변경 테스트
        test_combinations = [
            ['ctrl', 'shift', 'space'],
            ['alt', 'f1'],
            ['ctrl', 'alt', 'r']
        ]
        
        for i, combo in enumerate(test_combinations, 1):
            print(f"\n{i}. {'+'.join(combo)} 조합으로 변경 테스트")
            
            success = hotkey_manager.change_hotkey(combo)
            if success:
                new_hotkey = hotkey_manager.get_current_hotkey_string()
                print(f"   ✅ 변경 성공: {new_hotkey}")
            else:
                print(f"   ❌ 변경 실패")
        
        # 원본으로 복원
        print(f"\n원본 단축키로 복원: {original_hotkey}")
        hotkey_manager.change_hotkey(['ctrl', 'alt', 'space'])
        
        return True
        
    except Exception as e:
        print(f"❌ 단축키 변경 테스트 실패: {e}")
        return False

def test_hotkey_detection():
    """실제 단축키 감지 테스트"""
    print("\n=== 실제 단축키 감지 테스트 ===")
    
    app = QApplication(sys.argv)
    hotkey_manager = HotkeyManager()
    
    # 테스트 상태
    test_state = {
        'detections': 0,
        'max_detections': 3,
        'test_running': True
    }
    
    def on_recording_started():
        test_state['detections'] += 1
        print(f"🔴 단축키 감지됨! ({test_state['detections']}/{test_state['max_detections']})")
        
        status = hotkey_manager.get_status()
        print(f"   현재 눌린 키: {status['currently_pressed']}")
    
    def on_recording_stopped():
        print("⏹️ 단축키 해제됨")
    
    def on_status_changed(status):
        print(f"📊 상태 변경: {status}")
    
    def on_error_occurred(error):
        print(f"❌ 오류 발생: {error}")
    
    def on_permission_required(message):
        print(f"⚠️ 권한 필요: {message}")
    
    def check_test_complete():
        if test_state['detections'] >= test_state['max_detections']:
            print("\n✅ 모든 테스트 완료!")
            app.quit()
        elif not test_state['test_running']:
            print("\n⏰ 테스트 시간 초과")
            app.quit()
    
    def timeout():
        test_state['test_running'] = False
        check_test_complete()
    
    # 신호 연결
    hotkey_manager.recording_started.connect(on_recording_started)
    hotkey_manager.recording_stopped.connect(on_recording_stopped)
    hotkey_manager.status_changed.connect(on_status_changed)
    hotkey_manager.error_occurred.connect(on_error_occurred)
    hotkey_manager.permission_required.connect(on_permission_required)
    
    # 감지 완료 체크 타이머
    detection_timer = QTimer()
    detection_timer.timeout.connect(check_test_complete)
    detection_timer.start(500)  # 500ms마다 체크
    
    # 타임아웃 타이머 (30초)
    timeout_timer = QTimer()
    timeout_timer.timeout.connect(timeout)
    timeout_timer.setSingleShot(True)
    timeout_timer.start(30000)
    
    # 단축키 리스너 시작
    print(f"단축키 리스너 시작 중... ({hotkey_manager.get_current_hotkey_string()})")
    
    if hotkey_manager.start():
        print("✅ 단축키 리스너 시작됨")
        print(f"Ctrl+Alt+Space를 {test_state['max_detections']}번 눌러보세요 (30초 제한)")
        
        # 상태 모니터링
        status_timer = QTimer()
        status_timer.timeout.connect(lambda: print_status(hotkey_manager))
        status_timer.start(5000)  # 5초마다 상태 출력
        
        # 앱 실행
        app.exec()
        
        # 정리
        hotkey_manager.stop()
        
        if test_state['detections'] >= test_state['max_detections']:
            print("\n🎉 단축키 감지 테스트 성공!")
            return True
        else:
            print(f"\n⚠️ 단축키 감지 불완전 ({test_state['detections']}/{test_state['max_detections']})")
            return False
    else:
        print("❌ 단축키 리스너 시작 실패")
        return False

def print_status(hotkey_manager):
    """상태 정보 출력"""
    status = hotkey_manager.get_status()
    stats = hotkey_manager.get_key_statistics()
    
    print(f"\n📊 상태 정보:")
    print(f"   실행 중: {status['running']}")
    print(f"   활성화: {status['enabled']}")
    print(f"   녹음 중: {status['is_recording']}")
    print(f"   에러 수: {status['error_count']}")
    
    if stats:
        print(f"   키 통계: {dict(list(stats.items())[:5])}")  # 상위 5개만

def test_hotkey_toggle():
    """단축키 활성화/비활성화 테스트"""
    print("\n=== 단축키 토글 테스트 ===")
    
    try:
        hotkey_manager = HotkeyManager()
        
        # 초기 상태
        initial_state = hotkey_manager.is_enabled()
        print(f"초기 활성화 상태: {initial_state}")
        
        # 토글 테스트
        for i in range(3):
            new_state = hotkey_manager.toggle_enabled()
            print(f"토글 {i+1}: {new_state}")
            time.sleep(0.5)
        
        # 원래 상태로 복원
        while hotkey_manager.is_enabled() != initial_state:
            hotkey_manager.toggle_enabled()
        
        print(f"최종 상태: {hotkey_manager.is_enabled()}")
        print("✅ 토글 테스트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 토글 테스트 실패: {e}")
        return False

def test_error_recovery():
    """에러 복구 테스트"""
    print("\n=== 에러 복구 테스트 ===")
    
    try:
        hotkey_manager = HotkeyManager()
        
        # 강제 에러 발생 (에러 카운트 증가)
        hotkey_manager.error_count = 5
        print(f"에러 카운트 설정: {hotkey_manager.error_count}")
        
        # 재시작 시도 카운트 설정
        hotkey_manager.restart_attempts = 1
        print(f"재시작 시도 횟수: {hotkey_manager.restart_attempts}")
        
        # 상태 확인
        status = hotkey_manager.get_status()
        print(f"복구 상태: 에러={status['error_count']}, 재시작={status['restart_attempts']}")
        
        # 통계 리셋 테스트
        hotkey_manager.reset_statistics()
        status_after_reset = hotkey_manager.get_status()
        print(f"리셋 후: 에러={status_after_reset['error_count']}, 재시작={status_after_reset['restart_attempts']}")
        
        if status_after_reset['error_count'] == 0 and status_after_reset['restart_attempts'] == 0:
            print("✅ 에러 복구 테스트 성공")
            return True
        else:
            print("❌ 에러 복구 테스트 실패")
            return False
        
    except Exception as e:
        print(f"❌ 에러 복구 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("전역 단축키 시스템 테스트 시작\n")
    
    test_results = []
    
    try:
        # 1. 기본 기능 테스트
        hotkey_manager = test_hotkey_basic()
        test_results.append(("기본 기능", hotkey_manager is not None))
        
        if hotkey_manager:
            # 2. 단축키 변경 테스트
            result2 = test_hotkey_changes(hotkey_manager)
            test_results.append(("단축키 변경", result2))
            
            # 3. 토글 테스트
            result3 = test_hotkey_toggle()
            test_results.append(("활성화/비활성화", result3))
            
            # 4. 에러 복구 테스트
            result4 = test_error_recovery()
            test_results.append(("에러 복구", result4))
        
        # 5. 실제 감지 테스트
        print("\n실제 단축키 감지 테스트를 진행하시겠습니까?")
        choice = input("Enter를 눌러 진행하거나 'n'을 입력하여 건너뛰기: ").lower()
        
        if choice != 'n':
            result5 = test_hotkey_detection()
            test_results.append(("단축키 감지", result5))
        else:
            print("실제 감지 테스트 건너뜀")
        
        # 결과 요약
        print("\n" + "="*50)
        print("전역 단축키 테스트 결과 요약:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! 전역 단축키 시스템이 정상 작동합니다.")
        else:
            print("⚠️ 일부 테스트 실패. 시스템 점검이 필요합니다.")
        
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()