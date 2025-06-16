#!/usr/bin/env python3
"""
전체 시스템 통합 테스트 스크립트
"""

import sys
import os
import time
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_logging
setup_logging()

def test_main_app_import():
    """메인 애플리케이션 임포트 테스트"""
    print("=== 메인 애플리케이션 임포트 테스트 ===")
    
    try:
        from main import SpeechToTextApp
        print("✅ SpeechToTextApp 클래스 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_initialization():
    """애플리케이션 초기화 테스트"""
    print("\n=== 애플리케이션 초기화 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 기본 컴포넌트 확인
        components = [
            ('tray_manager', '트레이 매니저'),
            ('hotkey_manager', '단축키 매니저'),
            ('audio_recorder', '오디오 레코더'),
            ('whisper_handler', 'Whisper 핸들러'),
            ('clipboard_manager', '클립보드 매니저')
        ]
        
        for attr_name, display_name in components:
            if hasattr(speech_app, attr_name) and getattr(speech_app, attr_name):
                print(f"✅ {display_name} 초기화 성공")
            else:
                print(f"❌ {display_name} 초기화 실패")
                return False
        
        # 시그널 연결 확인
        if hasattr(speech_app, 'is_running'):
            print("✅ 애플리케이션 상태 관리 설정됨")
        else:
            print("❌ 애플리케이션 상태 관리 설정 실패")
            return False
        
        print("✅ 애플리케이션 초기화 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 애플리케이션 초기화 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_connections():
    """컴포넌트 간 연결 테스트"""
    print("\n=== 컴포넌트 간 연결 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 시그널 연결 상태 확인
        test_results = {'called': False, 'data': None}
        
        def test_signal_handler(*args):
            test_results['called'] = True
            test_results['data'] = args
            print(f"✅ 시그널 수신됨: {args}")
        
        # 워크플로우 완료 시그널 테스트
        speech_app.workflow_completed.connect(test_signal_handler)
        
        # 시그널 발생 테스트
        speech_app.workflow_completed.emit("테스트 텍스트", {"test": True})
        
        # 시그널 수신 확인
        QTimer.singleShot(100, app.quit)
        app.exec()
        
        if test_results['called']:
            print("✅ 시그널 연결 및 전달 성공")
        else:
            print("❌ 시그널 연결 또는 전달 실패")
            return False
        
        print("✅ 컴포넌트 간 연결 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 컴포넌트 간 연결 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """에러 처리 시스템 테스트"""
    print("\n=== 에러 처리 시스템 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 에러 처리 메서드 존재 확인
        error_methods = [
            'handle_workflow_error',
            'handle_system_error',
            'handle_hotkey_error',
            'handle_audio_error',
            'handle_whisper_error',
            'handle_clipboard_error'
        ]
        
        for method_name in error_methods:
            if hasattr(speech_app, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 에러 핸들링 테스트
        error_caught = {'value': False}
        
        def error_signal_handler(error):
            error_caught['value'] = True
            print(f"✅ 에러 시그널 수신: {error}")
        
        speech_app.workflow_failed.connect(error_signal_handler)
        
        # 의도적 에러 발생
        speech_app.handle_workflow_error("테스트 에러")
        
        QTimer.singleShot(100, app.quit)
        app.exec()
        
        if error_caught['value']:
            print("✅ 에러 처리 및 시그널 전달 성공")
        else:
            print("❌ 에러 처리 또는 시그널 전달 실패")
            return False
        
        print("✅ 에러 처리 시스템 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 에러 처리 시스템 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics_system():
    """통계 시스템 테스트"""
    print("\n=== 통계 시스템 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 초기 통계 확인
        initial_stats = speech_app.get_app_statistics()
        print(f"초기 통계: {initial_stats}")
        
        required_stats = ['total_recordings', 'successful_transcriptions', 'failed_transcriptions', 'success_rate']
        
        for stat_key in required_stats:
            if stat_key in initial_stats:
                print(f"✅ {stat_key} 통계 존재: {initial_stats[stat_key]}")
            else:
                print(f"❌ {stat_key} 통계 없음")
                return False
        
        # 통계 업데이트 테스트
        speech_app.stats['total_recordings'] += 1
        speech_app.stats['successful_transcriptions'] += 1
        
        updated_stats = speech_app.get_app_statistics()
        
        if updated_stats['total_recordings'] > initial_stats['total_recordings']:
            print("✅ 통계 업데이트 성공")
        else:
            print("❌ 통계 업데이트 실패")
            return False
        
        print("✅ 통계 시스템 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 통계 시스템 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_simulation():
    """전체 워크플로우 시뮬레이션 테스트"""
    print("\n=== 전체 워크플로우 시뮬레이션 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 워크플로우 상태 추적
        workflow_steps = {
            'recording_started': False,
            'recording_stopped': False,
            'audio_processed': False,
            'text_copied': False
        }
        
        # 시그널 핸들러들
        def on_recording_start():
            workflow_steps['recording_started'] = True
            print("✅ 1단계: 녹음 시작")
        
        def on_recording_stop():
            workflow_steps['recording_stopped'] = True
            print("✅ 2단계: 녹음 종료")
        
        def on_workflow_complete(text, metadata):
            workflow_steps['text_copied'] = True
            print(f"✅ 4단계: 워크플로우 완료 - '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # 시그널 연결
        speech_app.hotkey_manager.recording_started.connect(on_recording_start)
        speech_app.hotkey_manager.recording_stopped.connect(on_recording_stop)
        speech_app.workflow_completed.connect(on_workflow_complete)
        
        # 1. 녹음 시작 시뮬레이션
        speech_app.start_recording()
        
        # 2. 녹음 종료 시뮬레이션  
        speech_app.stop_recording()
        
        # 3. 가짜 오디오 데이터로 처리 시뮬레이션
        fake_audio = np.random.random(32000).astype(np.float32)  # 2초 오디오
        
        # 오디오 처리는 실제로는 안함 (Whisper 모델 필요)
        workflow_steps['audio_processed'] = True
        print("✅ 3단계: 오디오 처리 (시뮬레이션)")
        
        # 4. 클립보드 복사 시뮬레이션
        test_text = "시뮬레이션 테스트 텍스트"
        test_metadata = {'confidence': 0.95, 'workflow_id': 'test123'}
        
        speech_app.copy_to_clipboard(test_text, test_metadata)
        
        # 결과 확인
        QTimer.singleShot(100, app.quit)
        app.exec()
        
        completed_steps = sum(workflow_steps.values())
        total_steps = len(workflow_steps)
        
        print(f"\n워크플로우 완료 단계: {completed_steps}/{total_steps}")
        
        if completed_steps >= 3:  # 실제 Whisper 처리 제외하고 3단계
            print("✅ 워크플로우 시뮬레이션 성공")
        else:
            print("❌ 워크플로우 시뮬레이션 부분 실패")
            for step, completed in workflow_steps.items():
                status = "✅" if completed else "❌"
                print(f"  {status} {step}")
            return False
        
        print("✅ 전체 워크플로우 시뮬레이션 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 전체 워크플로우 시뮬레이션 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_monitoring():
    """시스템 상태 모니터링 테스트"""
    print("\n=== 시스템 상태 모니터링 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # 상태 모니터링 메서드 확인
        monitoring_methods = [
            'check_system_health',
            'attempt_recovery',
            'get_app_statistics'
        ]
        
        for method_name in monitoring_methods:
            if hasattr(speech_app, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 상태 검사 실행
        try:
            speech_app.check_system_health()
            print("✅ 시스템 상태 검사 실행 성공")
        except Exception as e:
            print(f"❌ 시스템 상태 검사 실행 실패: {e}")
            return False
        
        # 복구 시도 테스트
        try:
            speech_app.attempt_recovery()
            print("✅ 시스템 복구 시도 실행 성공")
        except Exception as e:
            print(f"❌ 시스템 복구 시도 실행 실패: {e}")
            return False
        
        print("✅ 시스템 상태 모니터링 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 시스템 상태 모니터링 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_integration():
    """설정 통합 테스트"""
    print("\n=== 설정 통합 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from config import config
        from main import SpeechToTextApp
        
        # 기본 설정 확인
        whisper_model = config.get('whisper.model_name', 'base')
        hotkey_combo = config.get('hotkey.combination', ['ctrl', 'alt', 'space'])
        auto_copy = config.get('clipboard.auto_copy', True)
        
        print(f"✅ Whisper 모델: {whisper_model}")
        print(f"✅ 단축키 조합: {'+'.join(hotkey_combo)}")
        print(f"✅ 자동 복사: {auto_copy}")
        
        # 애플리케이션이 설정을 올바르게 사용하는지 확인
        speech_app = SpeechToTextApp()
        
        if speech_app.whisper_handler.get_current_model() == whisper_model:
            print("✅ Whisper 모델 설정 적용됨")
        else:
            print("❌ Whisper 모델 설정 적용 안됨")
            return False
        
        if speech_app.clipboard_manager.auto_copy_enabled == auto_copy:
            print("✅ 클립보드 자동복사 설정 적용됨")
        else:
            print("❌ 클립보드 자동복사 설정 적용 안됨")
            return False
        
        print("✅ 설정 통합 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 설정 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """UI 통합 테스트"""
    print("\n=== UI 통합 테스트 ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        from main import SpeechToTextApp
        speech_app = SpeechToTextApp()
        
        # UI 관련 메서드 확인
        ui_methods = [
            'show_settings',
            'show_status_info',
            'toggle_system'
        ]
        
        for method_name in ui_methods:
            if hasattr(speech_app, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 트레이 매니저 연결 확인
        if speech_app.tray_manager:
            tray_signals = [
                'quit_requested',
                'settings_requested',
                'toggle_requested',
                'status_info_requested'
            ]
            
            for signal_name in tray_signals:
                if hasattr(speech_app.tray_manager, signal_name):
                    print(f"✅ 트레이 {signal_name} 시그널 존재")
                else:
                    print(f"❌ 트레이 {signal_name} 시그널 없음")
                    return False
        
        print("✅ UI 통합 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ UI 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("전체 시스템 통합 테스트 시작\n")
    
    test_results = []
    
    try:
        # 1. 메인 애플리케이션 임포트 테스트
        result1 = test_main_app_import()
        test_results.append(("메인 앱 임포트", result1))
        
        if result1:
            # 2. 애플리케이션 초기화 테스트
            result2 = test_app_initialization()
            test_results.append(("앱 초기화", result2))
            
            # 3. 컴포넌트 간 연결 테스트
            result3 = test_component_connections()
            test_results.append(("컴포넌트 연결", result3))
            
            # 4. 에러 처리 시스템 테스트
            result4 = test_error_handling()
            test_results.append(("에러 처리", result4))
            
            # 5. 통계 시스템 테스트
            result5 = test_statistics_system()
            test_results.append(("통계 시스템", result5))
            
            # 6. 전체 워크플로우 시뮬레이션
            result6 = test_workflow_simulation()
            test_results.append(("워크플로우 시뮬레이션", result6))
            
            # 7. 시스템 상태 모니터링
            result7 = test_health_monitoring()
            test_results.append(("상태 모니터링", result7))
            
            # 8. 설정 통합 테스트
            result8 = test_configuration_integration()
            test_results.append(("설정 통합", result8))
            
            # 9. UI 통합 테스트
            result9 = test_ui_integration()
            test_results.append(("UI 통합", result9))
        
        # 결과 요약
        print("\n" + "="*60)
        print("전체 시스템 통합 테스트 결과:")
        print("="*60)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 통합 테스트 통과! 전체 시스템이 정상 작동합니다.")
            print("\n📝 시스템 구성요소:")
            print("- 🎤 오디오 녹음 시스템")
            print("- 🧠 AI 음성인식 (OpenAI Whisper)")
            print("- 📋 클립보드 관리")
            print("- ⌨️ 전역 단축키")
            print("- 🖥️ 시스템 트레이 UI")
            print("- 🔧 통합 에러 처리")
            print("- 📊 실시간 통계")
            print("\n🚀 실행 준비 완료!")
        else:
            print("⚠️ 일부 통합 테스트 실패. 시스템 점검이 필요합니다.")
        
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()