#!/usr/bin/env python3
"""
시스템 트레이 기능 테스트 스크립트
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from config import setup_logging
from tray_manager import TrayManager

def test_tray_basic():
    """기본 트레이 기능 테스트"""
    print("=== 기본 트레이 기능 테스트 ===")
    
    try:
        app = QApplication(sys.argv)
        tray_manager = TrayManager()
        print("✅ TrayManager 초기화 성공")
        
        # 상태 정보 출력
        status_info = tray_manager.get_status_info()
        print(f"현재 상태: {status_info['current_status']}")
        print(f"일시정지: {status_info['is_paused']}")
        print(f"녹음 횟수: {status_info['recording_count']}")
        
        return tray_manager, app
        
    except Exception as e:
        print(f"❌ TrayManager 초기화 실패: {e}")
        return None, None

def test_tray_status_changes(tray_manager):
    """상태 변경 테스트"""
    print("\n=== 상태 변경 테스트 ===")
    
    try:
        test_statuses = [
            ('idle', '대기 상태'),
            ('recording', '녹음 상태'),
            ('processing', '처리 상태'),
            ('error', '에러 상태'),
            ('idle', '대기 상태로 복귀')
        ]
        
        for status, description in test_statuses:
            print(f"상태 변경: {description}")
            tray_manager.set_status(status, f"테스트: {description}")
            time.sleep(1)
        
        print("✅ 상태 변경 테스트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 상태 변경 테스트 실패: {e}")
        return False

def test_tray_toggle(tray_manager):
    """토글 기능 테스트"""
    print("\n=== 토글 기능 테스트 ===")
    
    try:
        # 초기 상태 확인
        initial_paused = tray_manager.is_paused
        print(f"초기 일시정지 상태: {initial_paused}")
        
        # 토글 테스트
        for i in range(3):
            tray_manager.on_toggle_requested()
            current_paused = tray_manager.is_paused
            print(f"토글 {i+1}: 일시정지 = {current_paused}")
            time.sleep(0.5)
        
        # 원래 상태로 복원
        while tray_manager.is_paused != initial_paused:
            tray_manager.on_toggle_requested()
        
        print(f"최종 상태: {tray_manager.is_paused}")
        print("✅ 토글 기능 테스트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 토글 기능 테스트 실패: {e}")
        return False

def test_tray_notifications(tray_manager):
    """알림 기능 테스트"""
    print("\n=== 알림 기능 테스트 ===")
    
    try:
        from PyQt6.QtWidgets import QSystemTrayIcon
        
        test_messages = [
            ("정보", "정보 메시지 테스트", QSystemTrayIcon.MessageIcon.Information),
            ("경고", "경고 메시지 테스트", QSystemTrayIcon.MessageIcon.Warning),
            ("에러", "에러 메시지 테스트", QSystemTrayIcon.MessageIcon.Critical)
        ]
        
        for title, message, icon in test_messages:
            print(f"알림 표시: {title}")
            tray_manager.show_message(title, message, icon, 2000)
            time.sleep(1)
        
        print("✅ 알림 기능 테스트 성공")
        return True
        
    except Exception as e:
        print(f"❌ 알림 기능 테스트 실패: {e}")
        return False

def test_tray_statistics(tray_manager):
    """통계 기능 테스트"""
    print("\n=== 통계 기능 테스트 ===")
    
    try:
        # 초기 통계
        initial_count = tray_manager.recording_count
        print(f"초기 녹음 횟수: {initial_count}")
        
        # 가상 녹음 시뮬레이션
        for i in range(5):
            tray_manager.set_status('recording', f"가상 녹음 {i+1}")
            time.sleep(0.2)
            tray_manager.set_status('processing', f"가상 처리 {i+1}")
            time.sleep(0.2)
            tray_manager.set_status('idle', f"완료 {i+1}")
            time.sleep(0.1)
        
        final_count = tray_manager.recording_count
        expected_count = initial_count + 5
        
        print(f"최종 녹음 횟수: {final_count}")
        print(f"예상 녹음 횟수: {expected_count}")
        
        if final_count == expected_count:
            print("✅ 통계 기능 테스트 성공")
            return True
        else:
            print("❌ 통계 카운트 불일치")
            return False
        
    except Exception as e:
        print(f"❌ 통계 기능 테스트 실패: {e}")
        return False

def test_tray_interactive():
    """인터랙티브 트레이 테스트"""
    print("\n=== 인터랙티브 트레이 테스트 ===")
    print("시스템 트레이에서 아이콘을 확인하고 메뉴를 테스트해보세요.")
    print("- 우클릭: 컨텍스트 메뉴")
    print("- 더블클릭: 일시정지/재개")
    print("- 중간클릭: 상태 정보")
    print("10초 후 자동 종료됩니다...")
    
    app = QApplication(sys.argv)
    tray_manager = TrayManager()
    
    # 테스트 상태 시뮬레이션
    states = ['idle', 'recording', 'processing', 'error', 'idle']
    state_index = 0
    
    def cycle_states():
        nonlocal state_index
        status = states[state_index]
        tray_manager.set_status(status, f"자동 테스트: {status}")
        state_index = (state_index + 1) % len(states)
    
    # 신호 연결
    def on_quit():
        print("종료 요청됨")
        app.quit()
    
    def on_settings():
        print("설정 요청됨")
    
    def on_toggle():
        print("토글 요청됨")
    
    def on_status_info():
        status_info = tray_manager.get_status_info()
        print(f"상태 정보 요청: {status_info}")
    
    tray_manager.quit_requested.connect(on_quit)
    tray_manager.settings_requested.connect(on_settings)
    tray_manager.toggle_requested.connect(on_toggle)
    tray_manager.status_info_requested.connect(on_status_info)
    
    # 상태 변경 타이머
    state_timer = QTimer()
    state_timer.timeout.connect(cycle_states)
    state_timer.start(2000)  # 2초마다 상태 변경
    
    # 자동 종료 타이머
    exit_timer = QTimer()
    exit_timer.timeout.connect(app.quit)
    exit_timer.setSingleShot(True)
    exit_timer.start(10000)  # 10초 후 종료
    
    # 트레이 표시
    if tray_manager.show():
        return True
    else:
        print("❌ 트레이 표시 실패")
        return False

def main():
    """메인 테스트 함수"""
    print("시스템 트레이 테스트 시작\n")
    
    test_results = []
    
    try:
        # 1. 기본 기능 테스트
        tray_manager, app = test_tray_basic()
        test_results.append(("기본 기능", tray_manager is not None))
        
        if tray_manager:
            # 2. 상태 변경 테스트
            result2 = test_tray_status_changes(tray_manager)
            test_results.append(("상태 변경", result2))
            
            # 3. 토글 기능 테스트
            result3 = test_tray_toggle(tray_manager)
            test_results.append(("토글 기능", result3))
            
            # 4. 알림 기능 테스트
            result4 = test_tray_notifications(tray_manager)
            test_results.append(("알림 기능", result4))
            
            # 5. 통계 기능 테스트
            result5 = test_tray_statistics(tray_manager)
            test_results.append(("통계 기능", result5))
        
        # 6. 인터랙티브 테스트
        print("\n인터랙티브 테스트를 진행하시겠습니까?")
        choice = input("Enter를 눌러 진행하거나 'n'을 입력하여 건너뛰기: ").lower()
        
        if choice != 'n':
            result6 = test_tray_interactive()
            test_results.append(("인터랙티브", result6))
        else:
            print("인터랙티브 테스트 건너뜀")
        
        # 결과 요약
        print("\n" + "="*50)
        print("시스템 트레이 테스트 결과 요약:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! 시스템 트레이가 정상 작동합니다.")
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