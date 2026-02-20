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

from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QOpenGLWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont, QImage, QSurfaceFormat, QColor
from PyQt5.QtCore import Qt, QTimer, QRect
from OpenGL.GL import *
from OpenGL.GLU import *

from core.translations import load_translations, t
from core.storage import get_saved_settings

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

# TODO: cross support for abacus and the dumb rock
#  Abacus will be a helpful assistant. The rock might be used one day for idk, something, I dont care.

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

        self.display_width = 350
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

        self.show()

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
        elif event.button() == Qt.RightButton:
            # Open settings
            window = create_window('Settings', size="800x600", topmost=False)
            canvas = tk.Canvas(window, height=600)
            scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # TODO: Create settings options for:
            #   - Display language (and search results language meaning I have to build a translate function as well)
            #   - Toggle sprite (on/off, user may choose to use a hotkey instead for activation commands)
            #   - Toggle activation word (so the user does not have to say 'Abacus' each iteration, instead saying 'Search [x]')
            #   - Light mode (implement flashbang lmao)
            #   - Drag to move sprite (draw sprite with something like a crane to move him around)
            #   - Hidden toggle to turn off data stealing :3

            # fetch settings from available-settings.json and create elements based on type
            saved = get_saved_settings()
            setting_vars = {}
            with open("core/settings/available-settings.json", "r") as f:
                settings = json.load(f)
                for key, setting in settings.items():
                    if setting.get("hidden"):
                        continue

                    label_text = t(key)
                    desc_text = t(key + "_description")

                    if setting["type"] == "checkbox":
                        var = tk.BooleanVar(value=saved.get(key, False))
                        chk = tk.Checkbutton(scrollable_frame, text=label_text, variable=var)
                        chk.pack(anchor=tk.W, pady=5)
                        setting_vars[key] = var
                    elif setting["type"] == "dropdown":
                        lbl = tk.Label(scrollable_frame, text=label_text)
                        lbl.pack(anchor=tk.W, pady=(10, 0))
                        
                        if key == "microphone_input":
                            options = [d["name"] for d in get_audio_inputs()]
                        else:
                            options = setting["options"]
                        
                        var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                        dropdown = tk.OptionMenu(scrollable_frame, var, *options)
                        dropdown.pack(anchor=tk.W, pady=5)
                        setting_vars[key] = var
                    elif setting["type"] == "button":
                        btn = tk.Button(scrollable_frame, text=setting["name"])
                        btn.pack(anchor=tk.W, pady=5)
            
                def save_settings():
                    data = {key: var.get() for key, var in setting_vars.items()}
                    
                    if data.get("display_lang") == "fr" or data.get("speaking_lang") == "fr":
                        data["display_lang"] = "en"
                        data["speaking_lang"] = "en"
                        
                        winsound.PlaySound("data/audio/cat-laugh-meme.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                        img_window = tk.Toplevel()
                        img_window.attributes("-fullscreen", True)
                        img_window.attributes("-topmost", True)
                        img = tk.PhotoImage(file="data/img/lmao-french.png")
                        
                        from PIL import Image, ImageTk
                        pil_img = Image.open("data/img/lmao-french.png")
                        screen_w = img_window.winfo_screenwidth()
                        screen_h = img_window.winfo_screenheight()
                        pil_img = pil_img.resize((screen_w, screen_h))
                        img = ImageTk.PhotoImage(pil_img)
                        
                        lbl = tk.Label(img_window, image=img)
                        lbl.image = img
                        lbl.pack()
                        img_window.update()
                        
                        img_window.after(3700, img_window.destroy)
                        img_window.mainloop()
                    
                    os.makedirs("data", exist_ok=True)
                    with open("data/saved-settings.json", "w") as f:
                        json.dump(data, f, indent=4)
                    load_translations(data.get("display_lang", "en"))
                    window.destroy()

            save_btn = tk.Button(scrollable_frame, text="Save", command=save_settings)
            save_btn.pack(pady=15)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            window.mainloop()

            
    # def mousePressEvent(self, event):
    #     from main import start
    #     if event.button() == Qt.LeftButton:
    #         start();

            # self.move(
            #     self.screen.width() - self.display_width - 20,
            #     int(self.frame_height * (self.display_width / self.frame_width))
            # )

            # while True:
            #     time.sleep(0.001)
            #     self.location += self.direction

            #     self.move(
            #         self.screen.width() - self.display_width - self.location,
            #         self.screen.height() - self.display_height - 120
            #     )

            #     if self.location >= 1000:
            #         self.direction = -1
            #     if self.location <= 0:
            #         self.direction = 1


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
        QApplication.quit()

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