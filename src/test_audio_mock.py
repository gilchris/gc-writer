#!/usr/bin/env python3
"""
오디오 녹음 기능 모의 테스트 (PortAudio 없이)
"""

import sys
import numpy as np
import logging
from config import setup_logging

def test_audio_processing_only():
    """오디오 처리 기능만 테스트 (sounddevice 없이)"""
    print("=== 오디오 처리 기능 테스트 ===")
    
    # AudioRecorder 클래스의 처리 메서드들만 테스트
    # sounddevice import를 우회하기 위해 직접 구현
    
    class MockAudioProcessor:
        def __init__(self):
            self.sample_rate = 16000
            self.silence_threshold = 0.01
            self.logger = logging.getLogger(__name__)
        
        def remove_silence_advanced(self, audio_data):
            """향상된 무음 제거 알고리즘"""
            if len(audio_data) == 0:
                return audio_data
            
            try:
                # 프레임 설정
                frame_length = int(self.sample_rate * 0.02)  # 20ms 프레임
                hop_length = frame_length // 2  # 50% 오버랩
                
                # RMS 기반 에너지 계산
                rms_values = []
                for i in range(0, len(audio_data) - frame_length, hop_length):
                    frame = audio_data[i:i + frame_length]
                    rms = np.sqrt(np.mean(frame**2))
                    rms_values.append(rms)
                
                if not rms_values:
                    return audio_data
                
                # 동적 임계값 계산
                rms_array = np.array(rms_values)
                noise_floor = np.percentile(rms_array, 20)  # 하위 20%를 노이즈로 간주
                dynamic_threshold = max(self.silence_threshold, noise_floor * 2)
                
                # 무음이 아닌 구간 찾기
                active_frames = rms_array > dynamic_threshold
                
                # 연속된 액티브 구간 찾기
                if not np.any(active_frames):
                    # 모든 프레임이 무음이면 가장 큰 에너지를 가진 부분 반환
                    max_idx = np.argmax(rms_array)
                    start_sample = max_idx * hop_length
                    end_sample = min(start_sample + frame_length * 10, len(audio_data))
                    return audio_data[start_sample:end_sample]
                
                # 첫 번째와 마지막 액티브 프레임 찾기
                first_active = np.where(active_frames)[0][0]
                last_active = np.where(active_frames)[0][-1]
                
                # 약간의 패딩 추가 (앞뒤로 몇 프레임씩)
                padding_frames = 2
                start_frame = max(0, first_active - padding_frames)
                end_frame = min(len(active_frames), last_active + padding_frames + 1)
                
                # 샘플 인덱스로 변환
                start_sample = start_frame * hop_length
                end_sample = min(end_frame * hop_length + frame_length, len(audio_data))
                
                result = audio_data[start_sample:end_sample]
                
                # 결과 검증
                if len(result) < frame_length:
                    return audio_data  # 너무 짧으면 원본 반환
                
                self.logger.debug(f"무음 제거: {len(audio_data)} -> {len(result)} 샘플")
                return result
                
            except Exception as e:
                self.logger.warning(f"무음 제거 실패: {e}")
                return audio_data
        
        def resample_audio(self, audio_data, original_sr, target_sr):
            """오디오 리샘플링"""
            try:
                if original_sr == target_sr:
                    return audio_data
                
                # 간단한 리샘플링 (선형 보간)
                ratio = target_sr / original_sr
                new_length = int(len(audio_data) * ratio)
                
                # numpy의 interp를 사용한 리샘플링
                old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
                new_indices = np.linspace(0, len(audio_data) - 1, new_length)
                resampled = np.interp(new_indices, old_indices, audio_data)
                
                self.logger.info(f"리샘플링: {original_sr}Hz -> {target_sr}Hz")
                return resampled.astype(np.float32)
                
            except Exception as e:
                self.logger.error(f"리샘플링 실패: {e}")
                return audio_data
        
        def process_audio_for_whisper(self, audio_data):
            """Whisper 호환 형식으로 오디오 처리"""
            try:
                if len(audio_data) == 0:
                    return None
                
                # 1. 데이터 타입 확인 및 변환
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                # 2. 정규화 (-1.0 ~ 1.0 범위)
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val
                
                # 3. 무음 제거
                audio_data = self.remove_silence_advanced(audio_data)
                
                # 4. 최소 길이 확인 (0.1초 이상)
                min_samples = int(self.sample_rate * 0.1)
                if len(audio_data) < min_samples:
                    self.logger.warning("오디오가 너무 짧습니다 (0.1초 미만)")
                    return None
                
                # 5. 샘플레이트가 16kHz가 아니면 리샘플링
                if self.sample_rate != 16000:
                    audio_data = self.resample_audio(audio_data, self.sample_rate, 16000)
                
                return audio_data
                
            except Exception as e:
                self.logger.error(f"오디오 처리 실패: {e}")
                return None
    
    # 테스트 시작
    processor = MockAudioProcessor()
    
    # 1. 사인파 + 무음 테스트
    print("1. 사인파 + 무음 테스트")
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 음
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = 0.3 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    # 앞뒤에 무음 추가
    silence = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
    test_audio_with_silence = np.concatenate([silence, test_audio, silence])
    
    print(f"   원본: {len(test_audio_with_silence)} 샘플, {len(test_audio_with_silence)/sample_rate:.2f}초")
    
    # 무음 제거 테스트
    processed = processor.remove_silence_advanced(test_audio_with_silence)
    print(f"   무음 제거 후: {len(processed)} 샘플, {len(processed)/sample_rate:.2f}초")
    
    # Whisper 호환 형식 변환 테스트
    whisper_audio = processor.process_audio_for_whisper(test_audio_with_silence)
    if whisper_audio is not None:
        print(f"   Whisper 형식: {len(whisper_audio)} 샘플, {len(whisper_audio)/16000:.2f}초")
        print(f"   데이터 타입: {whisper_audio.dtype}")
        print(f"   값 범위: {np.min(whisper_audio):.4f} ~ {np.max(whisper_audio):.4f}")
        print("   ✅ 처리 성공")
    else:
        print("   ❌ 처리 실패")
    
    # 2. 리샘플링 테스트
    print("\n2. 리샘플링 테스트")
    processor.sample_rate = 44100  # 44.1kHz로 설정
    test_44k = 0.2 * np.sin(2 * np.pi * 880 * np.linspace(0, 0.5, 22050)).astype(np.float32)
    print(f"   원본 (44.1kHz): {len(test_44k)} 샘플")
    
    resampled = processor.resample_audio(test_44k, 44100, 16000)
    print(f"   리샘플링 (16kHz): {len(resampled)} 샘플")
    expected_length = int(len(test_44k) * 16000 / 44100)
    print(f"   예상 길이: {expected_length}, 실제 차이: {abs(len(resampled) - expected_length)}")
    
    if abs(len(resampled) - expected_length) <= 1:
        print("   ✅ 리샘플링 성공")
    else:
        print("   ❌ 리샘플링 오차 큼")
    
    # 3. 노이즈 + 신호 테스트
    print("\n3. 노이즈 + 신호 테스트")
    # 저레벨 노이즈 생성
    noise = np.random.normal(0, 0.01, int(sample_rate * 2)).astype(np.float32)
    # 중간에 실제 신호 삽입
    signal_start = int(sample_rate * 0.5)
    signal_end = int(sample_rate * 1.5)
    signal = 0.5 * np.sin(2 * np.pi * 220 * np.linspace(0, 1, signal_end - signal_start))
    noise[signal_start:signal_end] += signal
    
    print(f"   노이즈+신호: {len(noise)} 샘플, {len(noise)/sample_rate:.2f}초")
    
    processor.sample_rate = 16000  # 다시 16kHz로 설정
    denoised = processor.remove_silence_advanced(noise)
    print(f"   무음 제거 후: {len(denoised)} 샘플, {len(denoised)/sample_rate:.2f}초")
    
    if len(denoised) < len(noise) * 0.8:  # 원본의 80% 이하로 줄어들면 성공
        print("   ✅ 노이즈 제거 성공")
    else:
        print("   ⚠️ 노이즈 제거 효과 미미")
    
    print("\n=== 오디오 처리 기능 테스트 완료 ===")

def test_config_loading():
    """설정 로딩 테스트"""
    print("\n=== 설정 로딩 테스트 ===")
    
    try:
        from config import config
        
        # 오디오 설정 확인
        sample_rate = config.get('audio.sample_rate', 16000)
        channels = config.get('audio.channels', 1)
        silence_threshold = config.get('audio.silence_threshold', 0.01)
        
        print(f"샘플레이트: {sample_rate}Hz")
        print(f"채널: {channels}")
        print(f"무음 임계값: {silence_threshold}")
        
        # Whisper 설정 확인
        model_name = config.get('whisper.model_name', 'base')
        language = config.get('whisper.language', 'ko')
        
        print(f"Whisper 모델: {model_name}")
        print(f"언어: {language}")
        
        print("✅ 설정 로딩 성공")
        
    except Exception as e:
        print(f"❌ 설정 로딩 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("오디오 처리 기능 모의 테스트 시작\n")
    
    try:
        # 1. 설정 테스트
        test_config_loading()
        
        # 2. 오디오 처리 테스트
        test_audio_processing_only()
        
        print("\n모든 테스트 완료!")
        print("\n참고: 실제 오디오 녹음 테스트를 위해서는 다음이 필요합니다:")
        print("sudo apt install portaudio19-dev")
        print("그 후 python src/test_audio.py 실행")
        
    except Exception as e:
        print(f"테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()