from PIL import Image, ImageTk
import tkinter as tk
import json
import os
import signal
import threading
import time
import simpleaudio as sa
from core.translations import load_translations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, 'data', 'saved-settings.json')

def save_settings(data):
    if data.get("display_lang") == "fr" or data.get("speaking_lang") == "fr":
        data["display_lang"] = "en"
        data["speaking_lang"] = "en"
        img_window = tk.Tk()
        img_window.attributes("-fullscreen", True)
        img_window.attributes("-topmost", True)
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
        play_sound_multiple("data/audio/cat-laugh-meme.wav", count=1, interval=0.2)
        img_window.mainloop()
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    load_translations(data.get("display_lang", "en"))

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
