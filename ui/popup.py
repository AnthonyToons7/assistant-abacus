import os
import signal
import json
import random
import math
import numpy as np
import time 
import tkinter as tk
import threading
import subprocess
import pyaudio
import winsound
import sys, os
import struct
import time
import simpleaudio as sa

from winotify import Notification, audio
from win32api import *
from win32gui import *
import win32con
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QOpenGLWidget, QGraphicsOpacityEffect, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFrame, QScrollArea, QShortcut
from PyQt5.QtGui import QPixmap, QFont, QImage, QSurfaceFormat, QColor, QPainter, QBrush, QPen, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal

from OpenGL.GL import *
from OpenGL.GLU import *

from core.translations import load_translations, t
from core.storage import get_saved_settings, get_user_data, set_user_data
from core.settings import save_settings
from ui.settings_ui import open_settings_window

signal.signal(signal.SIGINT, signal.SIG_DFL)

def create_window(title, size="300x200", topmost=True):
    modal = tk.Tk()
    modal.title(title)
    modal.geometry(size)
    modal.grab_set()

    if topmost:
        modal.attributes("-topmost", True)

    return modal

def create_element(parent, widget_type, **kwargs):
    widget = widget_type(parent, **kwargs)
    widget.pack()
    return widget

def open_manual_input(prompt=None):
    result = {"text": None}
    def submit():
        result['text'] = entry.get()

    window = create_window(t("manual_input_title"), size="400x150")
    label = create_element(window, tk.Label, text=prompt if prompt else t("manual_input_prompt"))
    entry = create_element(window, tk.Entry)
    submit_btn = create_element(window, tk.Button, text=t("submit"), command=submit)

    window.mainloop()
    return result['text']


def show_settings_panel(save_callback=save_settings, setting_actions=None, initial_tab="settings"):
    launcher_path = os.path.join(os.path.dirname(__file__), "settings_launcher.py")
    subprocess.Popen([sys.executable, launcher_path, initial_tab], cwd=os.path.dirname(os.path.dirname(__file__)))

class AbacusSprite(QLabel):
    def __init__(
        self,
        on_click=None,
        frame_count=8,
        sheet_dir="data/img/Slime-sheet.png",
        fps=10
    ):
        self.on_click = on_click
        self.chat_dock = None
        self.drag_enabled = False
        self.dragging = False
        self.drag_offset = QPoint()
        self.hotkey_enabled = False
        self._hotkey_shortcut = None
        self.drag_controls = None
        self.drag_origin_pos = None
        super().__init__()

        self.sheet = QPixmap(sheet_dir)
        if self.sheet.isNull():
            print("Failed to load sprite sheet!")
            return

        self.frame_count = frame_count
        self.current_frame = 0

        self.frame_width = self.sheet.width() // frame_count
        self.frame_height = self.sheet.height()

        self.display_width = 150
        self.display_height = int(self.frame_height * (self.display_width / self.frame_width))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(int(1000 / fps))

        self.update_frame()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.screen = QApplication.primaryScreen().geometry()
        self.move(
            self.screen.width() - self.display_width - -10,
            self.screen.height() - self.display_height - 40
        )

        self.default_pos = QPoint(
            self.screen.width() - self.display_width - 10,
            self.screen.height() - self.display_height - 40
        )
        self.move(self.default_pos)
        self.setup_hotkey()
        self.show()

    def attach_chat_dock(self, chat_dock):
        self.chat_dock = chat_dock

    def setup_hotkey(self):
        if self._hotkey_shortcut is not None:
            return
        self._hotkey_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Shift+A"), self)
        self._hotkey_shortcut.activated.connect(self._trigger_hotkey_action)

    def _build_drag_controls(self):
        if self.drag_controls is not None:
            return self.drag_controls

        self.drag_controls = QWidget(self)
        self.drag_controls.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_controls.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.drag_controls.setFixedSize(112, 32)
        self.drag_controls.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self.drag_controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        confirm_btn = QPushButton("✓", self.drag_controls)
        confirm_btn.setFixedSize(48, 28)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(
            "QPushButton { background: #2ecc71; color: white; border: none; border-radius: 10px; font: 11px 'Segoe UI Semibold'; }"
            "QPushButton:hover { background: #27ae60; }"
        )
        confirm_btn.clicked.connect(self.confirm_drag_position)

        cancel_btn = QPushButton("✕", self.drag_controls)
        cancel_btn.setFixedSize(48, 28)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(
            "QPushButton { background: #e74c3c; color: white; border: none; border-radius: 10px; font: 11px 'Segoe UI Semibold'; }"
            "QPushButton:hover { background: #c0392b; }"
        )
        cancel_btn.clicked.connect(self.cancel_drag_position)

        layout.addWidget(confirm_btn)
        layout.addWidget(cancel_btn)
        return self.drag_controls

    def show_drag_controls(self):
        controls = self._build_drag_controls()
        controls.move(self.width() // 2 - controls.width() // 2, -38)
        controls.raise_()
        controls.show()

    def hide_drag_controls(self):
        if self.drag_controls is not None:
            self.drag_controls.hide()

    def _trigger_hotkey_action(self):
        if not self.hotkey_enabled:
            return
        if self.chat_dock is not None:
            self.chat_dock.show_chat()
            self.chat_dock.focus_input()
        else:
            self.prompt_window = PromptInputWindow()
            self.prompt_window.show()

    def set_hotkey_enabled(self, enabled):
        self.hotkey_enabled = bool(enabled)
        self.setToolTip("Hotkey ready" if self.hotkey_enabled else "Hotkey disabled")

    def enter_drag_mode(self):
        self.drag_enabled = True
        self.dragging = False
        self.drag_origin_pos = self.pos()
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip("Drag mode enabled — move me around")
        self.show_drag_controls()

    def persist_sprite_position(self):
        data = dict(get_saved_settings())
        data["sprite_position"] = [int(self.pos().x()), int(self.pos().y())]
        save_settings(data)

    def confirm_drag_position(self):
        self.hide_drag_controls()
        self.drag_enabled = False
        self.dragging = False
        self.default_pos = self.pos()
        self.persist_sprite_position()
        self.setCursor(Qt.ArrowCursor)

    def cancel_drag_position(self):
        self.hide_drag_controls()
        self.drag_enabled = False
        self.dragging = False
        if self.drag_origin_pos is not None:
            self.move(self.drag_origin_pos)
            self.default_pos = self.drag_origin_pos
        self.setCursor(Qt.ArrowCursor)

    def apply_saved_settings(self, saved=None):
        saved = saved or get_saved_settings()
        should_show = bool(saved.get("toggle_sprite", True))
        self.setVisible(should_show)

        sprite_position = saved.get("sprite_position")
        if isinstance(sprite_position, (list, tuple)) and len(sprite_position) >= 2:
            x = int(sprite_position[0])
            y = int(sprite_position[1])
            self.move(x, y)
            self.default_pos = QPoint(x, y)

        self.set_hotkey_enabled(bool(saved.get("hotkey_activation", False)))

    def handle_settings_save(self, data):
        save_settings(data)
        self.apply_saved_settings(data)

    def handle_setting_action(self, key):
        if key == "drag_to_move_sprite":
            self.enter_drag_mode()
            return

        if key == "hotkey_activation":
            next_value = not bool(get_saved_settings().get("hotkey_activation", False))
            data = dict(get_saved_settings())
            data[key] = next_value
            self.handle_settings_save(data)
            self.set_hotkey_enabled(next_value)

    def jump_on_notif(self, height=100, duration=500):
        """Animate sprite to jump up 'height' pixels"""
        if not self.isVisible():
            return
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(self.pos().x(), self.pos().y() - height))
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()

    def fall_back(self, duration=500):
        """Animate sprite falling back to original position"""
        if not self.isVisible():
            return
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(self.default_pos)
        self.anim.setEasingCurve(QEasingCurve.InQuad)
        self.anim.start()

    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.update_frame()

    def update_frame(self):
        frame_rect = QRect(
            self.current_frame * self.frame_width,
            0,
            self.frame_width,
            self.frame_height
        )

        frame = self.sheet.copy(frame_rect)
        frame = frame.scaled(
            self.display_width,
            self.display_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setPixmap(frame)
        self.location = 0
        self.direction = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drag_enabled:
                self.dragging = True
                self.drag_offset = event.globalPos() - self.pos()
                event.accept()
                return
            if self.on_click:
                self.on_click()
            if self.chat_dock is not None:
                self.chat_dock.show_chat()
                self.chat_dock.focus_input()
            else:
                self.prompt_window = PromptInputWindow()
                self.prompt_window.show()
        elif event.button() == Qt.MiddleButton:
            if self.chat_dock:
                self.chat_dock.show_chat()
                self.chat_dock.focus_input()
            else:
                self.prompt_window = PromptInputWindow()
                self.prompt_window.show()
        elif event.button() == Qt.RightButton:
            show_settings_panel(
                self.handle_settings_save,
                setting_actions={
                    "drag_to_move_sprite": lambda: self.handle_setting_action("drag_to_move_sprite"),
                    "hotkey_activation": lambda: self.handle_setting_action("hotkey_activation"),
                },
            )

    def _get_clamped_position(self, x, y):
        screen = QApplication.primaryScreen().availableGeometry()
        max_x = max(0, screen.width() - self.display_width)
        max_y = max(0, screen.height() - self.display_height - 8)
        x = max(0, min(int(x), max_x))
        y = max(0, min(int(y), max_y))
        return x, y

    def mouseMoveEvent(self, event):
        if self.drag_enabled and self.dragging:
            new_pos = event.globalPos() - self.drag_offset
            clamped_x, clamped_y = self._get_clamped_position(new_pos.x(), new_pos.y())
            self.move(QPoint(clamped_x, clamped_y))
            self.default_pos = QPoint(clamped_x, clamped_y)
            if self.drag_controls is not None:
                self.drag_controls.move(self.width() // 2 - self.drag_controls.width() // 2, -38)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.drag_enabled and self.dragging:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)
            self.show_drag_controls()
            event.accept()
            return

class PromptInputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(420)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        card = QWidget(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            QWidget#card {
                background-color: rgba(12, 20, 44, 225);
                border: 1px solid rgba(110, 163, 255, 130);
                border-radius: 18px;
            }
        """)
        self.layout.addWidget(card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(9)

        self.suggestion_templates = {
            "Startup": "startup",
            "Play Music": "play the song <song name>",
            "Web Search": "search <query>",
        }

        title_row = QHBoxLayout()
        title = QLabel("Message A.B.A.C.U.S.", card)
        title.setStyleSheet("color: #d6e5ff; font: 10px 'Segoe UI Semibold'; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()

        close_btn = QPushButton("✕", card)
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9fb8e4;
                border: none;
                font: bold 11px 'Segoe UI';
            }
            QPushButton:hover {
                color: #ffffff;
                background: #2a65df;
                border-radius: 8px;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_row.addWidget(close_btn)
        inner.addLayout(title_row)

        line = QWidget(card)
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(110, 163, 255, 90);")
        inner.addWidget(line)

        suggestion_row = QHBoxLayout()
        suggestion_row.setContentsMargins(0, 0, 0, 0)
        suggestion_row.setSpacing(6)

        for suggestion, template in self.suggestion_templates.items():
            suggestion_btn = QPushButton(suggestion, card)
            suggestion_btn.setCursor(Qt.PointingHandCursor)
            suggestion_btn.setStyleSheet(
                """
                QPushButton {
                    color: #d9e3f7;
                    background: rgba(165, 171, 184, 70);
                    border: 1px solid rgba(192, 198, 214, 95);
                    border-radius: 10px;
                    padding: 4px 10px;
                    font: 9px 'Segoe UI Semibold';
                }
                QPushButton:hover {
                    background: rgba(194, 201, 214, 95);
                    border: 1px solid rgba(218, 224, 236, 145);
                    color: #ffffff;
                }
                """
            )
            suggestion_btn.clicked.connect(lambda _=False, t=template: self.handle_suggestion_click(t))
            suggestion_row.addWidget(suggestion_btn)

        suggestion_row.addStretch()
        inner.addLayout(suggestion_row)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 2, 0, 0)
        input_row.setSpacing(8)

        self.input = QLineEdit(card)
        self.input.setPlaceholderText("Message A.B.A.C.U.S....")
        self.input.setStyleSheet("""
            QLineEdit {
                background: rgba(8, 18, 41, 220);
                color: white;
                border: 1px solid rgba(122, 170, 255, 180);
                border-radius: 17px;
                padding: 8px 12px;
                font: 11px 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #6ea3ff; }
        """)
        self.input.returnPressed.connect(self.submit)
        input_row.addWidget(self.input, 1)

        submit_btn = QPushButton("➤", card)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setFixedSize(34, 34)
        submit_btn.setStyleSheet("""
            QPushButton {
                color: #dff0ff;
                background: #2a65df;
                border: none;
                border-radius: 11px;
                font: 11px 'Segoe UI Semibold';
            }
            QPushButton:hover { background: #3b78ef; }
        """)
        submit_btn.clicked.connect(self.submit)
        input_row.addWidget(submit_btn)
        inner.addLayout(input_row)

        self.adjustSize()
        self.position_near_sprite()
        self.input.setFocus()

    def position_near_sprite(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20,
                  screen.height() - self.height() - 220)

    def handle_suggestion_click(self, template):
        text = str(template or "").strip()
        if not text:
            return
        self.input.setText(text)
        self.input.setFocus()

        placeholder_index = text.find("<")
        if placeholder_index != -1:
            self.input.setCursorPosition(placeholder_index)
        else:
            self.input.setCursorPosition(len(text))

    def submit(self):
        text = self.input.text().strip()
        if not text:
            return
        ai_mode_enabled = bool(get_saved_settings()["ai_mode"])
        if not ai_mode_enabled:
            self.close()
        else:
            self.input.clear()
            self.input.setFocus()
        from core.pipeline import get_on_speech 
        handler = get_on_speech()
        if handler:
            threading.Thread(target=handler, args=(text,'manual'), daemon=True).start()


class ChatBubble(QFrame):
    def __init__(self, role, text, parent=None):
        super().__init__(parent)
        self.role = role
        self.setObjectName("chatBubble")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)

        bubble = QLabel(text, self)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setMaximumWidth(250)
        bubble.setStyleSheet(
            """
            QLabel {
                color: white;
                border-radius: 16px;
                padding: 10px 12px;
                font: 14px 'Segoe UI';
            }
            """
        )

        if role == "user":
            bubble.setStyleSheet(
                bubble.styleSheet() +
                "QLabel {"
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23a138, stop:1 #47c47f);"
                "}"
            )
            row.addStretch()
            row.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                bubble.styleSheet() +
                "QLabel {"
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6116c4, stop:1 #2e67e0);"
                "}"
            )
            row.addWidget(bubble)
            row.addStretch()

        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)

    def animate_in(self):
        current_pos = self.pos()
        start_offset = QPoint(12, 14) if self.role == "user" else QPoint(-12, 14)
        self.move(current_pos + start_offset)

        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(320)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.slide_anim = QPropertyAnimation(self, b"pos", self)
        self.slide_anim.setDuration(320)
        self.slide_anim.setStartValue(self.pos())
        self.slide_anim.setEndValue(current_pos)
        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.fade_anim.start()
        self.slide_anim.start()


class TypingBubble(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("typingBubble")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)

        self.bubble = QFrame(self)
        self.bubble.setFixedSize(72, 40)
        self.bubble.setStyleSheet(
            "QFrame {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6116c4, stop:1 #2e67e0);"
            "border-radius: 16px;"
            "}"
        )
        row.addWidget(self.bubble)
        row.addStretch()

        self.dot_x_positions = [14, 30, 46]
        self.dot_base_y = 17
        self.phase = 0.0
        self.phase_step = 0.17
        self.dot_phase_offset = 1.25
        self.dot_amplitude = 4
        self.dots = []

        for x in self.dot_x_positions:
            dot = QLabel(self.bubble)
            dot.setFixedSize(6, 6)
            dot.setStyleSheet("background: rgba(214, 219, 226, 235); border-radius: 3px;")
            dot.move(x, self.dot_base_y)
            dot.show()
            self.dots.append(dot)

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)

    def _tick(self):
        for i, dot in enumerate(self.dots):
            dot_phase = self.phase - (i * self.dot_phase_offset)
            float_offset = (math.sin(dot_phase) + 1.0) / 2.0
            y = self.dot_base_y - int(round(float_offset * self.dot_amplitude))
            dot.move(self.dot_x_positions[i], y)
        self.phase += self.phase_step

    def animate_in(self):
        current_pos = self.pos()
        self.move(current_pos + QPoint(-8, 10))

        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(80)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.slide_anim = QPropertyAnimation(self, b"pos", self)
        self.slide_anim.setDuration(80)
        self.slide_anim.setStartValue(self.pos())
        self.slide_anim.setEndValue(current_pos)
        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.fade_anim.start()
        self.slide_anim.start()

    def stop_animation(self):
        self.timer.stop()


class ChatDock(QWidget):
    append_message_signal = pyqtSignal(str, str, str)
    set_typing_state_signal = pyqtSignal(bool)

    def __init__(self, sprite):
        super().__init__()
        self.sprite = sprite
        self.is_hidden = False
        self.show_background = False
        self.top_margin = 100
        self.right_margin = 24
        self.visible_x = 0
        self.visible_y = 0
        self.hidden_x = 0
        self.ui_anims = []
        self.scroll_anim = None
        self.is_typing = False
        self.typing_bubble = None
        self.suggestion_templates = {
            "Startup": "startup",
            "Play Music": "play the song <song name>",
            "Web Search": "search <query>",
        }

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(420)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame(self)
        self.card.setObjectName("chatCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        outer.addWidget(self.card)

        header = QWidget(self.card)
        header.setObjectName("chatHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 10, 10, 8)
        self.session_label = QLabel("Session: pending", header)
        self.session_label.setStyleSheet("color: #d6e5ff; font: 10px 'Segoe UI Semibold';")
        header_layout.addWidget(self.session_label)
        header_layout.addStretch()

        self.settings_btn = QPushButton("Settings", header)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setFixedSize(58, 22)
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)

        self.schedule_btn = QPushButton("Schedule", header)
        self.schedule_btn.setCursor(Qt.PointingHandCursor)
        self.schedule_btn.setFixedSize(66, 22)
        self.schedule_btn.clicked.connect(self.open_schedule)
        header_layout.addWidget(self.schedule_btn)

        self.bg_toggle = QPushButton("Background", header)
        self.bg_toggle.setCursor(Qt.PointingHandCursor)
        self.bg_toggle.setFixedSize(78, 22)
        self.bg_toggle.clicked.connect(self.toggle_background)
        header_layout.addWidget(self.bg_toggle)
        card_layout.addWidget(header)

        self.scroll = QScrollArea(self.card)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; }")
        self.scroll.verticalScrollBar().setSingleStep(20)
        self.scroll_contents = QWidget()
        self.scroll_contents.setObjectName("scrollContents")
        self.messages_layout = QVBoxLayout(self.scroll_contents)
        self.messages_layout.setContentsMargins(10, 8, 10, 8)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()
        self.scroll.setWidget(self.scroll_contents)
        card_layout.addWidget(self.scroll, 1)

        input_wrap = QWidget(self.card)
        input_wrap.setObjectName("chatInputWrap")
        input_outer = QVBoxLayout(input_wrap)
        input_outer.setContentsMargins(10, 8, 10, 10)
        input_outer.setSpacing(6)

        suggestion_row = QHBoxLayout()
        suggestion_row.setContentsMargins(0, 0, 0, 0)
        suggestion_row.setSpacing(6)

        for suggestion, template in self.suggestion_templates.items():
            suggestion_btn = QPushButton(suggestion, input_wrap)
            suggestion_btn.setCursor(Qt.PointingHandCursor)
            suggestion_btn.setStyleSheet(
                """
                QPushButton {
                    color: #d9e3f7;
                    background: rgba(165, 171, 184, 70);
                    border: 1px solid rgba(192, 198, 214, 95);
                    border-radius: 10px;
                    padding: 4px 10px;
                    font: 9px 'Segoe UI Semibold';
                }
                QPushButton:hover {
                    background: rgba(194, 201, 214, 95);
                    border: 1px solid rgba(218, 224, 236, 145);
                    color: #ffffff;
                }
                """
            )
            suggestion_btn.clicked.connect(lambda _=False, t=template: self.handle_suggestion_click(t))
            suggestion_row.addWidget(suggestion_btn)

        suggestion_row.addStretch()
        input_outer.addLayout(suggestion_row)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.input = QLineEdit(input_wrap)
        self.input.setPlaceholderText("Message A.B.A.C.U.S....")
        self.input.returnPressed.connect(self.submit_message)
        input_layout.addWidget(self.input, 1)

        self.send_btn = QPushButton("➤", input_wrap)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setFixedSize(34, 34)
        self.send_btn.clicked.connect(self.submit_message)
        input_layout.addWidget(self.send_btn)
        input_outer.addLayout(input_layout)
        card_layout.addWidget(input_wrap)

        self.setStyleSheet(
            """
            QWidget#chatHeader,
            QWidget#chatInputWrap,
            QWidget#scrollContents {
                background: transparent;
            }
            QWidget#chatCard {
                background: transparent;
                border-radius: 18px;
            }
            QScrollArea,
            QScrollArea QWidget {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px 2px 2px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(139, 177, 255, 170);
                border-radius: 5px;
                min-height: 26px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(168, 199, 255, 220);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
                border: none;
                height: 0;
            }
            QPushButton {
                color: #dff0ff;
                background: #2a65df;
                border: none;
                border-radius: 11px;
                font: 10px 'Segoe UI Semibold';
            }
            QPushButton:hover {
                background: #3b78ef;
            }
            QLineEdit {
                background: rgba(8, 18, 41, 220);
                color: white;
                border: 1px solid rgba(122, 170, 255, 180);
                border-radius: 17px;
                padding: 8px 12px;
                font: 11px 'Segoe UI';
            }
            QLineEdit:focus {
                border: 1px solid #6ea3ff;
            }
            """
        )
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.build_toggle_button()
        self.append_message_signal.connect(self.append_message)
        self.set_typing_state_signal.connect(self._apply_typing_state)
        self.reposition()
        self.show()

    def build_toggle_button(self):
        self.toggle_btn = QPushButton("❯")
        self.toggle_btn.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.toggle_btn.setFixedSize(34, 42)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_chat)
        self.toggle_btn.setStyleSheet(
            """
            QPushButton {
                background: rgba(21, 39, 82, 230);
                color: #eaf4ff;
                border-radius: 12px;
                border: 1px solid rgba(132, 176, 255, 140);
                font: bold 14px 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(35, 59, 112, 240);
            }
            """
        )

        self.unread_dot = QLabel(self.toggle_btn)
        self.unread_dot.setFixedSize(10, 10)
        self.unread_dot.move((self.toggle_btn.width() - 10) // 2, 2)
        self.unread_dot.setStyleSheet("background: #ff3b30; border-radius: 5px;")
        self.unread_dot.hide()

        self.position_toggle()
        self.toggle_btn.show()

    def reposition(self):
        screen = QApplication.primaryScreen().availableGeometry()
        sprite_top = self.sprite.default_pos.y()
        max_height = max(260, sprite_top - self.top_margin - 14)

        self.setFixedHeight(max_height)
        self.visible_x = screen.width() - self.width() - self.right_margin
        self.visible_y = self.top_margin
        self.hidden_x = screen.width() + 12

        self.move(self.visible_x if not self.is_hidden else self.hidden_x, self.visible_y)
        self.position_toggle()

    def position_toggle(self):
        screen = QApplication.primaryScreen().availableGeometry()
        center_y = self.visible_y + (self.height() // 2) - (self.toggle_btn.height() // 2)
        y = max(110, min(screen.height() - self.toggle_btn.height() - 20, center_y))
        self.toggle_btn.move(screen.width() - self.toggle_btn.width() - 2, y)

    def toggle_background(self):
        self.show_background = not self.show_background
        if self.show_background:
            self.card.setStyleSheet(
                "QFrame#chatCard {"
                "background: rgba(12, 20, 44, 205);"
                "border: 1px solid rgba(110, 163, 255, 120);"
                "border-radius: 18px;"
                "}"
            )
            self.bg_toggle.setText("Background ✓")
        else:
            self.card.setStyleSheet("QFrame#chatCard { background: transparent; border-radius: 18px; }")
            self.bg_toggle.setText("Background")

    def focus_input(self):
        self.input.setFocus()

    def open_settings(self):
        save_callback = save_settings
        setting_actions = {}
        if self.sprite is not None and hasattr(self.sprite, "handle_settings_save"):
            save_callback = self.sprite.handle_settings_save
            if hasattr(self.sprite, "handle_setting_action"):
                setting_actions = {
                    "drag_to_move_sprite": lambda: self.sprite.handle_setting_action("drag_to_move_sprite"),
                    "hotkey_activation": lambda: self.sprite.handle_setting_action("hotkey_activation"),
                }
        show_settings_panel(save_callback, setting_actions=setting_actions, initial_tab="settings")

    def open_schedule(self):
        save_callback = save_settings
        setting_actions = {}
        if self.sprite is not None and hasattr(self.sprite, "handle_settings_save"):
            save_callback = self.sprite.handle_settings_save
            if hasattr(self.sprite, "handle_setting_action"):
                setting_actions = {
                    "drag_to_move_sprite": lambda: self.sprite.handle_setting_action("drag_to_move_sprite"),
                    "hotkey_activation": lambda: self.sprite.handle_setting_action("hotkey_activation"),
                }
        show_settings_panel(save_callback, setting_actions=setting_actions, initial_tab="schedule")

    def show_chat(self):
        if not self.is_hidden:
            return
        self.toggle_chat()

    def toggle_chat(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.reposition()

        if self.is_hidden:
            self._animate_widget(self, QPoint(self.visible_x, self.visible_y))
            if self.sprite is not None and self.sprite.isVisible():
                self._animate_widget(self.sprite, self.sprite.default_pos)
            self.toggle_btn.setText("❯")
            self.unread_dot.hide()
            self.is_hidden = False
            return

        hidden_sprite_x = screen.width() + 14
        self._animate_widget(self, QPoint(self.hidden_x, self.visible_y))
        if self.sprite is not None and self.sprite.isVisible():
            self._animate_widget(self.sprite, QPoint(hidden_sprite_x, self.sprite.default_pos.y()))
        self.toggle_btn.setText("❮")
        self.is_hidden = True

    def _animate_widget(self, widget, end_pos):
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(360)
        anim.setStartValue(widget.pos())
        anim.setEndValue(end_pos)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.start()
        self.ui_anims.append(anim)
        anim.finished.connect(lambda: self.ui_anims.remove(anim) if anim in self.ui_anims else None)

    def submit_message(self):
        if self.is_typing:
            return

        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.input.setFocus()

        from core.pipeline import get_on_speech
        handler = get_on_speech()
        if handler:
            threading.Thread(target=handler, args=(text, "manual"), daemon=True).start()

    def handle_suggestion_click(self, template):
        text = str(template or "").strip()
        if not text:
            return
        self.input.setText(text)
        self.input.setFocus()

        placeholder_index = text.find("<")
        if placeholder_index != -1:
            self.input.setCursorPosition(placeholder_index)
        else:
            self.input.setCursorPosition(len(text))

    def enqueue_message(self, role, text, session_id=""):
        if isinstance(session_id, tuple):
            session_id = session_id[0] if session_id else ""
        session_id = "" if session_id is None else str(session_id)
        self.append_message_signal.emit(str(role), str(text), session_id)

    def is_near_bottom(self, threshold=40):
        bar = self.scroll.verticalScrollBar()
        return (bar.maximum() - bar.value()) <= threshold

    def smooth_scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        target = bar.maximum()
        start = bar.value()

        if start >= target:
            return

        if self.scroll_anim is not None:
            self.scroll_anim.stop()

        self.scroll_anim = QPropertyAnimation(bar, b"value", self)
        self.scroll_anim.setDuration(260)
        self.scroll_anim.setStartValue(start)
        self.scroll_anim.setEndValue(target)
        self.scroll_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.scroll_anim.start()

    def append_message(self, role, text, session_id=""):
        if isinstance(session_id, tuple):
            session_id = session_id[0] if session_id else ""
        session_id = "" if session_id is None else str(session_id)
        if session_id:
            self.session_label.setText(f"Session: {session_id[:12]}")

        if role == "assistant":
            self._hide_typing_bubble()

        should_auto_scroll = self.is_near_bottom()
        bubble = ChatBubble(role, text, self.scroll_contents)
        count = self.messages_layout.count()

        if count > 0:
            self.messages_layout.insertWidget(count - 1, bubble)
        else:
            self.messages_layout.addWidget(bubble)

        self.scroll_contents.adjustSize()
        QApplication.processEvents()
        bubble.animate_in()

        if should_auto_scroll:
            QTimer.singleShot(50, self.smooth_scroll_to_bottom)

    def set_typing_state(self, is_typing):
        self.set_typing_state_signal.emit(bool(is_typing))

    def _apply_typing_state(self, is_typing):
        self.is_typing = bool(is_typing)
        self.input.setEnabled(not self.is_typing)
        self.send_btn.setEnabled(not self.is_typing)

        if self.is_typing:
            self.input.setPlaceholderText("A.B.A.C.U.S. is typing...")
            self._show_typing_bubble()
            return

        self._hide_typing_bubble()
        self.input.setPlaceholderText("Message A.B.A.C.U.S....")
        self.input.setFocus()

    def _show_typing_bubble(self):
        if self.typing_bubble is not None:
            return

        should_auto_scroll = self.is_near_bottom()
        self.typing_bubble = TypingBubble(self.scroll_contents)

        count = self.messages_layout.count()
        if count > 0:
            self.messages_layout.insertWidget(count - 1, self.typing_bubble)
        else:
            self.messages_layout.addWidget(self.typing_bubble)

        self.scroll_contents.adjustSize()
        QApplication.processEvents()
        self.typing_bubble.animate_in()

        if should_auto_scroll:
            QTimer.singleShot(50, self.smooth_scroll_to_bottom)

    def _hide_typing_bubble(self):
        if self.typing_bubble is None:
            return

        self.typing_bubble.stop_animation()
        self.messages_layout.removeWidget(self.typing_bubble)
        self.typing_bubble.deleteLater()
        self.typing_bubble = None

def show_toast(title, msg, sprite=None, sound_file="", duration="short"):
    if sprite is not None:
        sprite.jump_on_notif(height=150, duration=600)

    toast = Notification(app_id="A.B.A.C.U.S.", title=title, msg=msg, duration=duration)
    toast.set_audio(audio.Mail, loop=False)

    threading.Thread(target=toast.show, daemon=True).start()
    wait = 7500 if duration == "short" else 25000
    
    if sprite is not None:
        QTimer.singleShot(wait, lambda: sprite.fall_back(duration=400))

active_sounds = []
def play_sound_multiple(file_path, count=5, interval=0.2):
    def play_loop():
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        for _ in range(count):
            play_obj = wave_obj.play()
            active_sounds.append(play_obj)
            time.sleep(interval)
        for p in active_sounds[:]:
            if not p.is_playing():
                active_sounds.remove(p)
    threading.Thread(target=play_loop, daemon=True).start()

class SpeakNowWindow:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.label = tk.Label(self.root, text="Speak now!", font=("Arial", 18), bg="white")
        self.label.pack(padx=10, pady=5)

        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = screen_width - width - 20
        y = screen_height - height - 50
        self.root.geometry(f"+{x}+{y}")

    def disable_event(self):
        pass

    def hide(self):
        self.root.destroy()

class TransparentOverlay(QWidget):
    def __init__(self, glow_color=(255, 0, 0), glow_strength=6, border_thickness=4, duration=2000, fade_duration=500):
        super().__init__()

        r, g, b, *a = glow_color
        alpha = a[0] if a else 255
        self.glow_color = QColor(r, g, b, alpha)
        self.glow_strength = glow_strength
        self.border_thickness = border_thickness
        self.duration = duration
        self.fade_duration = fade_duration

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        hwnd = int(self.winId())
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

    def close_overlay(self):
        self.close()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        for i in range(self.glow_strength, 0, -1):
            alpha = int(self.glow_color.alpha() * (i / self.glow_strength))
            color = QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), alpha)
            pen = QtGui.QPen(color, self.border_thickness + i * 2)
            painter.setPen(pen)
            painter.drawRect(i, i, self.width() - 2*i, self.height() - 2*i)

    def start_fade_out(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(self.fade_duration)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close_overlay)
        self.fade_out.start()


def get_audio_inputs():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            devices.append({"index": i, "name": info['name']})
    p.terminate()
    return devices


# class WindowsBalloonTip:
#     def __init__(self, title, msg):

#         message_map = {
#             win32con.WM_DESTROY: self.OnDestroy,
#         }

#         wc = WNDCLASS()
#         hinst = wc.hInstance = GetModuleHandle(None)
#         wc.lpszClassName = "PythonTaskbar"
#         wc.lpfnWndProc = message_map
#         classAtom = RegisterClass(wc)
#         style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
#         self.hwnd = CreateWindow(
#             classAtom,
#             "Taskbar",
#             style,
#             0, 0,
#             win32con.CW_USEDEFAULT,
#             win32con.CW_USEDEFAULT,
#             0, 0,
#             hinst,
#             None
#         )

#         UpdateWindow(self.hwnd)

#         iconPathName = os.path.abspath(
#             os.path.join(sys.path[0], "data/img/rock.png")
#         )
#         icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE

#         try:
#             hicon = LoadImage(
#                 hinst,
#                 iconPathName,
#                 win32con.IMAGE_ICON,
#                 0, 0,
#                 icon_flags
#             )
#         except:
#             hicon = LoadIcon(0, win32con.IDI_APPLICATION)

#         flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
#         nid = (self.hwnd, 0, flags,
#                win32con.WM_USER + 20,
#                hicon, "tooltip")

#         Shell_NotifyIcon(NIM_ADD, nid)
#         Shell_NotifyIcon(
#             NIM_MODIFY,
#             (self.hwnd, 0, NIF_INFO,
#              win32con.WM_USER + 20,
#              hicon,
#              "Balloon tooltip",
#              msg,
#              200,
#              title)
#         )

#         time.sleep(10)
#         DestroyWindow(self.hwnd)

#     def OnDestroy(self, hwnd, msg, wparam, lparam):
#         nid = (self.hwnd, 0)
#         Shell_NotifyIcon(NIM_DELETE, nid)
#         PostQuitMessage(0)
#         return 0

# def balloon_tip(title, msg):
#         threading.Thread(
#         target=WindowsBalloonTip,
#         args=(title, msg),
#         daemon=True
#     ).start()

# Uh, this is a 3D rock sprite, I guess?
# class Rock3D(QOpenGLWidget):
#     def __init__(self, image_path):
#         super().__init__()
#         fmt = QSurfaceFormat()
#         fmt.setAlphaBufferSize(8)
#         self.setFormat(fmt)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setAttribute(Qt.WA_NoSystemBackground)
#         self.angle = 0
#         self.image_path = image_path
#         self.texture = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_angle)
#         self.timer.start(20)

#     def initializeGL(self):
#         glEnable(GL_TEXTURE_2D)
#         glClearColor(0.0, 0.0, 0.0, 0.0)
#         glEnable(GL_BLEND)
#         glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#         self.load_texture()

#     def load_texture(self):
#         image = QImage(self.image_path).convertToFormat(QImage.Format_RGBA8888)
#         width, height = image.width(), image.height()
#         ptr = image.bits()
#         ptr.setsize(image.byteCount())
#         arr = np.frombuffer(ptr, np.uint8)

#         self.texture = glGenTextures(1)
#         glBindTexture(GL_TEXTURE_2D, self.texture)
#         glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#         glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#         glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, arr)

#     def paintEvent(self, event):
#         self.makeCurrent()
#         self.paintGL()
#         self.doneCurrent()

#     def paintGL(self):
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         glLoadIdentity()

#         glTranslatef(0.0, 0.0, -2.3)  # Move back a bit
#         glRotatef(self.angle, 0.0, 1.0, 0.0)  # Rotate around Y axis

#         glBindTexture(GL_TEXTURE_2D, self.texture)
#         glBegin(GL_QUADS)
#         glTexCoord2f(0.0, 1.0); glVertex3f(-1.0, -1.0, 0.0)
#         glTexCoord2f(1.0, 1.0); glVertex3f(1.0, -1.0, 0.0)
#         glTexCoord2f(1.0, 0.0); glVertex3f(1.0, 1.0, 0.0)
#         glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, 1.0, 0.0)
#         glEnd()

#     def resizeGL(self, w, h):
#         glViewport(0, 0, w, h)
#         glMatrixMode(GL_PROJECTION)
#         glLoadIdentity()
#         gluPerspective(45.0, w / h if h else 1, 0.1, 100.0)
#         glMatrixMode(GL_MODELVIEW)

#     def update_angle(self):
#         self.angle = (self.angle + 2) % 360
#         self.update()

# class RockSprite(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
#         self.setAttribute(Qt.WA_TranslucentBackground)

#         self.gl_widget = Rock3D("data/img/rock2.png")
#         self.gl_widget.setFixedSize(300, 200)

#         self.screen_geometry = QApplication.primaryScreen().geometry()
#         self.move(self.screen_geometry.width() - 320,
#                   self.screen_geometry.height() - 240)

#         self.gl_widget.setParent(self)
#         self.gl_widget.move(0, 0)
#         self.show()

#         self.bubble = QLabel("", None)
#         self.bubble.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#         self.bubble.setStyleSheet("""
#             QLabel {
#                 background-color: white;
#                 border-radius: 10px;
#                 border: 1px solid black;
#                 padding: 5px;
#             }
#         """)
#         self.bubble.setFont(QFont("Arial", 12))

#         self.sentences = self.load_sentences("data/rock/rock.json")
#         if not self.sentences:
#             self.sentences = ["..."]

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.show_random_sentence)
#         self.timer.start(20000)
#         self.show_random_sentence()

#     def load_sentences(self, path):
#         try:
#             with open(path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#             if isinstance(data, list):
#                 return data
#             print("rock.json format invalid — must be a list of strings.")
#             return []
#         except Exception as e:
#             print("Failed to load sentences:", e)
#             return []

#     def show_random_sentence(self):
#         sentence = random.choice(self.sentences)
#         self.bubble.setText(sentence)
#         self.bubble.adjustSize()

#         bubble_x = self.x() + (self.gl_widget.width() - self.bubble.width() - 30)
#         bubble_y = self.y() - self.bubble.height() - 20
#         self.bubble.move(bubble_x, bubble_y)
#         self.bubble.show()
#         self.bubble.raise_()
#         QTimer.singleShot(5000, self.bubble.hide)