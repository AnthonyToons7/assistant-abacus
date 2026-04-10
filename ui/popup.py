import os
import signal
import json
import random
import math
import numpy as np
import time 
import tkinter as tk
import threading
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
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QOpenGLWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont, QImage, QSurfaceFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QPoint, QEasingCurve
from OpenGL.GL import *
from OpenGL.GLU import *

from core.translations import load_translations, t
from core.storage import get_saved_settings
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

class AbacusSprite(QLabel):
    def __init__(
        self,
        on_click=None,
        frame_count=8,
        sheet_dir="data/img/Slime-sheet.png",
        fps=10
    ):
        self.on_click = on_click
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
        self.show()

    def jump_on_notif(self, height=100, duration=500):
        """Animate sprite to jump up 'height' pixels"""
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(self.pos().x(), self.pos().y() - height))
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()

    def fall_back(self, duration=500):
        """Animate sprite falling back to original position"""
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
        if event.button() == Qt.LeftButton and self.on_click:
            self.on_click()
        elif event.button() == Qt.MiddleButton:
            self._prompt_window = PromptInputWindow()
            self._prompt_window.show()
        elif event.button() == Qt.RightButton:
            with open("core/settings/available-settings.json", "r") as f:
                settings = json.load(f)
            open_settings_window(
                t=t,
                get_saved_settings=get_saved_settings,
                get_audio_inputs=get_audio_inputs,
                settings=settings,
                save_callback=save_settings,
            )

class PromptInputWindow(QWidget):
    """Small always-on-top window that lets the user type a prompt manually."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(420)

        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
        from PyQt5.QtGui import QPainter, QBrush, QPen

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        card = QWidget(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            QWidget#card {
                background-color: #13152a;
                border: 1px solid #252840;
                border-radius: 10px;
            }
        """)
        self._layout.addWidget(card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(16, 14, 16, 14)
        inner.setSpacing(10)

        title_row = QHBoxLayout()
        title = QLabel("⌨  TYPE PROMPT", card)
        title.setStyleSheet("color: #5b7fff; font: bold 11px 'Courier New'; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()

        close_btn = QPushButton("✕", card)
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6b7096;
                border: none;
                font: bold 12px 'Courier New';
            }
            QPushButton:hover { color: #ffffff; background: #ff4d6d; border-radius: 4px; }
        """)
        close_btn.clicked.connect(self.close)
        title_row.addWidget(close_btn)
        inner.addLayout(title_row)

        line = QWidget(card)
        line.setFixedHeight(1)
        line.setStyleSheet("background: #252840;")
        inner.addWidget(line)

        self._input = QLineEdit(card)
        self._input.setPlaceholderText("e.g.  Abacus, play my playlist Lofi")
        self._input.setStyleSheet("""
            QLineEdit {
                background: #0d0e1c;
                color: #e4e6f0;
                border: 1px solid #252840;
                border-radius: 6px;
                padding: 8px 10px;
                font: 10px 'Courier New';
            }
            QLineEdit:focus { border: 1px solid #5b7fff; }
        """)
        self._input.returnPressed.connect(self._submit)
        inner.addWidget(self._input)

        submit_btn = QPushButton("SEND", card)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background: #5b7fff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font: bold 10px 'Courier New';
            }
            QPushButton:hover { background: #6b8fff; }
        """)
        submit_btn.clicked.connect(self._submit)
        inner.addWidget(submit_btn)

        self.adjustSize()
        self._position_near_sprite()
        self._input.setFocus()

    def _position_near_sprite(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20,
                  screen.height() - self.height() - 220)

    def _submit(self):
        text = self._input.text().strip()
        if not text:
            return
        self.close()
        from core.pipeline import get_on_speech  # lazy import — avoids circular dependency
        handler = get_on_speech()
        if handler:
            threading.Thread(target=handler, args=(text,), daemon=True).start()
        else:
            print("[PromptInputWindow] on_speech not ready yet — call start() first.")


def show_toast(title, msg, sprite, sound_file="", duration="short"):
    sprite.jump_on_notif(height=150, duration=600)

    toast = Notification(app_id="ABACUS", title=title, msg=msg, duration=duration)
    toast.set_audio(audio.Mail, loop=False)

    threading.Thread(target=toast.show, daemon=True).start()
    wait = 7500 if duration == "short" else 25000
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