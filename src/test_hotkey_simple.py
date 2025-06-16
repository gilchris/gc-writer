#!/usr/bin/env python3
"""
간단한 단축키 실제 감지 테스트
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from config import setup_logging
from hotkey_manager import HotkeyManager

def simple_hotkey_test():
    """간단한 단축키 감지 테스트"""
    print("=== 간단한 단축키 감지 테스트 ===")
    print("Ctrl+Alt+Space를 3번 눌러보세요 (10초 제한)")
    
    app = QApplication(sys.argv)
    hotkey_manager = HotkeyManager()
    
    test_count = 0
    max_tests = 3
    
    def on_start():
        nonlocal test_count
        test_count += 1
        print(f"✅ 감지됨! ({test_count}/{max_tests})")
        
        if test_count >= max_tests:
            print("🎉 테스트 완료!")
            QTimer.singleShot(1000, app.quit)
    
    def on_stop():
        print("   ⏹️ 해제됨")
    
    def timeout():
        print(f"⏰ 시간 초과 - {test_count}/{max_tests} 감지됨")
        app.quit()
    
    # 신호 연결
    hotkey_manager.recording_started.connect(on_start)
    hotkey_manager.recording_stopped.connect(on_stop)
    
    # 타임아웃 설정
    QTimer.singleShot(10000, timeout)
    
    # 시작
    if hotkey_manager.start():
        print("단축키 리스너 활성화됨")
        app.exec()
        hotkey_manager.stop()
        return test_count >= max_tests
    else:
        print("❌ 단축키 리스너 시작 실패")
        return False

if __name__ == "__main__":
    try:
        success = simple_hotkey_test()
        if success:
            print("\n🎉 단축키 감지 성공!")
        else:
            print("\n⚠️ 단축키 감지 불완전")
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")