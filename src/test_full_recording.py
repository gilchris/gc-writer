#!/usr/bin/env python3
"""
전체 오디오 녹음 시스템 통합 테스트
"""

import sys
import time
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 설정 로드
from config import setup_logging
from audio_recorder import AudioRecorder

def test_full_audio_system():
    """전체 오디오 시스템 테스트"""
    print("=== 전체 오디오 시스템 통합 테스트 ===")
    
    app = QApplication(sys.argv)
    
    # AudioRecorder 인스턴스 생성
    try:
        recorder = AudioRecorder()
        print("✅ AudioRecorder 초기화 성공")
    except Exception as e:
        print(f"❌ AudioRecorder 초기화 실패: {e}")
        return False
    
    # 테스트 상태
    test_state = {
        'recordings_completed': 0,
        'total_tests': 2,
        'test_passed': False
    }
    
    def on_recording_started():
        print("🔴 녹음 시작 신호 수신")
    
    def on_recording_stopped():
        print("⏹️ 녹음 중지 신호 수신")
    
    def on_recording_finished(audio_data):
        test_state['recordings_completed'] += 1
        duration = len(audio_data) / 16000  # 16kHz 가정
        max_amplitude = np.max(np.abs(audio_data)) if len(audio_data) > 0 else 0
        rms = np.sqrt(np.mean(audio_data**2)) if len(audio_data) > 0 else 0
        
        print(f"✅ 녹음 완료 ({test_state['recordings_completed']}/{test_state['total_tests']})")
        print(f"   - 길이: {len(audio_data)} 샘플 ({duration:.2f}초)")
        print(f"   - 최대 진폭: {max_amplitude:.4f}")
        print(f"   - RMS: {rms:.4f}")
        print(f"   - 데이터 타입: {audio_data.dtype}")
        
        # 유효성 검사
        if len(audio_data) > 1000 and max_amplitude > 0.001:
            print("   ✅ 유효한 오디오 데이터")
            test_state['test_passed'] = True
        else:
            print("   ⚠️ 매우 작은 신호 또는 빈 데이터")
        
        # 모든 테스트 완료 시 종료
        if test_state['recordings_completed'] >= test_state['total_tests']:
            print("\n모든 테스트 완료!")
            QTimer.singleShot(1000, app.quit)
        else:
            # 다음 테스트 준비
            print("\n2초 후 다음 테스트...")
            QTimer.singleShot(2000, start_next_test)
    
    def on_audio_level_changed(level):
        if recorder.is_recording and level > 0.01:
            # 레벨이 충분히 높을 때만 표시 (스팸 방지)
            bar_length = 20
            filled = int(level * bar_length * 50)  # 레벨 증폭
            bar = "█" * min(filled, bar_length) + "░" * (bar_length - min(filled, bar_length))
            print(f"\r🎤 레벨: [{bar}] {level:.4f}", end="", flush=True)
    
    def start_next_test():
        test_num = test_state['recordings_completed'] + 1
        print(f"\n--- 테스트 {test_num}: 3초 녹음 ---")
        print("3초간 아무거나 말해보세요...")
        
        # 녹음 시작
        if recorder.start_recording():
            # 3초 후 자동 중지
            QTimer.singleShot(3000, recorder.stop_recording)
        else:
            print("❌ 녹음 시작 실패")
            app.quit()
    
    # 신호 연결
    recorder.recording_started.connect(on_recording_started)
    recorder.recording_stopped.connect(on_recording_stopped)
    recorder.recording_finished.connect(on_recording_finished)
    recorder.audio_level_changed.connect(on_audio_level_changed)
    
    # 현재 장치 정보 출력
    device_info = recorder.get_current_device_info()
    if device_info:
        print(f"사용 장치: {device_info['name']}")
        print(f"샘플레이트: {device_info['sample_rate']}Hz")
        print(f"채널: {device_info['channels']}")
    
    # 첫 번째 테스트 시작
    print("\n1초 후 첫 번째 테스트 시작...")
    QTimer.singleShot(1000, start_next_test)
    
    # 타임아웃 설정 (20초)
    QTimer.singleShot(20000, lambda: [print("\n⏰ 테스트 타임아웃"), app.quit()])
    
    # 앱 실행
    app.exec()
    
    return test_state['test_passed']

def test_device_selection():
    """장치 선택 기능 테스트"""
    print("\n=== 장치 선택 기능 테스트 ===")
    
    try:
        recorder = AudioRecorder()
        
        # 장치 목록 가져오기
        devices = recorder.get_device_list()
        print(f"발견된 장치 수: {len(devices)}")
        
        compatible_devices = [d for d in devices if d['compatible']]
        print(f"호환 가능한 장치 수: {len(compatible_devices)}")
        
        for device in compatible_devices[:3]:  # 상위 3개만 표시
            print(f"  - {device['name']} (인덱스: {device['index']})")
        
        # 장치 변경 테스트
        if len(compatible_devices) > 1:
            new_device = compatible_devices[1]  # 두 번째 호환 장치 선택
            print(f"\n장치 변경 테스트: {new_device['name']}")
            
            if recorder.set_device(new_device['index']):
                print("✅ 장치 변경 성공")
                
                # 변경된 정보 확인
                current_info = recorder.get_current_device_info()
                if current_info:
                    print(f"현재 장치: {current_info['name']}")
                    return True
            else:
                print("❌ 장치 변경 실패")
        else:
            print("⚠️ 장치 변경 테스트 건너뜀 (호환 장치가 1개 이하)")
            return True
        
    except Exception as e:
        print(f"❌ 장치 선택 테스트 실패: {e}")
        return False

def test_audio_processing():
    """오디오 처리 기능 테스트"""
    print("\n=== 오디오 처리 기능 테스트 ===")
    
    try:
        recorder = AudioRecorder()
        
        # 테스트 데이터 생성
        sample_rate = 44100  # 다른 샘플레이트로 테스트
        duration = 2.0
        frequency = 440
        
        # 사인파 + 무음 생성
        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = 0.5 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
        silence = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
        test_audio = np.concatenate([silence, signal, silence])
        
        print(f"테스트 오디오: {len(test_audio)} 샘플, {len(test_audio)/sample_rate:.2f}초")
        
        # 리샘플링 테스트
        resampled = recorder.resample_audio(test_audio, sample_rate, 16000)
        expected_length = int(len(test_audio) * 16000 / sample_rate)
        print(f"리샘플링: {len(test_audio)} -> {len(resampled)} (예상: {expected_length})")
        
        if abs(len(resampled) - expected_length) <= 10:  # 10 샘플 오차 허용
            print("✅ 리샘플링 성공")
        else:
            print("❌ 리샘플링 오차 큼")
            return False
        
        # 무음 제거 테스트
        processed = recorder.remove_silence_advanced(test_audio)
        print(f"무음 제거: {len(test_audio)} -> {len(processed)} 샘플")
        
        if len(processed) < len(test_audio) * 0.8:  # 20% 이상 감소
            print("✅ 무음 제거 성공")
        else:
            print("⚠️ 무음 제거 효과 제한적")
        
        # Whisper 포맷 변환 테스트
        whisper_audio = recorder.process_audio_for_whisper(test_audio)
        if whisper_audio is not None:
            print(f"Whisper 형식: {len(whisper_audio)} 샘플")
            print(f"값 범위: {np.min(whisper_audio):.3f} ~ {np.max(whisper_audio):.3f}")
            
            if whisper_audio.dtype == np.float32 and np.max(np.abs(whisper_audio)) <= 1.0:
                print("✅ Whisper 형식 변환 성공")
                return True
            else:
                print("❌ Whisper 형식 불일치")
        else:
            print("❌ Whisper 형식 변환 실패")
        
        return False
        
    except Exception as e:
        print(f"❌ 오디오 처리 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("전체 오디오 녹음 시스템 통합 테스트\n")
    
    test_results = []
    
    try:
        # 1. 오디오 처리 테스트
        result1 = test_audio_processing()
        test_results.append(("오디오 처리", result1))
        
        # 2. 장치 선택 테스트
        result2 = test_device_selection()
        test_results.append(("장치 선택", result2))
        
        # 3. 실제 녹음 테스트
        print("\n실제 녹음 테스트를 진행하시겠습니까?")
        choice = input("Enter를 눌러 진행하거나 'n'을 입력하여 건너뛰기: ").lower()
        
        if choice != 'n':
            result3 = test_full_audio_system()
            test_results.append(("실제 녹음", result3))
        else:
            print("실제 녹음 테스트 건너뜀")
        
        # 결과 요약
        print("\n" + "="*50)
        print("테스트 결과 요약:")
        print("="*50)
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n총 {passed}/{len(test_results)} 테스트 통과")
        
        if passed == len(test_results):
            print("🎉 모든 테스트 통과! 오디오 시스템이 정상 작동합니다.")
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