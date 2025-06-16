"""
고급 OpenAI Whisper 음성 인식 모듈
"""

import whisper
import numpy as np
import threading
import logging
import time
import os
import warnings
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QRunnable, QThreadPool
from config import config


class WhisperWorker(QRunnable):
    """향상된 Whisper 처리를 위한 워커 클래스"""
    
    def __init__(self, model, audio_data, sample_rate, options, callback):
        super().__init__()
        self.model = model
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.options = options
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
    
    def run(self):
        try:
            # 오디오 데이터 전처리
            audio_data = self._preprocess_audio(self.audio_data)
            
            if audio_data is None or len(audio_data) == 0:
                self.callback(None, "유효하지 않은 오디오 데이터", None)
                return
            
            # 음성 구간 감지 (VAD)
            if self.options.get('enable_vad', True):
                audio_data = self._apply_vad(audio_data)
            
            # Whisper 옵션 설정
            whisper_options = self._build_whisper_options()
            
            # Whisper로 음성 인식
            self.logger.debug(f"Whisper 실행 시작 - 옵션: {whisper_options}")
            result = self.model.transcribe(audio_data, **whisper_options)
            
            # 결과 후처리
            text, confidence = self._postprocess_result(result)
            
            processing_time = time.time() - self.start_time
            self.logger.info(f"음성 인식 완료 - 처리시간: {processing_time:.2f}초")
            
            self.callback(text, None, {
                'confidence': confidence,
                'processing_time': processing_time,
                'language': result.get('language', 'unknown'),
                'segments': len(result.get('segments', []))
            })
            
        except Exception as e:
            error_msg = f"음성 인식 실패: {e}"
            self.logger.error(error_msg)
            self.callback(None, error_msg, None)
    
    def _preprocess_audio(self, audio_data):
        """오디오 데이터 전처리"""
        try:
            # 타입 변환
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # 정규화
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # 리샘플링 (16kHz로)
            if self.sample_rate != 16000:
                try:
                    import librosa
                    audio_data = librosa.resample(
                        audio_data, 
                        orig_sr=self.sample_rate, 
                        target_sr=16000
                    )
                    self.logger.debug(f"리샘플링: {self.sample_rate}Hz -> 16000Hz")
                except ImportError:
                    self.logger.warning("librosa가 없어 리샘플링 생략")
            
            # 무음 구간 제거
            silence_threshold = self.options.get('silence_threshold', 0.01)
            if silence_threshold > 0:
                audio_data = self._remove_silence(audio_data, silence_threshold)
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"오디오 전처리 실패: {e}")
            return None
    
    def _remove_silence(self, audio_data, threshold):
        """무음 구간 제거"""
        try:
            # 윈도우 크기 (100ms)
            window_size = int(16000 * 0.1)
            
            # 에너지 계산
            energy = np.array([np.sum(audio_data[i:i+window_size]**2) 
                             for i in range(0, len(audio_data)-window_size, window_size//2)])
            
            # 임계값을 넘는 구간 찾기
            active_windows = energy > threshold
            
            if np.any(active_windows):
                start_idx = np.where(active_windows)[0][0] * window_size // 2
                end_idx = np.where(active_windows)[0][-1] * window_size // 2 + window_size
                return audio_data[start_idx:end_idx]
            else:
                return audio_data
                
        except Exception as e:
            self.logger.warning(f"무음 제거 실패: {e}")
            return audio_data
    
    def _apply_vad(self, audio_data):
        """Voice Activity Detection 적용"""
        try:
            # 간단한 에너지 기반 VAD
            frame_length = int(16000 * 0.025)  # 25ms
            hop_length = int(16000 * 0.01)     # 10ms
            
            frames = np.array([audio_data[i:i+frame_length] 
                             for i in range(0, len(audio_data)-frame_length, hop_length)])
            
            energies = np.sum(frames**2, axis=1)
            threshold = np.mean(energies) * 0.3
            
            voice_frames = energies > threshold
            
            if np.any(voice_frames):
                start_frame = np.where(voice_frames)[0][0]
                end_frame = np.where(voice_frames)[0][-1]
                
                start_sample = start_frame * hop_length
                end_sample = min(end_frame * hop_length + frame_length, len(audio_data))
                
                return audio_data[start_sample:end_sample]
            else:
                return audio_data
                
        except Exception as e:
            self.logger.warning(f"VAD 적용 실패: {e}")
            return audio_data
    
    def _build_whisper_options(self):
        """Whisper 옵션 구성"""
        options = {
            'language': self.options.get('language', 'ko'),
            'task': self.options.get('task', 'transcribe'),
            'fp16': self.options.get('fp16', False),
            'temperature': self.options.get('temperature', 0.0),
            'best_of': self.options.get('best_of', 5),
            'beam_size': self.options.get('beam_size', 5),
            'patience': self.options.get('patience', None),
            'suppress_tokens': self.options.get('suppress_tokens', "-1"),
            'initial_prompt': self.options.get('initial_prompt', None),
            'condition_on_previous_text': self.options.get('condition_on_previous_text', True),
            'verbose': False
        }
        
        # None 값 제거
        return {k: v for k, v in options.items() if v is not None}
    
    def _postprocess_result(self, result):
        """결과 후처리"""
        try:
            text = result['text'].strip()
            
            # 신뢰도 계산 (segments 기반)
            segments = result.get('segments', [])
            if segments:
                confidences = []
                for segment in segments:
                    if 'avg_logprob' in segment:
                        # 로그 확률을 신뢰도로 변환
                        confidence = np.exp(segment['avg_logprob'])
                        confidences.append(confidence)
                
                avg_confidence = np.mean(confidences) if confidences else 0.5
            else:
                avg_confidence = 0.5
            
            # 텍스트 정리
            if text:
                # 반복 문구 제거
                text = self._clean_text(text)
            
            return text, avg_confidence
            
        except Exception as e:
            self.logger.warning(f"결과 후처리 실패: {e}")
            return result.get('text', '').strip(), 0.5
    
    def _clean_text(self, text):
        """텍스트 정리"""
        try:
            # 기본 정리
            text = text.strip()
            
            # 연속된 공백 제거
            import re
            text = re.sub(r'\s+', ' ', text)
            
            # 특수 문자 정리 (선택적)
            if self.options.get('clean_special_chars', False):
                text = re.sub(r'[^\w\s가-힣]', '', text)
            
            return text
            
        except Exception as e:
            self.logger.warning(f"텍스트 정리 실패: {e}")
            return text


class WhisperHandler(QObject):
    transcription_started = pyqtSignal()
    transcription_completed = pyqtSignal(str, dict)  # 텍스트, 메타데이터
    transcription_failed = pyqtSignal(str)
    model_loading_started = pyqtSignal(str)  # 모델명
    model_loading_completed = pyqtSignal(str)  # 모델명
    model_loading_failed = pyqtSignal(str)  # 에러 메시지
    language_detected = pyqtSignal(str)  # 감지된 언어
    
    def __init__(self, model_name=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 설정에서 모델명 로드
        self.model_name = model_name or config.get('whisper.model_name', 'base')
        self.model = None
        self.model_loading = False
        self.thread_pool = QThreadPool()
        
        # Whisper 옵션 로드
        self.options = self._load_whisper_options()
        
        # 통계
        self.stats = {
            'total_transcriptions': 0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'total_processing_time': 0.0,
            'average_confidence': 0.0
        }
        
        # 모델 로딩을 별도 스레드에서 수행
        self.load_model_async()
    
    def load_model_async(self):
        """향상된 비동기 Whisper 모델 로딩"""
        if self.model_loading:
            self.logger.warning("모델이 이미 로딩 중입니다")
            return
        
        def load_model():
            try:
                self.model_loading = True
                self.model_loading_started.emit(self.model_name)
                self.logger.info(f"Whisper 모델 로딩 시작: {self.model_name}")
                
                # 모델 정보 로그
                model_info = self.get_model_info(self.model_name)
                self.logger.info(f"모델 정보: {model_info}")
                
                # Whisper 경고 억제
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    
                    # 모델 로드 시작 시간
                    start_time = time.time()
                    
                    # 모델 로딩
                    self.model = whisper.load_model(
                        self.model_name,
                        download_root=None,  # 기본 경로 사용
                        in_memory=True      # 메모리에 로드
                    )
                    
                    load_time = time.time() - start_time
                
                self.logger.info(f"Whisper 모델 로딩 완료 - 소요시간: {load_time:.2f}초")
                self.model_loading_completed.emit(self.model_name)
                
            except Exception as e:
                error_msg = f"모델 로딩 실패: {e}"
                self.logger.error(error_msg)
                self.model_loading_failed.emit(error_msg)
            finally:
                self.model_loading = False
        
        thread = threading.Thread(target=load_model, daemon=True)
        thread.start()
    
    def transcribe_audio(self, audio_data, sample_rate=16000, custom_options=None):
        """향상된 오디오 데이터를 텍스트로 변환"""
        if self.model is None:
            if not self.model_loading:
                self.logger.error("Whisper 모델이 로드되지 않았습니다")
                self.transcription_failed.emit("모델이 로드되지 않았습니다. 모델을 다시 로딩해주세요.")
            else:
                self.transcription_failed.emit("모델 로딩 중입니다. 잠시 후 다시 시도해주세요.")
            return
        
        # 오디오 데이터 검증
        validation_error = self._validate_audio_data(audio_data)
        if validation_error:
            self.transcription_failed.emit(validation_error)
            return
        
        # 옵션 병합
        options = self.options.copy()
        if custom_options:
            options.update(custom_options)
        
        self.logger.info(f"음성 인식 시작 - 길이: {len(audio_data)/sample_rate:.2f}초")
        self.transcription_started.emit()
        
        # 통계 업데이트
        self.stats['total_transcriptions'] += 1
        
        # 콜백 함수
        def on_transcription_complete(text, error, metadata):
            if error:
                self.stats['failed_transcriptions'] += 1
                self.logger.error(f"음성 인식 실패: {error}")
                self.transcription_failed.emit(error)
            else:
                if text and text.strip():
                    # 성공 통계 업데이트
                    self.stats['successful_transcriptions'] += 1
                    
                    if metadata:
                        self.stats['total_processing_time'] += metadata.get('processing_time', 0)
                        
                        # 평균 신뢰도 업데이트
                        confidence = metadata.get('confidence', 0.5)
                        self.stats['average_confidence'] = (
                            (self.stats['average_confidence'] * (self.stats['successful_transcriptions'] - 1) + confidence) /
                            self.stats['successful_transcriptions']
                        )
                        
                        # 언어 감지 시그널
                        detected_language = metadata.get('language')
                        if detected_language:
                            self.language_detected.emit(detected_language)
                    
                    self.logger.info(f"음성 인식 완료: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                    self.transcription_completed.emit(text, metadata or {})
                else:
                    self.stats['failed_transcriptions'] += 1
                    self.logger.warning("인식된 텍스트가 없습니다")
                    self.transcription_failed.emit("음성을 인식할 수 없습니다. 더 명확하게 말씀해주세요.")
        
        # 워커 생성 및 실행
        worker = WhisperWorker(
            self.model, 
            audio_data, 
            sample_rate,
            options,
            on_transcription_complete
        )
        self.thread_pool.start(worker)
    
    def change_model(self, model_name):
        """향상된 모델 변경"""
        if model_name == self.model_name and self.model is not None:
            self.logger.info(f"동일한 모델이 이미 로드됨: {model_name}")
            return
        
        if model_name not in self.get_available_models():
            error_msg = f"지원하지 않는 모델: {model_name}"
            self.logger.error(error_msg)
            self.model_loading_failed.emit(error_msg)
            return
        
        self.logger.info(f"모델 변경: {self.model_name} -> {model_name}")
        
        # 기존 모델 정리
        if self.model is not None:
            del self.model
            self.model = None
        
        self.model_name = model_name
        
        # 설정에 저장
        config.set('whisper.model_name', model_name)
        config.save_settings()
        
        # 새 모델 로딩
        self.load_model_async()
    
    def get_available_models(self):
        """사용 가능한 모델 목록 반환"""
        return [
            "tiny",      # 최소 모델
            "base",      # 기본 권장
            "small",     # 균형형
            "medium",    # 고품질
            "large",     # 최고 품질
            "large-v2",  # 최신 대형 모델
            "large-v3"   # 최신 대형 모델 v3
        ]
    
    def get_model_info(self, model_name):
        """상세 모델 정보 반환"""
        model_info = {
            "tiny": {
                "size": "39 MB", 
                "speed": "매우 빠름", 
                "accuracy": "낮음",
                "memory": "~1GB",
                "use_case": "빠른 테스트용"
            },
            "base": {
                "size": "74 MB", 
                "speed": "빠름", 
                "accuracy": "보통",
                "memory": "~1GB",
                "use_case": "일반적인 사용 (권장)"
            },
            "small": {
                "size": "244 MB", 
                "speed": "보통", 
                "accuracy": "좋음",
                "memory": "~2GB",
                "use_case": "균형잡힌 성능"
            },
            "medium": {
                "size": "769 MB", 
                "speed": "느림", 
                "accuracy": "매우 좋음",
                "memory": "~5GB",
                "use_case": "고품질 인식"
            },
            "large": {
                "size": "1550 MB", 
                "speed": "매우 느림", 
                "accuracy": "최고",
                "memory": "~10GB",
                "use_case": "최고 품질 (영어)"
            },
            "large-v2": {
                "size": "1550 MB", 
                "speed": "매우 느림", 
                "accuracy": "최고",
                "memory": "~10GB",
                "use_case": "최고 품질 (다국어 개선)"
            },
            "large-v3": {
                "size": "1550 MB", 
                "speed": "매우 느림", 
                "accuracy": "최고",
                "memory": "~10GB",
                "use_case": "최신 최고 품질"
            }
        }
        return model_info.get(model_name, {})
    
    def is_model_loaded(self):
        """모델 로딩 상태 확인"""
        return self.model is not None
    
    def is_model_loading(self):
        """모델 로딩 중 상태 확인"""
        return self.model_loading
    
    def get_current_model(self):
        """현재 모델명 반환"""
        return self.model_name
    
    def get_supported_languages(self):
        """지원하는 언어 목록"""
        return {
            'ko': '한국어',
            'en': 'English',
            'ja': '日本語',
            'zh': '中文',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'ru': 'Русский',
            'auto': '자동 감지'
        }
    
    def change_language(self, language_code):
        """인식 언어 변경"""
        if language_code in self.get_supported_languages():
            self.options['language'] = None if language_code == 'auto' else language_code
            config.set('whisper.language', language_code)
            config.save_settings()
            self.logger.info(f"인식 언어 변경: {language_code}")
        else:
            self.logger.error(f"지원하지 않는 언어: {language_code}")
    
    def get_statistics(self):
        """통계 정보 반환"""
        stats = self.stats.copy()
        if stats['successful_transcriptions'] > 0:
            stats['average_processing_time'] = (
                stats['total_processing_time'] / stats['successful_transcriptions']
            )
            stats['success_rate'] = (
                stats['successful_transcriptions'] / stats['total_transcriptions'] * 100
            )
        else:
            stats['average_processing_time'] = 0.0
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """통계 초기화"""
        self.stats = {
            'total_transcriptions': 0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'total_processing_time': 0.0,
            'average_confidence': 0.0
        }
        self.logger.info("Whisper 통계가 초기화되었습니다")
    
    def _load_whisper_options(self):
        """설정에서 Whisper 옵션 로드"""
        return {
            'language': config.get('whisper.language', 'ko'),
            'task': config.get('whisper.task', 'transcribe'),
            'fp16': config.get('whisper.fp16', False),
            'temperature': config.get('whisper.temperature', 0.0),
            'best_of': config.get('whisper.best_of', 5),
            'beam_size': config.get('whisper.beam_size', 5),
            'silence_threshold': config.get('audio.silence_threshold', 0.01),
            'enable_vad': True,
            'clean_special_chars': False
        }
    
    def _validate_audio_data(self, audio_data):
        """오디오 데이터 유효성 검증"""
        if audio_data is None:
            return "오디오 데이터가 없습니다"
        
        if len(audio_data) == 0:
            return "빈 오디오 데이터입니다"
        
        # 최소 길이 확인 (0.1초)
        if len(audio_data) < 1600:  # 16000 * 0.1
            return "오디오가 너무 짧습니다 (최소 0.1초 필요)"
        
        # 최대 길이 확인 (30초)
        if len(audio_data) > 16000 * 30:
            return "오디오가 너무 깁니다 (최대 30초)"
        
        # 데이터 타입 확인
        if not isinstance(audio_data, np.ndarray):
            return "잘못된 오디오 데이터 형식입니다"
        
        return None
    
    def update_options(self, new_options):
        """Whisper 옵션 업데이트"""
        self.options.update(new_options)
        self.logger.info(f"Whisper 옵션 업데이트: {new_options}")
    
    def get_current_options(self):
        """현재 Whisper 옵션 반환"""
        return self.options.copy()
    
    def force_reload_model(self):
        """모델 강제 재로딩"""
        self.logger.info("모델 강제 재로딩 시작")
        if self.model is not None:
            del self.model
            self.model = None
        self.load_model_async()
    
    def __del__(self):
        """소멸자 - 리소스 정리"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
            if hasattr(self, 'thread_pool'):
                self.thread_pool.waitForDone(3000)  # 3초 대기
        except:
            pass