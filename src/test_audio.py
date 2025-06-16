#!/usr/bin/env python3
"""
오디오 녹음 기능 테스트 스크립트
"""

import sys
import time
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import logging

# 설정 로드
from config import setup_logging
from audio_recorder import AudioRecorder

def test_audio_devices():
    """오디오 장치 테스트"""
    print("=== 오디오 장치 테스트 ===")
    
    recorder = AudioRecorder()
    devices = recorder.get_device_list()
    
    print(f"발견된 입력 장치: {len(devices)}개")
    for device in devices:
        status = "✓" if device['compatible'] else "✗"
        default = " (기본)" if device['is_default'] else ""
        print(f"{status} [{device['index']}] {device['name']}{default}")
        print(f"    채널: {device['channels']}, 샘플레이트: {device['sample_rate']}Hz")
    
    # 현재 장치 정보
    current = recorder.get_current_device_info()
    if current:
        print(f"\n현재 선택된 장치: {current['name']}")
        print(f"샘플레이트: {current['sample_rate']}Hz, 채널: {current['channels']}")

def test_recording():
    """녹음 기능 테스트"""
    print("\n=== 녹음 기능 테스트 ===")
    
    app = QApplication(sys.argv)
    recorder = AudioRecorder()
    
    # 테스트 상태 변수
    test_data = {
        'recording_count': 0,
        'max_recordings': 2
    }
    
    def on_recording_started():
        print("🔴 녹음 시작됨")
    
    def on_recording_stopped():
        print("⏹️ 녹음 중지됨")
    
    def on_recording_finished(audio_data):
        test_data['recording_count'] += 1
        duration = len(audio_data) / 16000  # 16kHz 가정
        print(f"✅ 녹음 완료: {len(audio_data)} 샘플, {duration:.2f}초")
        print(f"    데이터 타입: {audio_data.dtype}")
        print(f"    최대값: {np.max(np.abs(audio_data)):.4f}")
        print(f"    RMS: {np.sqrt(np.mean(audio_data**2)):.4f}")
        
        if test_data['recording_count'] >= test_data['max_recordings']:
            print("테스트 완료!")
            app.quit()
        else:
            # 다음 녹음을 위해 2초 대기
            QTimer.singleShot(2000, start_next_recording)
    
    def on_audio_level_changed(level):
        # 레벨 바 표시 (간단한 버전)
        if recorder.is_recording:
            bar_length = 20
            filled = int(level * bar_length * 100)  # 레벨 증폭
            bar = "█" * min(filled, bar_length) + "░" * (bar_length - min(filled, bar_length))
            print(f"\r🎤 레벨: [{bar}] {level:.4f}", end="", flush=True)
    
    def start_next_recording():
        print(f"\n3초 후 {test_data['recording_count'] + 1}번째 녹음 시작... (아무거나 말하세요)")
        time.sleep(3)
        
        if recorder.start_recording():
            # 5초 후 자동 중지
            QTimer.singleShot(5000, recorder.stop_recording)
        else:
            print("녹음 시작 실패!")
            app.quit()
    
    # 신호 연결
    recorder.recording_started.connect(on_recording_started)
    recorder.recording_stopped.connect(on_recording_stopped)
    recorder.recording_finished.connect(on_recording_finished)
    recorder.audio_level_changed.connect(on_audio_level_changed)
    
    # 첫 번째 녹음 시작
    start_next_recording()
    
    # 앱 실행
    app.exec()

def test_audio_processing():
    """오디오 처리 기능 테스트"""
    print("\n=== 오디오 처리 테스트 ===")
    
    recorder = AudioRecorder()
    
    # 테스트 오디오 생성 (1초간 사인파)
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 음
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = 0.3 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    # 앞뒤에 무음 추가
    silence = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
    test_audio_with_silence = np.concatenate([silence, test_audio, silence])
    
    print(f"원본 오디오: {len(test_audio_with_silence)} 샘플, {len(test_audio_with_silence)/sample_rate:.2f}초")
    
    # 무음 제거 테스트
    processed = recorder.remove_silence_advanced(test_audio_with_silence)
    print(f"무음 제거 후: {len(processed)} 샘플, {len(processed)/sample_rate:.2f}초")
    
    # Whisper 호환 형식 변환 테스트
    whisper_audio = recorder.process_audio_for_whisper(test_audio_with_silence)
    if whisper_audio is not None:
        print(f"Whisper 형식: {len(whisper_audio)} 샘플, {len(whisper_audio)/16000:.2f}초")
        print(f"데이터 타입: {whisper_audio.dtype}")
        print(f"값 범위: {np.min(whisper_audio):.4f} ~ {np.max(whisper_audio):.4f}")
    else:
        print("❌ Whisper 형식 변환 실패")

def main():
    """메인 테스트 함수"""
    print("음성 녹음 기능 테스트 시작\n")
    
    try:
        # 1. 장치 테스트
        test_audio_devices()
        
        # 2. 오디오 처리 테스트
        test_audio_processing()
        
        # 3. 실제 녹음 테스트
        choice = input("\n실제 녹음 테스트를 진행하시겠습니까? (y/N): ").lower()
        if choice == 'y':
            test_recording()
        else:
            print("테스트 완료!")
            
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()