import os
import tkinter as tk
import signal
import ctypes
import json
import random
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QRegion, QPainterPath, QBitmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer

signal.signal(signal.SIGINT, signal.SIG_DFL) 

class AbacusSprite(QLabel):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap("data/img/rock2.png")
        if self.pixmap.isNull():
            print("Failed to load image!")
            return

        self.pixmap = self.pixmap.scaledToWidth(300)
        self.pixmap = self.pixmap.scaledToHeight(200)
        self.setPixmap(self.pixmap)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.screen_geometry = QApplication.primaryScreen().geometry()
        self.move(self.screen_geometry.width() - self.pixmap.width() - 10, self.screen_geometry.height() - self.pixmap.height() - 20)
        self.show()

        self.bubble = QLabel("", None)
        self.bubble.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.bubble.setFont(QFont("Arial", 12))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.bubble.width(), self.bubble.height(), 10, 10)

        mask = QBitmap(self.bubble.size())
        mask.fill(Qt.GlobalColor.color0)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillPath(path, Qt.GlobalColor.color1)
        painter.end()

        self.bubble.setMask(mask)

        self.sentences = self.load_sentences("data/rock/rock.json")
        if not self.sentences:
            self.sentences = ["..."]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_random_sentence)
        self.timer.start(20000)
        self.show_random_sentence()

    def load_sentences(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            print("rock.json format invalid — must be a list of strings.")
            return []
        except Exception as e:
            print("Failed to load sentences:", e)
            return []

    def show_random_sentence(self):
        sentence = random.choice(self.sentences)
        self.bubble.setText(sentence)
        self.bubble.adjustSize()

        bubble_x = self.x() + (self.width() - self.bubble.width() - 30)
        bubble_y = self.y() - self.bubble.height() - 10
        self.bubble.move(bubble_x, bubble_y)
        self.bubble.show()
        self.bubble.raise_()

        QTimer.singleShot(5000, self.bubble.hide)

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         print("Sprite clicked!")
    #         pixmap = self.pixmap.scaledToWidth(300)
    #         pixmap = pixmap.scaledToHeight(200)
    #         self.setPixmap(pixmap)
    #         self.screen_geometry = QApplication.primaryScreen().geometry()
    #         self.move(self.screen_geometry.width() - pixmap.width() - 20,
    #                   self.screen_geometry.height() - pixmap.height() - 100)
    #         self.update_bubble_position()

    def update_bubble_position(self):
        if not self.bubble.isVisible():
            return
        bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
        bubble_y = self.y() - self.bubble.height() - 10
        self.bubble.move(bubble_x, bubble_y)

class SpeakNowWindow:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.label = tk.Label(self.root, text="Speak now!", font=("Arial", 18), bg="yellow")
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
        QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i in range(self.glow_strength, 0, -1):
            alpha = int(self.glow_color.alpha() * (i / self.glow_strength))
            color = QColor(self.glow_color.red(), self.glow_color.green(), self.glow_color.blue(), alpha)
            pen = QPen(color, self.border_thickness + i * 2)
            painter.setPen(pen)
            painter.drawRect(i, i, self.width() - 2*i, self.height() - 2*i)

    def start_fade_out(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(self.fade_duration)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close_overlay)
        self.fade_out.start()
