#!/usr/bin/env python3
"""
간단한 오디오 테스트 (특정 장치 사용)
"""

import sys
import numpy as np
import sounddevice as sd
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def test_simple_recording():
    """간단한 녹음 테스트"""
    print("=== 간단한 오디오 녹음 테스트 ===")
    
    try:
        # PulseAudio 장치 사용 시도
        pulse_device = None
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            if 'pulse' in device['name'].lower() and device['max_input_channels'] > 0:
                pulse_device = i
                break
        
        if pulse_device is None:
            # 기본 장치 사용
            pulse_device = sd.default.device[0]
        
        device_info = sd.query_devices(pulse_device)
        print(f"사용할 장치: {device_info['name']}")
        print(f"최대 입력 채널: {device_info['max_input_channels']}")
        print(f"기본 샘플레이트: {device_info['default_samplerate']}")
        
        # 간단한 설정으로 테스트
        sample_rate = 16000
        duration = 3  # 3초
        channels = 1
        
        print(f"\n{duration}초간 녹음 시작... (아무거나 말해보세요)")
        time.sleep(1)
        
        # 녹음 수행
        audio_data = sd.rec(
            int(sample_rate * duration),
            samplerate=sample_rate,
            channels=channels,
            dtype=np.float32,
            device=pulse_device
        )
        
        sd.wait()  # 녹음 완료까지 대기
        
        print("녹음 완료!")
        print(f"데이터 크기: {audio_data.shape}")
        print(f"데이터 타입: {audio_data.dtype}")
        print(f"최대 진폭: {np.max(np.abs(audio_data)):.4f}")
        print(f"RMS: {np.sqrt(np.mean(audio_data**2)):.4f}")
        
        # 간단한 재생 테스트
        choice = input("\n녹음된 내용을 재생해보시겠습니까? (y/N): ").lower()
        if choice == 'y':
            print("재생 중...")
            sd.play(audio_data, sample_rate)
            sd.wait()
            print("재생 완료!")
        
        return True
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return False

def test_device_list():
    """장치 목록 출력"""
    print("=== 사용 가능한 오디오 장치 ===")
    
    try:
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
        
        print(f"입력 장치 {len(input_devices)}개 발견:")
        for i, (idx, device) in enumerate(input_devices):
            print(f"{i+1}. [{idx}] {device['name']}")
            print(f"    채널: {device['max_input_channels']}, 샘플레이트: {device['default_samplerate']}Hz")
        
        return input_devices
        
    except Exception as e:
        print(f"장치 목록 조회 실패: {e}")
        return []

def test_specific_device():
    """특정 장치로 테스트"""
    devices = test_device_list()
    
    if not devices:
        return False
    
    print("\n특정 장치를 선택하여 테스트하시겠습니까?")
    choice = input("장치 번호를 입력하세요 (1-{}) 또는 Enter로 기본 장치 사용: ".format(len(devices)))
    
    device_index = None
    if choice.strip():
        try:
            selected = int(choice) - 1
            if 0 <= selected < len(devices):
                device_index = devices[selected][0]
                print(f"선택된 장치: {devices[selected][1]['name']}")
            else:
                print("잘못된 번호입니다. 기본 장치를 사용합니다.")
        except ValueError:
            print("잘못된 입력입니다. 기본 장치를 사용합니다.")
    
    # 선택된 장치로 녹음 테스트
    try:
        sample_rate = 16000
        duration = 3
        channels = 1
        
        print(f"\n{duration}초간 녹음 시작...")
        time.sleep(1)
        
        if device_index is not None:
            audio_data = sd.rec(
                int(sample_rate * duration),
                samplerate=sample_rate,
                channels=channels,
                dtype=np.float32,
                device=device_index
            )
        else:
            audio_data = sd.rec(
                int(sample_rate * duration),
                samplerate=sample_rate,
                channels=channels,
                dtype=np.float32
            )
        
        sd.wait()
        
        print("녹음 완료!")
        print(f"데이터 크기: {audio_data.shape}")
        print(f"최대 진폭: {np.max(np.abs(audio_data)):.4f}")
        
        # 유효한 오디오 데이터인지 확인
        if np.max(np.abs(audio_data)) > 0.001:
            print("✅ 유효한 오디오 데이터가 감지되었습니다!")
            return True
        else:
            print("⚠️ 매우 작은 신호 또는 무음이 감지되었습니다.")
            return False
            
    except Exception as e:
        print(f"녹음 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("간단한 오디오 녹음 테스트\n")
    
    try:
        # 1. 기본 테스트
        success = test_simple_recording()
        
        if not success:
            print("\n기본 테스트 실패. 특정 장치로 재시도...")
            test_specific_device()
        
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 중 오류: {e}")

if __name__ == "__main__":
    main()