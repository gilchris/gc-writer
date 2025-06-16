#!/usr/bin/env python3
"""
클립보드 관리 기능 테스트 스크립트
"""

import sys
import os
import time
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_logging
setup_logging()

def test_clipboard_import():
    """클립보드 관련 모듈 임포트 테스트"""
    print("=== 클립보드 모듈 임포트 테스트 ===")
    
    try:
        # 기본 모듈
        import pyperclip
        print("✅ pyperclip 모듈 임포트 성공")
        
        # ClipboardManager 임포트
        from clipboard_manager import ClipboardManager
        print("✅ ClipboardManager 클래스 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 실패: {e}")
        return False

def test_clipboard_class_structure():
    """ClipboardManager 클래스 구조 테스트"""
    print("\n=== ClipboardManager 클래스 구조 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        # 클래스 메서드 존재 확인
        required_methods = [
            'copy_text',
            'get_clipboard_content',
            'add_to_history',
            'get_history',
            'clear_history',
            'restore_previous_clipboard',
            'copy_from_history',
            'search_history',
            'get_statistics',
            'toggle_auto_copy',
            'toggle_history',
            'export_history',
            'import_history'
        ]
        
        for method_name in required_methods:
            if hasattr(ClipboardManager, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 시그널 존재 확인
        required_signals = [
            'text_copied',
            'clipboard_backup_created',
            'clipboard_restored',
            'history_updated',
            'copy_failed'
        ]
        
        for signal_name in required_signals:
            if hasattr(ClipboardManager, signal_name):
                print(f"✅ {signal_name} 시그널 정의됨")
            else:
                print(f"❌ {signal_name} 시그널 없음")
                return False
        
        print("✅ 클래스 구조 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 클래스 구조 테스트 실패: {e}")
        return False

def test_text_validation():
    """텍스트 검증 기능 테스트"""
    print("\n=== 텍스트 검증 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        
        # 테스트 케이스들
        test_cases = [
            ("", "빈 문자열"),
            ("   ", "공백만 있는 문자열"),
            ("정상 텍스트", "정상 텍스트"),
            ("x" * 100001, "너무 긴 텍스트"),
            ("안녕하세요\n여러줄\n텍스트", "여러줄 텍스트")
        ]
        
        for text, description in test_cases:
            result = clipboard_manager._validate_text(text)
            
            if description in ["빈 문자열", "공백만 있는 문자열", "너무 긴 텍스트"]:
                # 비정상 케이스는 invalid여야 함
                if not result['valid']:
                    print(f"✅ {description}: 검증 실패 감지됨 - {result['error']}")
                else:
                    print(f"❌ {description}: 예상치 못한 검증 통과")
                    return False
            else:
                # 정상 케이스는 valid여야 함
                if result['valid']:
                    print(f"✅ {description}: 검증 통과")
                else:
                    print(f"❌ {description}: 예상치 못한 검증 실패 - {result['error']}")
                    return False
        
        print("✅ 텍스트 검증 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 텍스트 검증 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_cleaning():
    """텍스트 정리 기능 테스트"""
    print("\n=== 텍스트 정리 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        
        # 테스트 케이스들
        test_cases = [
            ("  앞뒤 공백  ", "앞뒤 공백"),
            ("여러    공백    정리", "여러 공백 정리"),
            ("탭\t과\t공백\n정리", "탭과 공백 정리"),
            ("제어\x07문자\x08제거", "제어문자제거")
        ]
        
        for input_text, expected_pattern in test_cases:
            cleaned = clipboard_manager._clean_text(input_text)
            
            if expected_pattern == "앞뒤 공백":
                expected = "앞뒤 공백"
            elif expected_pattern == "여러 공백 정리":
                expected = "여러 공백 정리"
            elif expected_pattern == "탭과 공백 정리":
                expected = "탭과 공백 정리"
            elif expected_pattern == "제어문자제거":
                expected = "제어문자제거"
            
            if cleaned == expected:
                print(f"✅ {expected_pattern}: '{input_text}' -> '{cleaned}'")
            else:
                print(f"❌ {expected_pattern}: 예상 '{expected}', 실제 '{cleaned}'")
                return False
        
        print("✅ 텍스트 정리 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 텍스트 정리 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_copy():
    """기본 복사 기능 테스트"""
    print("\n=== 기본 복사 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        
        # 테스트 데이터
        test_texts = [
            "안녕하세요",
            "Hello World",
            "테스트 텍스트 123",
            "특수문자 !@#$%^&*()"
        ]
        
        for text in test_texts:
            # 복사 테스트
            result = clipboard_manager.copy_text(text, source="test")
            
            if result:
                print(f"✅ 복사 성공: '{text}'")
                
                # 클립보드에서 확인
                clipboard_content = clipboard_manager.get_clipboard_content()
                if clipboard_content == text:
                    print(f"✅ 클립보드 내용 확인: '{clipboard_content}'")
                else:
                    print(f"❌ 클립보드 내용 불일치: 예상 '{text}', 실제 '{clipboard_content}'")
                    return False
            else:
                print(f"❌ 복사 실패: '{text}'")
                return False
        
        print("✅ 기본 복사 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 기본 복사 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_history_management():
    """히스토리 관리 기능 테스트"""
    print("\n=== 히스토리 관리 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        clipboard_manager.clear_history()  # 초기화
        
        # 여러 텍스트 복사
        test_texts = ["첫번째", "두번째", "세번째", "네번째"]
        
        for text in test_texts:
            clipboard_manager.copy_text(text, source="test")
            time.sleep(0.01)  # 타임스탬프 구분을 위한 짧은 대기
        
        # 히스토리 확인
        history = clipboard_manager.get_history()
        print(f"히스토리 항목 수: {len(history)}")
        
        if len(history) != len(test_texts):
            print(f"❌ 히스토리 항목 수 불일치: 예상 {len(test_texts)}, 실제 {len(history)}")
            return False
        
        # 순서 확인 (최신이 먼저)
        for i, expected_text in enumerate(reversed(test_texts)):
            if history[i]['text'] != expected_text:
                print(f"❌ 히스토리 순서 불일치: 위치 {i}, 예상 '{expected_text}', 실제 '{history[i]['text']}'")
                return False
            print(f"✅ 히스토리 항목 {i}: '{history[i]['text']}'")
        
        # 검색 테스트
        search_results = clipboard_manager.search_history("번째")
        if len(search_results) == 4:  # 모든 항목이 "번째"를 포함
            print("✅ 히스토리 검색 성공")
        else:
            print(f"❌ 히스토리 검색 실패: 예상 4개, 실제 {len(search_results)}개")
            return False
        
        # 특정 항목 복사 테스트
        success = clipboard_manager.copy_from_history(1)  # 두번째 최신 항목
        if success:
            current_content = clipboard_manager.get_clipboard_content()
            expected_content = history[1]['text']
            if current_content == expected_content:
                print(f"✅ 히스토리에서 복사 성공: '{current_content}'")
            else:
                print(f"❌ 히스토리에서 복사 실패: 예상 '{expected_content}', 실제 '{current_content}'")
                return False
        else:
            print("❌ 히스토리에서 복사 실패")
            return False
        
        print("✅ 히스토리 관리 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 히스토리 관리 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_restore():
    """백업 및 복원 기능 테스트"""
    print("\n=== 백업 및 복원 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        
        # 초기 텍스트 설정
        initial_text = "초기 클립보드 내용"
        clipboard_manager.copy_text(initial_text, source="test")
        
        # 새 텍스트 복사 (백업 생성)
        new_text = "새로운 클립보드 내용"
        clipboard_manager.copy_text(new_text, source="test")
        
        # 현재 클립보드 확인
        current = clipboard_manager.get_clipboard_content()
        if current == new_text:
            print(f"✅ 새 텍스트 복사 확인: '{current}'")
        else:
            print(f"❌ 새 텍스트 복사 실패: 예상 '{new_text}', 실제 '{current}'")
            return False
        
        # 백업 히스토리 확인
        backup_history = clipboard_manager.get_backup_history()
        if len(backup_history) > 0:
            print(f"✅ 백업 생성 확인: {len(backup_history)}개 백업")
        else:
            print("❌ 백업이 생성되지 않음")
            return False
        
        # 백업에서 복원
        restore_success = clipboard_manager.restore_previous_clipboard(method="backup")
        if restore_success:
            restored = clipboard_manager.get_clipboard_content()
            if restored == initial_text:
                print(f"✅ 백업 복원 성공: '{restored}'")
            else:
                print(f"❌ 백업 복원 내용 불일치: 예상 '{initial_text}', 실제 '{restored}'")
                return False
        else:
            print("❌ 백업 복원 실패")
            return False
        
        print("✅ 백업 및 복원 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 백업 및 복원 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """통계 기능 테스트"""
    print("\n=== 통계 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        clipboard_manager.clear_history()  # 초기화
        
        # 여러 번 복사
        test_texts = ["통계1", "통계2", "통계3"]
        for text in test_texts:
            clipboard_manager.copy_text(text, source="test")
        
        # 통계 확인
        stats = clipboard_manager.get_statistics()
        print(f"통계 정보: {stats}")
        
        required_keys = [
            'total_copies', 'successful_copies', 'failed_copies',
            'total_characters', 'history_items', 'success_rate'
        ]
        
        for key in required_keys:
            if key in stats:
                print(f"✅ {key} 통계 존재: {stats[key]}")
            else:
                print(f"❌ {key} 통계 없음")
                return False
        
        # 기본 값 확인
        if stats['successful_copies'] >= len(test_texts):
            print("✅ 성공 복사 횟수 정상")
        else:
            print(f"❌ 성공 복사 횟수 이상: {stats['successful_copies']}")
            return False
        
        if stats['success_rate'] > 0:
            print(f"✅ 성공률 계산됨: {stats['success_rate']:.1f}%")
        else:
            print("❌ 성공률 계산 오류")
            return False
        
        print("✅ 통계 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 통계 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_import():
    """내보내기/가져오기 기능 테스트"""
    print("\n=== 내보내기/가져오기 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        clipboard_manager.clear_history()
        
        # 테스트 데이터 준비
        test_texts = ["내보내기1", "내보내기2", "내보내기3"]
        for text in test_texts:
            clipboard_manager.copy_text(text, source="test")
        
        # JSON 내보내기 테스트
        json_export = clipboard_manager.export_history(format="json")
        if json_export:
            print("✅ JSON 내보내기 성공")
            
            # JSON 파싱 확인
            try:
                parsed = json.loads(json_export)
                if len(parsed) == len(test_texts):
                    print(f"✅ JSON 내용 확인: {len(parsed)}개 항목")
                else:
                    print(f"❌ JSON 항목 수 불일치: 예상 {len(test_texts)}, 실제 {len(parsed)}")
                    return False
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
                return False
        else:
            print("❌ JSON 내보내기 실패")
            return False
        
        # 텍스트 내보내기 테스트
        txt_export = clipboard_manager.export_history(format="txt")
        if txt_export and len(txt_export.split('\n')) == len(test_texts):
            print("✅ 텍스트 내보내기 성공")
        else:
            print("❌ 텍스트 내보내기 실패")
            return False
        
        # 새 매니저로 가져오기 테스트
        new_manager = ClipboardManager()
        new_manager.clear_history()
        
        import_success = new_manager.import_history(json_export, format="json")
        if import_success:
            imported_history = new_manager.get_history()
            if len(imported_history) >= len(test_texts):
                print(f"✅ 가져오기 성공: {len(imported_history)}개 항목")
            else:
                print(f"❌ 가져오기 항목 수 부족: {len(imported_history)}")
                return False
        else:
            print("❌ 가져오기 실패")
            return False
        
        print("✅ 내보내기/가져오기 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 내보내기/가져오기 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_toggle_features():
    """토글 기능 테스트"""
    print("\n=== 토글 기능 테스트 ===")
    
    try:
        from clipboard_manager import ClipboardManager
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        clipboard_manager = ClipboardManager()
        
        # 자동 복사 토글 테스트
        initial_auto_copy = clipboard_manager.auto_copy_enabled
        toggled_auto_copy = clipboard_manager.toggle_auto_copy()
        
        if toggled_auto_copy != initial_auto_copy:
            print(f"✅ 자동 복사 토글 성공: {initial_auto_copy} -> {toggled_auto_copy}")
        else:
            print("❌ 자동 복사 토글 실패")
            return False
        
        # 히스토리 토글 테스트
        initial_history = clipboard_manager.history_enabled
        toggled_history = clipboard_manager.toggle_history()
        
        if toggled_history != initial_history:
            print(f"✅ 히스토리 토글 성공: {initial_history} -> {toggled_history}")
        else:
            print("❌ 히스토리 토글 실패")
            return False
        
        # 원래 상태로 복원
        if clipboard_manager.auto_copy_enabled != initial_auto_copy:
            clipboard_manager.toggle_auto_copy()
        if clipboard_manager.history_enabled != initial_history:
            clipboard_manager.toggle_history()
        
        print("✅ 토글 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 토글 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("클립보드 관리 기능 테스트 시작\n")
    
    test_results = []
    
    try:
        # 1. 모듈 임포트 테스트
        result1 = test_clipboard_import()
        test_results.append(("모듈 임포트", result1))
        
        if result1:
            # 2. 클래스 구조 테스트
            result2 = test_clipboard_class_structure()
            test_results.append(("클래스 구조", result2))
            
            # 3. 텍스트 검증 테스트
            result3 = test_text_validation()
            test_results.append(("텍스트 검증", result3))
            
            # 4. 텍스트 정리 테스트
            result4 = test_text_cleaning()
            test_results.append(("텍스트 정리", result4))
            
            # 5. 기본 복사 테스트
            result5 = test_basic_copy()
            test_results.append(("기본 복사", result5))
            
            # 6. 히스토리 관리 테스트
            result6 = test_history_management()
            test_results.append(("히스토리 관리", result6))
            
            # 7. 백업 복원 테스트
            result7 = test_backup_restore()
            test_results.append(("백업 복원", result7))
            
            # 8. 통계 기능 테스트
            result8 = test_statistics()
            test_results.append(("통계 기능", result8))
            
            # 9. 내보내기/가져오기 테스트
            result9 = test_export_import()
            test_results.append(("내보내기/가져오기", result9))
            
            # 10. 토글 기능 테스트
            result10 = test_toggle_features()
            test_results.append(("토글 기능", result10))
        
        # 결과 요약
        print("\n" + "="*50)
        print("클립보드 관리 기능 테스트 결과:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! 클립보드 관리 기능이 정상 구현되었습니다.")
            print("\n📝 주요 기능:")
            print("- 🔄 자동 클립보드 복사 및 백업")
            print("- 📚 스마트 히스토리 관리 (중복 제거, 검색)")
            print("- 🔒 텍스트 검증 및 정리")
            print("- 📊 상세 사용 통계")
            print("- 💾 히스토리 내보내기/가져오기")
            print("- ⚙️ 설정 토글 (자동복사, 히스토리)")
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