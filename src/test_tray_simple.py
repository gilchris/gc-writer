#!/usr/bin/env python3
"""
간단한 트레이 매니저 기능 테스트 (GUI 없음)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_logging
setup_logging()

def test_tray_import():
    """트레이 매니저 임포트 테스트"""
    print("=== 트레이 매니저 임포트 테스트 ===")
    
    try:
        # PyQt6 임포트 테스트
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
        from PyQt6.QtCore import QObject, pyqtSignal, QTimer
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
        print("✅ PyQt6 모듈 임포트 성공")
        
        # TrayManager 임포트 테스트
        from tray_manager import TrayManager
        print("✅ TrayManager 클래스 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 실패: {e}")
        return False

def test_tray_class_structure():
    """트레이 매니저 클래스 구조 테스트"""
    print("\n=== 트레이 매니저 클래스 구조 테스트 ===")
    
    try:
        from tray_manager import TrayManager
        
        # 클래스 메서드 존재 확인
        required_methods = [
            'setup_icons',
            'setup_menu', 
            'setup_tray_icon',
            'set_status',
            'show_message',
            'on_tray_activated',
            'show_about',
            'update_tooltip',
            'on_toggle_requested',
            'get_status_info',
            'reset_session_stats'
        ]
        
        for method_name in required_methods:
            if hasattr(TrayManager, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 시그널 존재 확인
        required_signals = [
            'quit_requested',
            'settings_requested',
            'toggle_requested',
            'status_info_requested'
        ]
        
        # 임시 인스턴스 생성 없이 클래스 속성 확인
        tray_class = TrayManager
        for signal_name in required_signals:
            # 클래스 정의에서 시그널 확인
            if hasattr(tray_class, signal_name):
                print(f"✅ {signal_name} 시그널 정의됨")
            else:
                print(f"❌ {signal_name} 시그널 없음")
                return False
        
        print("✅ 클래스 구조 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 클래스 구조 테스트 실패: {e}")
        return False

def test_icon_creation():
    """아이콘 생성 기능 테스트"""
    print("\n=== 아이콘 생성 기능 테스트 ===")
    
    try:
        from PyQt6.QtGui import QColor
        from PyQt6.QtWidgets import QApplication
        
        # 최소한의 QApplication 생성 (GUI 없음)
        app = QApplication([])
        
        from tray_manager import TrayManager
        
        # 아이콘 생성 메서드 직접 테스트
        # 임시 TrayManager 인스턴스 생성 (시스템 트레이 확인 우회)
        import unittest.mock
        
        with unittest.mock.patch('tray_manager.QSystemTrayIcon.isSystemTrayAvailable', return_value=True):
            tray_manager = TrayManager()
            
            # 아이콘 생성 테스트
            test_colors = [
                (QColor(255, 0, 0), "빨간색"),
                (QColor(0, 255, 0), "초록색"),
                (QColor(0, 0, 255), "파란색"),
                (QColor(128, 128, 128), "회색")
            ]
            
            for color, color_name in test_colors:
                icon = tray_manager.create_microphone_icon(color, 22, False)
                if icon and not icon.isNull():
                    print(f"✅ {color_name} 마이크 아이콘 생성 성공")
                else:
                    print(f"❌ {color_name} 마이크 아이콘 생성 실패")
                    return False
            
            # 에러 아이콘 테스트
            error_icon = tray_manager.create_microphone_icon(QColor(255, 0, 0), 22, True)
            if error_icon and not error_icon.isNull():
                print("✅ 에러 표시 아이콘 생성 성공")
            else:
                print("❌ 에러 표시 아이콘 생성 실패")
                return False
        
        print("✅ 아이콘 생성 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 아이콘 생성 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_status_info():
    """상태 정보 기능 테스트"""
    print("\n=== 상태 정보 기능 테스트 ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        import unittest.mock
        
        app = QApplication([])
        
        with unittest.mock.patch('tray_manager.QSystemTrayIcon.isSystemTrayAvailable', return_value=True):
            from tray_manager import TrayManager
            tray_manager = TrayManager()
            
            # 초기 상태 정보 확인
            status_info = tray_manager.get_status_info()
            print(f"초기 상태: {status_info}")
            
            required_keys = ['current_status', 'is_paused', 'recording_count', 'animation_running']
            for key in required_keys:
                if key in status_info:
                    print(f"✅ {key} 정보 존재: {status_info[key]}")
                else:
                    print(f"❌ {key} 정보 없음")
                    return False
            
            # 상태 변경 시뮬레이션
            test_statuses = ['recording', 'processing', 'idle']
            for status in test_statuses:
                # 상태 변경 (실제 GUI 없이)
                tray_manager.current_status = status
                print(f"✅ {status} 상태로 변경됨")
            
            print("✅ 상태 정보 테스트 통과")
            return True
            
    except Exception as e:
        print(f"❌ 상태 정보 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_structure():
    """메뉴 구조 테스트"""
    print("\n=== 메뉴 구조 테스트 ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        import unittest.mock
        
        app = QApplication([])
        
        with unittest.mock.patch('tray_manager.QSystemTrayIcon.isSystemTrayAvailable', return_value=True):
            from tray_manager import TrayManager
            tray_manager = TrayManager()
            
            # 메뉴 존재 확인
            if hasattr(tray_manager, 'menu') and tray_manager.menu:
                print("✅ 컨텍스트 메뉴 생성됨")
                
                # 메뉴 액션들 확인
                required_actions = [
                    'status_action',
                    'count_action', 
                    'toggle_action',
                    'info_action',
                    'settings_action',
                    'about_action',
                    'quit_action'
                ]
                
                for action_name in required_actions:
                    if hasattr(tray_manager, action_name):
                        action = getattr(tray_manager, action_name)
                        if action:
                            print(f"✅ {action_name} 액션 존재: {action.text()}")
                        else:
                            print(f"❌ {action_name} 액션이 None")
                            return False
                    else:
                        print(f"❌ {action_name} 액션 없음")
                        return False
                
                print("✅ 메뉴 구조 테스트 통과")
                return True
            else:
                print("❌ 컨텍스트 메뉴 생성 실패")
                return False
                
    except Exception as e:
        print(f"❌ 메뉴 구조 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("시스템 트레이 기능 테스트 시작 (GUI 비활성화 모드)\n")
    
    # GUI 없이 실행하기 위한 환경 설정
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    test_results = []
    
    try:
        # 1. 임포트 테스트
        result1 = test_tray_import()
        test_results.append(("모듈 임포트", result1))
        
        if result1:
            # 2. 클래스 구조 테스트
            result2 = test_tray_class_structure()
            test_results.append(("클래스 구조", result2))
            
            # 3. 아이콘 생성 테스트
            result3 = test_icon_creation()
            test_results.append(("아이콘 생성", result3))
            
            # 4. 상태 정보 테스트
            result4 = test_status_info()
            test_results.append(("상태 정보", result4))
            
            # 5. 메뉴 구조 테스트
            result5 = test_menu_structure()
            test_results.append(("메뉴 구조", result5))
        
        # 결과 요약
        print("\n" + "="*50)
        print("시스템 트레이 기능 테스트 결과:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! 시스템 트레이 기능이 정상 구현되었습니다.")
            print("\n📝 주의사항:")
            print("- 실제 시스템 트레이 표시는 GUI 환경에서만 가능합니다")
            print("- 현재 테스트는 코드 구조와 기본 기능만 검증했습니다")
            print("- 실제 환경에서는 데스크톱 환경이 시스템 트레이를 지원해야 합니다")
        else:
            print("⚠️ 일부 테스트 실패. 코드 수정이 필요합니다.")
        
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()