"""
시스템 트레이 관리 모듈
"""

import logging
import sys
import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QWidgetAction, QLabel, QFrame
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen, QFont, QAction


class TrayManager(QObject):
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    toggle_requested = pyqtSignal()
    status_info_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 시스템 트레이 지원 확인
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.error("시스템 트레이를 사용할 수 없습니다")
            sys.exit(1)
        
        self.tray_icon = QSystemTrayIcon()
        self.current_status = 'idle'
        self.is_paused = False
        self.recording_count = 0
        
        self.setup_icons()
        self.setup_menu()
        self.setup_tray_icon()
        
        # 상태 업데이트 타이머
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # 1초마다 상태 업데이트
    
    def setup_icons(self):
        """향상된 상태별 아이콘 생성"""
        self.icons = {}
        icon_size = 22  # 더 큰 아이콘
        
        # 고품질 아이콘들
        self.icons['idle'] = self.create_microphone_icon(QColor(100, 100, 100), icon_size)        # 회색 마이크
        self.icons['recording'] = self.create_microphone_icon(QColor(220, 50, 50), icon_size)    # 빨간 마이크
        self.icons['processing'] = self.create_microphone_icon(QColor(255, 165, 0), icon_size)   # 주황 마이크
        self.icons['paused'] = self.create_microphone_icon(QColor(160, 160, 160), icon_size)     # 연회색 마이크
        self.icons['error'] = self.create_microphone_icon(QColor(180, 50, 50), icon_size, True)  # 에러 표시
        
        # 애니메이션용 타이머 (녹음 중 깜빡임)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_recording_icon)
        self.animation_state = False
    
    def create_microphone_icon(self, color, size=22, is_error=False):
        """마이크 모양 아이콘 생성"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # 투명 배경
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 마이크 몸체 (캡슐 모양)
        mic_width = size // 3
        mic_height = size // 2
        mic_x = (size - mic_width) // 2
        mic_y = size // 6
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, mic_width//2, mic_width//2)
        
        # 마이크 스탠드
        stand_x = size // 2
        stand_y = mic_y + mic_height
        painter.drawLine(stand_x, stand_y, stand_x, stand_y + size//4)
        
        # 마이크 베이스
        base_width = size // 2
        base_y = stand_y + size//4
        painter.drawLine(stand_x - base_width//2, base_y, stand_x + base_width//2, base_y)
        
        # 에러 표시 (빨간 X)
        if is_error:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(2, 2, size-2, size-2)
            painter.drawLine(2, size-2, size-2, 2)
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_menu(self):
        """향상된 컨텍스트 메뉴 설정"""
        self.menu = QMenu()
        self.menu.setToolTipsVisible(True)
        
        # 상태 표시 영역 (비활성화된 액션)
        self.status_action = self.menu.addAction("🎤 대기중...")
        self.status_action.setEnabled(False)
        
        # 녹음 횟수 표시
        self.count_action = self.menu.addAction(f"📊 녹음 횟수: {self.recording_count}")
        self.count_action.setEnabled(False)
        
        self.menu.addSeparator()
        
        # 일시정지/재개 토글
        self.toggle_action = self.menu.addAction("⏸️ 일시정지")
        self.toggle_action.setToolTip("음성 인식을 일시적으로 중지합니다")
        self.toggle_action.triggered.connect(self.on_toggle_requested)
        
        self.menu.addSeparator()
        
        # 상태 정보
        self.info_action = self.menu.addAction("ℹ️ 상태 정보")
        self.info_action.setToolTip("현재 시스템 상태를 확인합니다")
        self.info_action.triggered.connect(self.status_info_requested.emit)
        
        # 설정
        self.settings_action = self.menu.addAction("⚙️ 설정")
        self.settings_action.setToolTip("프로그램 설정을 변경합니다")
        self.settings_action.triggered.connect(self.settings_requested.emit)
        
        self.menu.addSeparator()
        
        # 정보
        self.about_action = self.menu.addAction("📖 정보")
        self.about_action.setToolTip("프로그램 정보를 확인합니다")
        self.about_action.triggered.connect(self.show_about)
        
        # 종료
        self.quit_action = self.menu.addAction("❌ 종료")
        self.quit_action.setToolTip("프로그램을 종료합니다")
        self.quit_action.triggered.connect(self.quit_requested.emit)
    
    def setup_tray_icon(self):
        """향상된 트레이 아이콘 설정"""
        self.tray_icon.setIcon(self.icons['idle'])
        self.update_tooltip()
        self.tray_icon.setContextMenu(self.menu)
        
        # 클릭 이벤트
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def show(self):
        """트레이 아이콘 표시"""
        self.tray_icon.show()
        self.logger.info("시스템 트레이 아이콘 표시됨")
        
        # 시작 알림
        self.show_message(
            "🎤 음성 받아쓰기 프로그램",
            "프로그램이 시작되었습니다.\n\n단축키: Ctrl+Alt+Space\n우클릭으로 메뉴를 확인하세요.",
            QSystemTrayIcon.MessageIcon.Information
        )
        
        return QApplication.instance().exec()
    
    def hide(self):
        """트레이 아이콘 숨김"""
        self.tray_icon.hide()
        self.animation_timer.stop()
    
    def set_status(self, status, extra_info=None):
        """향상된 상태 변경"""
        if status == self.current_status and not extra_info:
            return
        
        prev_status = self.current_status
        self.current_status = status
        
        # 애니메이션 중지
        self.animation_timer.stop()
        
        # 녹음 횟수 업데이트
        if prev_status == 'recording' and status != 'recording':
            self.recording_count += 1
            self.count_action.setText(f"📊 녹음 횟수: {self.recording_count}")
        
        # 일시정지 상태 확인
        if self.is_paused:
            icon_key = 'paused'
            status_text = "⏸️ 일시정지됨"
        elif status == 'idle':
            icon_key = 'idle'
            status_text = "🎤 대기중..."
        elif status == 'recording':
            icon_key = 'recording'
            status_text = "🔴 녹음중..."
            # 깜빡임 애니메이션 시작
            self.animation_timer.start(600)  # 600ms 간격
        elif status == 'processing':
            icon_key = 'processing'
            status_text = "⚡ 음성인식중..."
        elif status == 'error':
            icon_key = 'error'
            status_text = "❌ 오류발생"
        else:
            icon_key = 'idle'
            status_text = f"❓ {status}"
        
        # 아이콘 및 상태 텍스트 업데이트
        self.tray_icon.setIcon(self.icons[icon_key])
        self.status_action.setText(status_text)
        self.update_tooltip(extra_info)
        
        self.logger.debug(f"트레이 상태 변경: {prev_status} -> {status}")
    
    def animate_recording_icon(self):
        """녹음 중 아이콘 애니메이션"""
        if self.current_status != 'recording':
            self.animation_timer.stop()
            return
        
        if self.animation_state:
            self.tray_icon.setIcon(self.icons['recording'])
        else:
            self.tray_icon.setIcon(self.icons['idle'])
        
        self.animation_state = not self.animation_state
    
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, duration=4000):
        """향상된 트레이 알림 메시지 표시"""
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon, duration)
        else:
            self.logger.warning("시스템이 트레이 메시지를 지원하지 않습니다")
            # 콘솔에라도 메시지 출력
            print(f"[{title}] {message}")
    
    def on_tray_activated(self, reason):
        """향상된 트레이 아이콘 클릭 이벤트"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 더블클릭시 일시정지/재개 토글
            self.on_toggle_requested()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # 중간클릭시 상태 정보 표시
            self.status_info_requested.emit()
    
    def show_about(self):
        """향상된 정보 대화상자 표시"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle("🎤 음성 받아쓰기 프로그램 정보")
        msg.setText(
            "<h3>🎤 음성 받아쓰기 프로그램 v1.0</h3>"
            "<p><b>OpenAI Whisper</b>를 사용한 고품질 음성-텍스트 변환</p>"
            "<hr>"
            "<p><b>🎯 주요 기능:</b></p>"
            "<ul>"
            "<li>실시간 음성 인식</li>"
            "<li>자동 클립보드 복사</li>"
            "<li>시스템 트레이 통합</li>"
            "<li>전역 단축키 지원</li>"
            "</ul>"
            "<p><b>⌨️ 단축키:</b> Ctrl+Alt+Space</p>"
            "<p><b>📝 사용법:</b></p>"
            "<ol>"
            "<li>Ctrl+Alt+Space를 누르고 있는 동안 말하기</li>"
            "<li>키를 놓으면 자동으로 음성 인식 시작</li>"
            "<li>인식된 텍스트가 클립보드로 복사됨</li>"
            "</ol>"
            f"<p><b>📊 현재 세션:</b> {self.recording_count}회 녹음</p>"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setTextFormat(1)  # RichText 형식
        msg.exec()
    
    def update_tooltip(self, extra_info=None):
        """툴팁 업데이트"""
        base_tooltip = "🎤 음성 받아쓰기 프로그램"
        
        if self.is_paused:
            status_line = "\n⏸️ 상태: 일시정지됨"
        elif self.current_status == 'idle':
            status_line = "\n✅ 상태: 대기중"
        elif self.current_status == 'recording':
            status_line = "\n🔴 상태: 녹음중"
        elif self.current_status == 'processing':
            status_line = "\n⚡ 상태: 음성인식중"
        else:
            status_line = f"\n❓ 상태: {self.current_status}"
        
        shortcut_line = "\n⌨️ 단축키: Ctrl+Alt+Space"
        count_line = f"\n📊 세션 녹음: {self.recording_count}회"
        
        tooltip = base_tooltip + status_line + shortcut_line + count_line
        
        if extra_info:
            tooltip += f"\n💡 {extra_info}"
        
        tooltip += "\n\n우클릭: 메뉴 | 더블클릭: 일시정지토글"
        
        self.tray_icon.setToolTip(tooltip)
    
    def on_toggle_requested(self):
        """일시정지/재개 토글 처리"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.toggle_action.setText("▶️ 재개")
            self.toggle_action.setToolTip("음성 인식을 재개합니다")
            self.show_message(
                "⏸️ 일시정지",
                "음성 인식이 일시정지되었습니다.\n더블클릭하여 재개할 수 있습니다.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.toggle_action.setText("⏸️ 일시정지")
            self.toggle_action.setToolTip("음성 인식을 일시적으로 중지합니다")
            self.show_message(
                "▶️ 재개",
                "음성 인식이 재개되었습니다.\nCtrl+Alt+Space로 녹음을 시작하세요.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        
        # 상태 업데이트
        self.set_status(self.current_status)
        self.toggle_requested.emit()
        
        self.logger.info(f"트레이 토글: {'일시정지' if self.is_paused else '재개'}")
    
    def update_status_display(self):
        """주기적 상태 표시 업데이트"""
        # 툴팁만 업데이트 (너무 자주 변경되지 않도록)
        if hasattr(self, 'last_tooltip_update'):
            import time
            if time.time() - self.last_tooltip_update < 5:  # 5초 간격
                return
        
        self.update_tooltip()
        import time
        self.last_tooltip_update = time.time()
    
    def get_status_info(self):
        """현재 상태 정보 반환"""
        return {
            'current_status': self.current_status,
            'is_paused': self.is_paused,
            'recording_count': self.recording_count,
            'animation_running': self.animation_timer.isActive()
        }
    
    def reset_session_stats(self):
        """세션 통계 초기화"""
        self.recording_count = 0
        self.count_action.setText(f"📊 녹음 횟수: {self.recording_count}")
        self.update_tooltip()
        self.logger.info("세션 통계가 초기화되었습니다")
    
    def __del__(self):
        """소멸자"""
        try:
            if hasattr(self, 'animation_timer'):
                self.animation_timer.stop()
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
        except:
            pass