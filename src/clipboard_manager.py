"""
고급 클립보드 관리 모듈
"""

import logging
import pyperclip
import time
import re
import hashlib
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime, timedelta
from config import config
import json
import os


class ClipboardManager(QObject):
    text_copied = pyqtSignal(str, dict)  # 텍스트, 메타데이터
    clipboard_backup_created = pyqtSignal(str)  # 백업 생성
    clipboard_restored = pyqtSignal(str)  # 복원 완료
    history_updated = pyqtSignal(int)  # 히스토리 업데이트
    copy_failed = pyqtSignal(str)  # 복사 실패
    
    def __init__(self, history_file=None, max_history=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 설정에서 값 로드
        self.history_file = history_file or "clipboard_history.json"
        self.max_history = max_history or config.get('clipboard.max_history', 50)
        self.auto_copy_enabled = config.get('clipboard.auto_copy', True)
        self.backup_enabled = config.get('clipboard.backup_previous', True)
        self.history_enabled = config.get('clipboard.history_enabled', True)
        
        # 내부 상태
        self.history = []
        self.backup_stack = []  # 백업 스택
        self.last_copied_hash = None  # 중복 방지
        self.copy_lock = threading.Lock()  # 동시 접근 방지
        
        # 통계
        self.stats = {
            'total_copies': 0,
            'successful_copies': 0,
            'failed_copies': 0,
            'total_characters': 0,
            'session_start': datetime.now().isoformat()
        }
        
        # 초기화
        self.load_history()
        self.setup_monitoring()
    
    def copy_text(self, text, source="manual", metadata=None):
        """향상된 텍스트를 클립보드에 복사"""
        if not self.auto_copy_enabled and source == "auto":
            self.logger.debug("자동 복사가 비활성화되어 있습니다")
            return False
        
        # 입력 검증
        validation_result = self._validate_text(text)
        if not validation_result['valid']:
            error_msg = f"텍스트 검증 실패: {validation_result['error']}"
            self.logger.warning(error_msg)
            self.copy_failed.emit(error_msg)
            return False
        
        try:
            with self.copy_lock:
                # 통계 업데이트
                self.stats['total_copies'] += 1
                
                # 텍스트 정리
                cleaned_text = self._clean_text(text)
                
                # 중복 검사
                text_hash = self._get_text_hash(cleaned_text)
                if text_hash == self.last_copied_hash:
                    self.logger.debug("중복된 텍스트 복사 시도 무시")
                    return True
                
                # 이전 클립보드 백업
                previous_content = None
                if self.backup_enabled:
                    previous_content = self.get_clipboard_content()
                    if previous_content and previous_content != cleaned_text:
                        self._backup_clipboard(previous_content)
                
                # 복사 실행
                start_time = time.time()
                pyperclip.copy(cleaned_text)
                copy_time = time.time() - start_time
                
                # 복사 확인
                if not self._verify_copy(cleaned_text):
                    raise Exception("복사 후 확인 실패")
                
                # 메타데이터 준비
                copy_metadata = {
                    'source': source,
                    'timestamp': datetime.now().isoformat(),
                    'length': len(cleaned_text),
                    'copy_time': copy_time,
                    'hash': text_hash
                }
                
                if metadata:
                    copy_metadata.update(metadata)
                
                # 히스토리 추가
                if self.history_enabled:
                    self.add_to_history(cleaned_text, previous_content, copy_metadata)
                
                # 통계 업데이트
                self.stats['successful_copies'] += 1
                self.stats['total_characters'] += len(cleaned_text)
                self.last_copied_hash = text_hash
                
                text_preview = cleaned_text[:50] + ('...' if len(cleaned_text) > 50 else '')
                self.logger.info(f"클립보드 복사 성공: '{text_preview}'")
                self.text_copied.emit(cleaned_text, copy_metadata)
                
                return True
                
        except Exception as e:
            self.stats['failed_copies'] += 1
            error_msg = f"클립보드 복사 실패: {e}"
            self.logger.error(error_msg)
            self.copy_failed.emit(error_msg)
            return False
    
    def get_clipboard_content(self):
        """현재 클립보드 내용 가져오기"""
        try:
            return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"클립보드 내용 가져오기 실패: {e}")
            return ""
    
    def add_to_history(self, new_text, previous_text=None, metadata=None):
        """향상된 히스토리에 항목 추가"""
        if not self.history_enabled:
            return
        
        try:
            # 중복 체크 (해시 기반)
            text_hash = self._get_text_hash(new_text)
            if self.history and self.history[0].get('hash') == text_hash:
                self.logger.debug("중복된 항목으로 히스토리 추가 생략")
                return
            
            history_item = {
                'text': new_text,
                'timestamp': datetime.now().isoformat(),
                'hash': text_hash,
                'length': len(new_text),
                'source': metadata.get('source', 'unknown') if metadata else 'unknown',
                'previous_clipboard': previous_text if previous_text else None
            }
            
            # 추가 메타데이터
            if metadata:
                history_item.update({
                    'copy_time': metadata.get('copy_time', 0),
                    'confidence': metadata.get('confidence', None),  # Whisper 신뢰도
                    'language': metadata.get('language', None)  # 감지된 언어
                })
            
            # 최신 항목을 맨 앞에 추가
            self.history.insert(0, history_item)
            
            # 최대 개수 제한
            if len(self.history) > self.max_history:
                removed_items = self.history[self.max_history:]
                self.history = self.history[:self.max_history]
                self.logger.debug(f"{len(removed_items)}개 오래된 항목 제거")
            
            # 파일에 저장 (비동기)
            self._save_history_async()
            
            # 시그널 발송
            self.history_updated.emit(len(self.history))
            
            self.logger.debug(f"히스토리 추가 완료: {len(self.history)}개 항목")
            
        except Exception as e:
            self.logger.error(f"히스토리 추가 실패: {e}")
    
    def get_history(self, limit=None):
        """히스토리 목록 반환"""
        if limit:
            return self.history[:limit]
        return self.history.copy()
    
    def clear_history(self):
        """히스토리 초기화"""
        try:
            self.history = []
            self.save_history()
            self.logger.info("히스토리가 초기화되었습니다")
            
        except Exception as e:
            self.logger.error(f"히스토리 초기화 실패: {e}")
    
    def restore_previous_clipboard(self, method="backup"):
        """향상된 이전 클립보드 내용 복원"""
        try:
            restored_text = None
            
            if method == "backup" and self.backup_stack:
                # 백업 스택에서 복원
                backup_item = self.backup_stack.pop()
                restored_text = backup_item['content']
                self.logger.info(f"백업에서 복원: {backup_item['timestamp']}")
                
            elif method == "history" and self.history:
                # 히스토리에서 복원 (두 번째 항목)
                if len(self.history) > 1:
                    restored_text = self.history[1]['text']
                    self.logger.info("히스토리에서 복원")
                else:
                    self.logger.warning("복원할 히스토리 항목이 부족합니다")
                    
            elif method == "previous" and self.history:
                # 가장 최근 항목의 이전 내용
                previous_text = self.history[0].get('previous_clipboard')
                if previous_text:
                    restored_text = previous_text
                    self.logger.info("이전 내용에서 복원")
                else:
                    self.logger.warning("이전 내용이 없습니다")
            
            if restored_text:
                pyperclip.copy(restored_text)
                self.clipboard_restored.emit(restored_text)
                self.logger.info(f"클립보드 복원 성공: '{restored_text[:50]}{'...' if len(restored_text) > 50 else ''}'")
                return True
            else:
                self.logger.warning(f"복원할 내용을 찾을 수 없습니다 (method: {method})")
                
        except Exception as e:
            self.logger.error(f"클립보드 복원 실패: {e}")
        
        return False
    
    def copy_from_history(self, index):
        """히스토리에서 특정 항목을 클립보드로 복사"""
        try:
            if 0 <= index < len(self.history):
                text = self.history[index]['text']
                pyperclip.copy(text)
                self.logger.info(f"히스토리 항목이 클립보드로 복사됨: {text[:50]}...")
                return True
            else:
                self.logger.warning("잘못된 히스토리 인덱스")
                
        except Exception as e:
            self.logger.error(f"히스토리에서 복사 실패: {e}")
        
        return False
    
    def search_history(self, keyword):
        """히스토리에서 키워드 검색"""
        try:
            keyword = keyword.lower()
            results = []
            
            for i, item in enumerate(self.history):
                if keyword in item['text'].lower():
                    results.append((i, item))
            
            return results
            
        except Exception as e:
            self.logger.error(f"히스토리 검색 실패: {e}")
            return []
    
    def save_history(self):
        """히스토리를 파일에 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"히스토리 저장 실패: {e}")
    
    def load_history(self):
        """파일에서 히스토리 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                    
                self.logger.info(f"히스토리 로드됨: {len(self.history)}개 항목")
            else:
                self.history = []
                self.logger.info("새로운 히스토리 파일 생성")
                
        except Exception as e:
            self.logger.error(f"히스토리 로드 실패: {e}")
            self.history = []
    
    def setup_monitoring(self):
        """클립보드 모니터링 설정"""
        # 주기적 청리 타이머
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_old_items)
        self.cleanup_timer.start(300000)  # 5분마다
        
        self.logger.info("클립보드 모니터링 시작")
    
    def _validate_text(self, text):
        """텍스트 유효성 검증"""
        if not text:
            return {'valid': False, 'error': '빈 텍스트'}
        
        if not text.strip():
            return {'valid': False, 'error': '공백만 포함된 텍스트'}
        
        if len(text) > 100000:  # 100KB 제한
            return {'valid': False, 'error': '텍스트가 너무 깁니다 (최대 100KB)'}
        
        return {'valid': True, 'error': None}
    
    def _clean_text(self, text):
        """텍스트 정리"""
        try:
            # 기본 정리
            cleaned = text.strip()
            
            # 연속된 공백/탭/줄바꿈을 단일 공백으로 정리
            cleaned = re.sub(r'[\s\n\t]+', ' ', cleaned)
            
            # 제어 문자 제거 (인쫼 가능한 것만 남김)
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"텍스트 정리 실패: {e}")
            return text.strip()
    
    def _get_text_hash(self, text):
        """텍스트 해시 생성"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def _backup_clipboard(self, content):
        """클립보드 백업"""
        try:
            if not content or not content.strip():
                return
            
            backup_item = {
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'hash': self._get_text_hash(content)
            }
            
            # 중복 방지
            if self.backup_stack and self.backup_stack[-1]['hash'] == backup_item['hash']:
                return
            
            self.backup_stack.append(backup_item)
            
            # 최대 10개로 제한
            if len(self.backup_stack) > 10:
                self.backup_stack.pop(0)
            
            self.clipboard_backup_created.emit(content)
            self.logger.debug(f"클립보드 백업 생성: {len(content)}자")
            
        except Exception as e:
            self.logger.error(f"클립보드 백업 실패: {e}")
    
    def _verify_copy(self, expected_text):
        """복사 결과 확인"""
        try:
            # 짧은 대기 후 확인
            time.sleep(0.01)
            actual_text = pyperclip.paste()
            return actual_text == expected_text
        except:
            return False
    
    def _save_history_async(self):
        """비동기 히스토리 저장"""
        def save_worker():
            try:
                self.save_history()
            except Exception as e:
                self.logger.error(f"비동기 히스토리 저장 실패: {e}")
        
        thread = threading.Thread(target=save_worker, daemon=True)
        thread.start()
    
    def _cleanup_old_items(self):
        """오래된 항목 정리"""
        try:
            if not self.history:
                return
            
            # 30일 이상 된 항목 제거
            cutoff_date = datetime.now() - timedelta(days=30)
            
            original_count = len(self.history)
            self.history = [item for item in self.history 
                          if datetime.fromisoformat(item['timestamp']) > cutoff_date]
            
            removed_count = original_count - len(self.history)
            if removed_count > 0:
                self.logger.info(f"{removed_count}개 오래된 항목 정리")
                self._save_history_async()
            
            # 백업 스택 정리 (10개 이상이면)
            if len(self.backup_stack) > 10:
                removed_backups = len(self.backup_stack) - 10
                self.backup_stack = self.backup_stack[-10:]
                self.logger.debug(f"{removed_backups}개 오래된 백업 제거")
                
        except Exception as e:
            self.logger.error(f"오래된 항목 정리 실패: {e}")
    
    def toggle_auto_copy(self):
        """자동 복사 토글"""
        self.auto_copy_enabled = not self.auto_copy_enabled
        config.set('clipboard.auto_copy', self.auto_copy_enabled)
        config.save_settings()
        
        status = "활성화" if self.auto_copy_enabled else "비활성화"
        self.logger.info(f"자동 복사 {status}")
        return self.auto_copy_enabled
    
    def toggle_history(self):
        """히스토리 기능 토글"""
        self.history_enabled = not self.history_enabled
        config.set('clipboard.history_enabled', self.history_enabled)
        config.save_settings()
        
        status = "활성화" if self.history_enabled else "비활성화"
        self.logger.info(f"히스토리 기능 {status}")
        return self.history_enabled
    
    def get_backup_history(self):
        """백업 히스토리 반환"""
        return self.backup_stack.copy()
    
    def export_history(self, format="json", limit=None):
        """히스토리 내보내기"""
        try:
            items = self.history[:limit] if limit else self.history
            
            if format == "json":
                return json.dumps(items, ensure_ascii=False, indent=2)
            elif format == "txt":
                lines = []
                for item in items:
                    timestamp = item['timestamp']
                    text = item['text']
                    lines.append(f"[{timestamp}] {text}")
                return "\n".join(lines)
            elif format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['timestamp', 'text', 'length', 'source'])
                for item in items:
                    writer.writerow([
                        item['timestamp'],
                        item['text'],
                        item.get('length', len(item['text'])),
                        item.get('source', 'unknown')
                    ])
                return output.getvalue()
            else:
                raise ValueError(f"지원하지 않는 포맷: {format}")
                
        except Exception as e:
            self.logger.error(f"히스토리 내보내기 실패: {e}")
            return None
    
    def import_history(self, data, format="json"):
        """히스토리 가져오기"""
        try:
            if format == "json":
                imported_items = json.loads(data)
                # 기존 히스토리와 병합
                for item in reversed(imported_items):
                    if 'text' in item and 'timestamp' in item:
                        self.history.insert(0, item)
                
                # 중복 제거 및 정리
                seen_hashes = set()
                unique_history = []
                for item in self.history:
                    item_hash = item.get('hash') or self._get_text_hash(item['text'])
                    if item_hash not in seen_hashes:
                        seen_hashes.add(item_hash)
                        unique_history.append(item)
                
                self.history = unique_history[:self.max_history]
                self.save_history()
                self.logger.info(f"{len(imported_items)}개 항목 가져오기 완료")
                return True
            else:
                raise ValueError(f"지원하지 않는 포맷: {format}")
                
        except Exception as e:
            self.logger.error(f"히스토리 가져오기 실패: {e}")
            return False
    
    def __del__(self):
        """소멸자 - 리소스 정리"""
        try:
            if hasattr(self, 'cleanup_timer'):
                self.cleanup_timer.stop()
            # 최종 저장
            if hasattr(self, 'history') and self.history:
                self.save_history()
        except:
            pass
    
    def get_statistics(self):
        """상세 통계 정보 반환"""
        try:
            stats = self.stats.copy()
            
            if self.history:
                # 히스토리 통계
                total_items = len(self.history)
                total_chars = sum(len(item['text']) for item in self.history)
                avg_chars = total_chars // total_items if total_items > 0 else 0
                
                # 날짜 범위
                timestamps = [datetime.fromisoformat(item['timestamp']) for item in self.history]
                latest_date = max(timestamps).isoformat() if timestamps else None
                oldest_date = min(timestamps).isoformat() if timestamps else None
                
                # 소스별 통계
                source_counts = {}
                for item in self.history:
                    source = item.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                # 통계 병합
                stats.update({
                    'history_items': total_items,
                    'history_characters': total_chars,
                    'average_characters': avg_chars,
                    'latest_date': latest_date,
                    'oldest_date': oldest_date,
                    'source_distribution': source_counts,
                    'backup_count': len(self.backup_stack),
                    'success_rate': (stats['successful_copies'] / stats['total_copies'] * 100) if stats['total_copies'] > 0 else 0
                })
            
            # 세션 다럈
            session_start = datetime.fromisoformat(stats['session_start'])
            session_duration = datetime.now() - session_start
            stats['session_duration_minutes'] = session_duration.total_seconds() / 60
            
            return stats
            
        except Exception as e:
            self.logger.error(f"통계 정보 생성 실패: {e}")
            return self.stats.copy()