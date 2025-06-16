"""
오디오 녹음 모듈
"""

import numpy as np
import sounddevice as sd
import threading
import logging
import time
from collections import deque
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from io import BytesIO
from config import config


class AudioRecorder(QObject):
    recording_finished = pyqtSignal(np.ndarray)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    device_changed = pyqtSignal(str)
    audio_level_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 설정에서 녹음 파라미터 로드
        self.sample_rate = config.get('audio.sample_rate', 16000)
        self.channels = config.get('audio.channels', 1)
        self.dtype = np.float32
        self.device_index = config.get('audio.device_index', None)
        self.silence_threshold = config.get('audio.silence_threshold', 0.01)
        self.remove_silence_enabled = config.get('audio.remove_silence', True)
        self.buffer_size = config.get('advanced.audio_buffer_size', 1024)
        
        # 녹음 상태
        self.is_recording = False
        self.audio_data = deque()  # 효율적인 데이터 추가를 위해 deque 사용
        self.stream = None
        self.recording_start_time = None
        self.max_recording_duration = 300  # 5분 최대 녹음 시간
        
        # 실시간 오디오 레벨 모니터링
        self.audio_level_timer = QTimer()
        self.audio_level_timer.timeout.connect(self.update_audio_level)
        self.current_audio_level = 0.0
        self.level_buffer = deque(maxlen=10)  # 최근 10개 레벨 값 저장
        
        # 무음 감지
        self.silence_timer = QTimer()
        self.silence_timer.timeout.connect(self.check_silence)
        self.silence_duration = 0
        self.max_silence_duration = 3000  # 3초 무음시 자동 종료
        self.auto_stop_enabled = config.get('audio.auto_stop_silence', False)
        
        self.setup_audio_device()
    
    def setup_audio_device(self):
        """오디오 장치 설정 및 검증"""
        try:
            # 사용 가능한 장치 목록 가져오기
            devices = self.get_device_list()
            if not devices:
                raise Exception("사용 가능한 오디오 입력 장치가 없습니다")
            
            # 설정된 장치 인덱스 확인
            if self.device_index is not None:
                device_valid = any(d['index'] == self.device_index for d in devices)
                if not device_valid:
                    self.logger.warning(f"설정된 장치 인덱스 {self.device_index}가 유효하지 않음")
                    self.device_index = None
            
            # 기본 입력 장치 또는 지정된 장치 정보 가져오기
            if self.device_index is not None:
                device_info = sd.query_devices(self.device_index)
            else:
                device_info = sd.query_devices(kind='input')
                self.device_index = device_info.get('index', None)
            
            self.logger.info(f"사용할 마이크: {device_info['name']} (인덱스: {self.device_index})")
            
            # 장치가 지원하는 샘플레이트 확인 및 조정
            self.validate_and_adjust_settings(device_info)
            
            # 설정 저장
            config.set('audio.device_index', self.device_index)
            config.set('audio.sample_rate', self.sample_rate)
            
        except Exception as e:
            self.logger.error(f"오디오 장치 설정 실패: {e}")
            # 기본값으로 폴백
            self.device_index = None
            self.sample_rate = 16000
    
    def validate_and_adjust_settings(self, device_info):
        """장치 설정 검증 및 조정"""
        try:
            # 현재 설정으로 테스트
            sd.check_input_settings(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=self.dtype
            )
            self.logger.info(f"오디오 설정 검증 완료: {self.sample_rate}Hz, {self.channels}ch")
            
        except Exception as e:
            self.logger.warning(f"현재 설정 불가: {e}")
            
            # 장치의 기본 샘플레이트로 조정
            try:
                new_sample_rate = int(device_info['default_samplerate'])
                sd.check_input_settings(
                    device=self.device_index,
                    channels=self.channels,
                    samplerate=new_sample_rate,
                    dtype=self.dtype
                )
                self.sample_rate = new_sample_rate
                self.logger.info(f"샘플레이트를 {self.sample_rate}Hz로 조정")
                
            except Exception as e2:
                self.logger.error(f"샘플레이트 조정 실패: {e2}")
                # 최후의 수단으로 44100Hz 시도
                try:
                    sd.check_input_settings(
                        device=self.device_index,
                        channels=self.channels,
                        samplerate=44100,
                        dtype=self.dtype
                    )
                    self.sample_rate = 44100
                    self.logger.info("샘플레이트를 44100Hz로 폴백")
                except:
                    raise Exception("호환되는 오디오 설정을 찾을 수 없습니다")
    
    def set_device(self, device_index):
        """오디오 장치 변경"""
        if self.is_recording:
            self.logger.warning("녹음 중에는 장치를 변경할 수 없습니다")
            return False
        
        try:
            # 새 장치 정보 가져오기
            device_info = sd.query_devices(device_index)
            if device_info['max_input_channels'] == 0:
                raise Exception("입력 장치가 아닙니다")
            
            # 이전 설정 백업
            old_device = self.device_index
            old_sample_rate = self.sample_rate
            
            # 새 장치 설정
            self.device_index = device_index
            self.validate_and_adjust_settings(device_info)
            
            self.logger.info(f"오디오 장치 변경: {device_info['name']}")
            self.device_changed.emit(device_info['name'])
            
            # 설정 저장
            config.set('audio.device_index', self.device_index)
            config.save_settings()
            
            return True
            
        except Exception as e:
            self.logger.error(f"장치 변경 실패: {e}")
            # 이전 설정 복원
            self.device_index = old_device
            self.sample_rate = old_sample_rate
            return False
    
    def audio_callback(self, indata, frames, time, status):
        """실시간 오디오 스트림 콜백"""
        if status:
            self.logger.warning(f"오디오 스트림 상태: {status}")
        
        if self.is_recording:
            # 오디오 데이터를 메모리 버퍼에 저장
            audio_frame = indata.copy()
            self.audio_data.append(audio_frame)
            
            # 실시간 오디오 레벨 계산
            rms_level = np.sqrt(np.mean(audio_frame**2))
            self.level_buffer.append(rms_level)
            
            # 평균 레벨 계산 (노이즈 감소)
            if self.level_buffer:
                self.current_audio_level = np.mean(list(self.level_buffer))
            
            # 최대 녹음 시간 체크
            if self.recording_start_time:
                elapsed = time.time() - self.recording_start_time
                if elapsed > self.max_recording_duration:
                    self.logger.warning("최대 녹음 시간 초과 - 자동 중지")
                    self.stop_recording()
    
    def update_audio_level(self):
        """오디오 레벨 업데이트 신호 발송"""
        if self.is_recording:
            self.audio_level_changed.emit(self.current_audio_level)
    
    def check_silence(self):
        """무음 감지 및 자동 중지"""
        if not self.is_recording or not self.auto_stop_enabled:
            return
        
        if self.current_audio_level < self.silence_threshold:
            self.silence_duration += 100  # 100ms 증가
            if self.silence_duration >= self.max_silence_duration:
                self.logger.info("무음 감지로 인한 자동 녹음 중지")
                self.stop_recording()
        else:
            self.silence_duration = 0  # 소리가 감지되면 리셋
    
    def start_recording(self):
        """향상된 녹음 시작"""
        if self.is_recording:
            self.logger.warning("이미 녹음 중입니다")
            return False
        
        try:
            # 메모리 버퍼 초기화
            self.audio_data.clear()
            self.level_buffer.clear()
            self.current_audio_level = 0.0
            self.silence_duration = 0
            self.recording_start_time = time.time()
            
            # 스트림 생성 및 시작
            self.stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.buffer_size,
                callback=self.audio_callback,
                latency='low'  # 낮은 지연시간 설정
            )
            
            self.stream.start()
            self.is_recording = True
            
            # 타이머 시작
            self.audio_level_timer.start(100)  # 100ms마다 레벨 업데이트
            if self.auto_stop_enabled:
                self.silence_timer.start(100)  # 100ms마다 무음 체크
            
            self.logger.info(f"녹음 시작됨 - 장치: {self.device_index}, 샘플레이트: {self.sample_rate}Hz")
            self.recording_started.emit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"녹음 시작 실패: {e}")
            self.is_recording = False
            self.cleanup_recording()
            return False
    
    def cleanup_recording(self):
        """녹음 관련 리소스 정리"""
        # 타이머 중지
        self.audio_level_timer.stop()
        self.silence_timer.stop()
        
        # 스트림 정리
        if self.stream:
            try:
                if self.stream.active:
                    self.stream.stop()
                self.stream.close()
            except Exception as e:
                self.logger.warning(f"스트림 정리 중 오류: {e}")
            finally:
                self.stream = None
    
    def stop_recording(self):
        """향상된 녹음 중지 및 데이터 처리"""
        if not self.is_recording:
            self.logger.warning("녹음 중이 아닙니다")
            return None
        
        try:
            self.is_recording = False
            
            # 리소스 정리
            self.cleanup_recording()
            
            # 녹음 시간 계산
            recording_duration = 0
            if self.recording_start_time:
                recording_duration = time.time() - self.recording_start_time
            
            # 오디오 데이터 처리
            if self.audio_data:
                # deque를 리스트로 변환 후 배열로 병합
                audio_frames = list(self.audio_data)
                if audio_frames:
                    audio_array = np.concatenate(audio_frames, axis=0)
                    audio_array = audio_array.flatten()  # 2D -> 1D
                    
                    self.logger.info(f"원본 오디오: {len(audio_array)} 샘플, {recording_duration:.2f}초")
                    
                    # Whisper 호환 형식으로 변환
                    processed_audio = self.process_audio_for_whisper(audio_array)
                    
                    if processed_audio is not None and len(processed_audio) > 0:
                        final_duration = len(processed_audio) / self.sample_rate
                        self.logger.info(f"처리된 오디오: {len(processed_audio)} 샘플, {final_duration:.2f}초")
                        
                        self.recording_stopped.emit()
                        self.recording_finished.emit(processed_audio)
                        
                        return processed_audio
                    else:
                        self.logger.warning("유효한 오디오 데이터가 없습니다")
                else:
                    self.logger.warning("오디오 프레임이 없습니다")
            else:
                self.logger.warning("녹음된 데이터가 없습니다")
            
            self.recording_stopped.emit()
            return None
                
        except Exception as e:
            self.logger.error(f"녹음 중지 실패: {e}")
            self.cleanup_recording()
            self.recording_stopped.emit()
            return None
    
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
            
            # 3. 무음 제거 (설정에 따라)
            if self.remove_silence_enabled:
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
    
    def resample_audio(self, audio_data, original_sr, target_sr):
        """오디오 리샘플링"""
        try:
            # scipy나 librosa를 사용하는 것이 좋지만, 간단한 방법으로 구현
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
    
    def remove_silence(self, audio_data, threshold=None):
        """기본 무음 제거 (하위 호환성)"""
        if threshold is None:
            threshold = self.silence_threshold
        
        return self.remove_silence_advanced(audio_data)
    
    def get_device_list(self):
        """향상된 오디오 장치 목록 반환"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    # 장치 호환성 테스트
                    is_compatible = self.test_device_compatibility(i)
                    
                    device_info = {
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate'],
                        'compatible': is_compatible,
                        'is_default': i == sd.default.device[0] if sd.default.device[0] is not None else False
                    }
                    input_devices.append(device_info)
            
            # 호환 가능한 장치를 앞으로 정렬
            input_devices.sort(key=lambda x: (not x['compatible'], not x['is_default'], x['name']))
            
            self.logger.info(f"발견된 입력 장치: {len(input_devices)}개")
            return input_devices
            
        except Exception as e:
            self.logger.error(f"장치 목록 조회 실패: {e}")
            return []
    
    def test_device_compatibility(self, device_index):
        """장치 호환성 테스트"""
        try:
            # 간단한 호환성 테스트
            sd.check_input_settings(
                device=device_index,
                channels=1,
                samplerate=16000,
                dtype=np.float32
            )
            return True
        except:
            try:
                # 다른 설정으로 재시도
                device_info = sd.query_devices(device_index)
                sd.check_input_settings(
                    device=device_index,
                    channels=1,
                    samplerate=int(device_info['default_samplerate']),
                    dtype=np.float32
                )
                return True
            except:
                return False
    
    def get_current_device_info(self):
        """현재 선택된 장치 정보 반환"""
        try:
            if self.device_index is not None:
                device_info = sd.query_devices(self.device_index)
                return {
                    'index': self.device_index,
                    'name': device_info['name'],
                    'channels': device_info['max_input_channels'],
                    'sample_rate': self.sample_rate,
                    'is_recording': self.is_recording
                }
            else:
                default_device = sd.query_devices(kind='input')
                return {
                    'index': None,
                    'name': default_device['name'],
                    'channels': default_device['max_input_channels'],
                    'sample_rate': self.sample_rate,
                    'is_recording': self.is_recording
                }
        except Exception as e:
            self.logger.error(f"현재 장치 정보 조회 실패: {e}")
            return None
    
    def get_recording_stats(self):
        """녹음 상태 및 통계 정보 반환"""
        stats = {
            'is_recording': self.is_recording,
            'current_level': self.current_audio_level,
            'silence_duration': self.silence_duration,
            'buffer_size': len(self.audio_data) if self.audio_data else 0,
            'recording_duration': 0
        }
        
        if self.recording_start_time and self.is_recording:
            stats['recording_duration'] = time.time() - self.recording_start_time
        
        return stats
    
    def set_audio_settings(self, **kwargs):
        """오디오 설정 변경"""
        if self.is_recording:
            self.logger.warning("녹음 중에는 설정을 변경할 수 없습니다")
            return False
        
        try:
            updated = False
            
            if 'silence_threshold' in kwargs:
                self.silence_threshold = kwargs['silence_threshold']
                config.set('audio.silence_threshold', self.silence_threshold)
                updated = True
            
            if 'remove_silence' in kwargs:
                self.remove_silence_enabled = kwargs['remove_silence']
                config.set('audio.remove_silence', self.remove_silence_enabled)
                updated = True
            
            if 'auto_stop_silence' in kwargs:
                self.auto_stop_enabled = kwargs['auto_stop_silence']
                updated = True
            
            if 'max_silence_duration' in kwargs:
                self.max_silence_duration = kwargs['max_silence_duration']
                updated = True
            
            if updated:
                config.save_settings()
                self.logger.info("오디오 설정이 업데이트되었습니다")
                
            return updated
            
        except Exception as e:
            self.logger.error(f"설정 변경 실패: {e}")
            return False
    
    def __del__(self):
        """소멸자 - 리소스 정리"""
        try:
            if self.is_recording:
                self.stop_recording()
            self.cleanup_recording()
        except:
            pass