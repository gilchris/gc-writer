#!/usr/bin/env python3
"""
Whisper 음성인식 기능 테스트 스크립트
"""

import sys
import os
import numpy as np
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_logging
setup_logging()

def test_whisper_import():
    """Whisper 관련 모듈 임포트 테스트"""
    print("=== Whisper 모듈 임포트 테스트 ===")
    
    try:
        # 기본 모듈
        import whisper
        import numpy as np
        print("✅ 기본 모듈 임포트 성공")
        
        # WhisperHandler 임포트
        from whisper_handler import WhisperHandler, WhisperWorker
        print("✅ WhisperHandler 클래스 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 실패: {e}")
        return False

def test_whisper_class_structure():
    """WhisperHandler 클래스 구조 테스트"""
    print("\n=== WhisperHandler 클래스 구조 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        # 클래스 메서드 존재 확인
        required_methods = [
            'load_model_async',
            'transcribe_audio', 
            'change_model',
            'get_available_models',
            'get_model_info',
            'is_model_loaded',
            'get_supported_languages',
            'change_language',
            'get_statistics',
            'reset_statistics'
        ]
        
        for method_name in required_methods:
            if hasattr(WhisperHandler, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 시그널 존재 확인
        required_signals = [
            'transcription_started',
            'transcription_completed',
            'transcription_failed',
            'model_loading_started',
            'model_loading_completed',
            'model_loading_failed',
            'language_detected'
        ]
        
        for signal_name in required_signals:
            if hasattr(WhisperHandler, signal_name):
                print(f"✅ {signal_name} 시그널 정의됨")
            else:
                print(f"❌ {signal_name} 시그널 없음")
                return False
        
        print("✅ 클래스 구조 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 클래스 구조 테스트 실패: {e}")
        return False

def test_model_info():
    """모델 정보 기능 테스트"""
    print("\n=== 모델 정보 기능 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        # GUI 없이 임시 인스턴스 생성
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        # WhisperHandler 생성 (모델 로딩 없이)
        whisper_handler = WhisperHandler()
        
        # 사용 가능한 모델 목록 확인
        models = whisper_handler.get_available_models()
        print(f"사용 가능한 모델: {models}")
        
        if len(models) > 0:
            print("✅ 모델 목록 로드 성공")
        else:
            print("❌ 모델 목록이 비어있음")
            return False
        
        # 각 모델 정보 확인
        for model_name in models[:3]:  # 처음 3개만 테스트
            model_info = whisper_handler.get_model_info(model_name)
            print(f"모델 '{model_name}' 정보: {model_info}")
            
            required_keys = ['size', 'speed', 'accuracy', 'memory', 'use_case']
            for key in required_keys:
                if key not in model_info:
                    print(f"❌ 모델 정보에 {key} 없음")
                    return False
        
        # 지원 언어 확인
        languages = whisper_handler.get_supported_languages()
        print(f"지원 언어: {list(languages.keys())}")
        
        if 'ko' in languages and 'en' in languages:
            print("✅ 기본 언어 지원 확인")
        else:
            print("❌ 기본 언어 지원 없음")
            return False
        
        print("✅ 모델 정보 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 모델 정보 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_validation():
    """오디오 데이터 검증 기능 테스트"""
    print("\n=== 오디오 데이터 검증 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        whisper_handler = WhisperHandler()
        
        # 테스트 케이스들
        test_cases = [
            (None, "None 데이터"),
            (np.array([]), "빈 배열"),
            (np.array([0.1] * 100), "너무 짧은 오디오 (100 샘플)"),
            (np.array([0.1] * (16000 * 31)), "너무 긴 오디오 (31초)"),
            (np.array([0.1] * 16000), "정상 오디오 (1초)"),
            ([1, 2, 3], "잘못된 타입 (리스트)")
        ]
        
        for audio_data, description in test_cases:
            error = whisper_handler._validate_audio_data(audio_data)
            if description == "정상 오디오 (1초)":
                # 정상 케이스는 에러가 없어야 함
                if error is None:
                    print(f"✅ {description}: 검증 통과")
                else:
                    print(f"❌ {description}: 예상치 못한 에러 - {error}")
                    return False
            else:
                # 비정상 케이스는 에러가 있어야 함
                if error is not None:
                    print(f"✅ {description}: 에러 감지됨 - {error}")
                else:
                    print(f"❌ {description}: 에러가 감지되지 않음")
                    return False
        
        print("✅ 오디오 데이터 검증 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 오디오 데이터 검증 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whisper_options():
    """Whisper 옵션 관리 테스트"""
    print("\n=== Whisper 옵션 관리 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        whisper_handler = WhisperHandler()
        
        # 현재 옵션 확인
        current_options = whisper_handler.get_current_options()
        print(f"현재 옵션: {current_options}")
        
        required_option_keys = ['language', 'task', 'fp16', 'temperature']
        for key in required_option_keys:
            if key in current_options:
                print(f"✅ {key} 옵션 존재: {current_options[key]}")
            else:
                print(f"❌ {key} 옵션 없음")
                return False
        
        # 옵션 업데이트 테스트
        new_options = {'temperature': 0.5, 'beam_size': 3}
        whisper_handler.update_options(new_options)
        
        updated_options = whisper_handler.get_current_options()
        if updated_options.get('temperature') == 0.5 and updated_options.get('beam_size') == 3:
            print("✅ 옵션 업데이트 성공")
        else:
            print("❌ 옵션 업데이트 실패")
            return False
        
        # 언어 변경 테스트
        whisper_handler.change_language('en')
        updated_options = whisper_handler.get_current_options()
        if updated_options.get('language') == 'en':
            print("✅ 언어 변경 성공")
        else:
            print("❌ 언어 변경 실패")
            return False
        
        print("✅ Whisper 옵션 관리 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ Whisper 옵션 관리 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """통계 기능 테스트"""
    print("\n=== 통계 기능 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        whisper_handler = WhisperHandler()
        
        # 초기 통계 확인
        initial_stats = whisper_handler.get_statistics()
        print(f"초기 통계: {initial_stats}")
        
        required_stat_keys = [
            'total_transcriptions', 
            'successful_transcriptions', 
            'failed_transcriptions',
            'average_processing_time',
            'success_rate'
        ]
        
        for key in required_stat_keys:
            if key in initial_stats:
                print(f"✅ {key} 통계 존재: {initial_stats[key]}")
            else:
                print(f"❌ {key} 통계 없음")
                return False
        
        # 초기값 확인
        if initial_stats['total_transcriptions'] == 0:
            print("✅ 초기 통계값이 올바름")
        else:
            print("❌ 초기 통계값이 잘못됨")
            return False
        
        # 통계 리셋 테스트
        whisper_handler.reset_statistics()
        reset_stats = whisper_handler.get_statistics()
        
        if all(reset_stats[key] == 0 for key in ['total_transcriptions', 'successful_transcriptions', 'failed_transcriptions']):
            print("✅ 통계 리셋 성공")
        else:
            print("❌ 통계 리셋 실패")
            return False
        
        print("✅ 통계 기능 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 통계 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whisper_worker():
    """WhisperWorker 클래스 테스트"""
    print("\n=== WhisperWorker 클래스 테스트 ===")
    
    try:
        from whisper_handler import WhisperWorker
        
        # 가짜 모델과 오디오 데이터로 워커 생성 테스트
        fake_model = None  # 실제 모델 없이 테스트
        fake_audio = np.random.random(16000).astype(np.float32)  # 1초 랜덤 오디오
        fake_options = {'language': 'ko', 'task': 'transcribe'}
        fake_callback = lambda text, error, metadata: None
        
        # 워커 인스턴스 생성
        worker = WhisperWorker(
            fake_model,
            fake_audio,
            16000,
            fake_options,
            fake_callback
        )
        
        # 워커 메서드 존재 확인
        worker_methods = [
            '_preprocess_audio',
            '_remove_silence',
            '_apply_vad',
            '_build_whisper_options',
            '_postprocess_result',
            '_clean_text'
        ]
        
        for method_name in worker_methods:
            if hasattr(worker, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 없음")
                return False
        
        # 전처리 기능 테스트 (모델 없이)
        processed_audio = worker._preprocess_audio(fake_audio)
        if processed_audio is not None and len(processed_audio) > 0:
            print("✅ 오디오 전처리 기능 동작")
        else:
            print("❌ 오디오 전처리 실패")
            return False
        
        # Whisper 옵션 구성 테스트
        options = worker._build_whisper_options()
        if isinstance(options, dict) and 'language' in options:
            print("✅ Whisper 옵션 구성 성공")
        else:
            print("❌ Whisper 옵션 구성 실패")
            return False
        
        print("✅ WhisperWorker 클래스 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ WhisperWorker 클래스 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_transcription():
    """모의 음성인식 테스트 (실제 Whisper 모델 없이)"""
    print("\n=== 모의 음성인식 테스트 ===")
    
    try:
        from whisper_handler import WhisperHandler
        
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        
        # 모델 로딩 없이 WhisperHandler 생성
        whisper_handler = WhisperHandler()
        whisper_handler.model = None  # 모델 강제로 None 설정
        
        # 가짜 오디오 데이터
        fake_audio = np.random.random(32000).astype(np.float32)  # 2초 오디오
        
        # 결과 저장용
        test_results = {'called': False, 'error': None}
        
        # 시그널 연결
        def on_transcription_failed(error):
            test_results['called'] = True
            test_results['error'] = error
            print(f"✅ transcription_failed 시그널 수신: {error}")
            app.quit()
        
        whisper_handler.transcription_failed.connect(on_transcription_failed)
        
        # 모델이 없는 상태에서 음성인식 시도
        whisper_handler.transcribe_audio(fake_audio)
        
        # 타임아웃 설정
        QTimer.singleShot(2000, app.quit)  # 2초 후 강제 종료
        
        # 이벤트 루프 실행
        app.exec()
        
        # 결과 확인
        if test_results['called'] and test_results['error']:
            print("✅ 모델 없는 상태 처리 성공")
        else:
            print("❌ 모델 없는 상태 처리 실패")
            return False
        
        print("✅ 모의 음성인식 테스트 통과")
        return True
        
    except Exception as e:
        print(f"❌ 모의 음성인식 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("Whisper 음성인식 기능 테스트 시작\n")
    
    test_results = []
    
    try:
        # 1. 모듈 임포트 테스트
        result1 = test_whisper_import()
        test_results.append(("모듈 임포트", result1))
        
        if result1:
            # 2. 클래스 구조 테스트
            result2 = test_whisper_class_structure()
            test_results.append(("클래스 구조", result2))
            
            # 3. 모델 정보 테스트
            result3 = test_model_info()
            test_results.append(("모델 정보", result3))
            
            # 4. 오디오 검증 테스트
            result4 = test_audio_validation()
            test_results.append(("오디오 검증", result4))
            
            # 5. 옵션 관리 테스트
            result5 = test_whisper_options()
            test_results.append(("옵션 관리", result5))
            
            # 6. 통계 기능 테스트
            result6 = test_statistics()
            test_results.append(("통계 기능", result6))
            
            # 7. 워커 클래스 테스트
            result7 = test_whisper_worker()
            test_results.append(("워커 클래스", result7))
            
            # 8. 모의 음성인식 테스트
            result8 = test_mock_transcription()
            test_results.append(("모의 음성인식", result8))
        
        # 결과 요약
        print("\n" + "="*50)
        print("Whisper 음성인식 테스트 결과:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! Whisper 음성인식 기능이 정상 구현되었습니다.")
            print("\n📝 주의사항:")
            print("- 실제 음성인식은 Whisper 모델이 로드된 후에 가능합니다")
            print("- 첫 실행 시 모델 다운로드로 인해 시간이 걸릴 수 있습니다")
            print("- 'base' 모델은 약 74MB이며 일반적인 사용에 권장됩니다")
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