from PIL import Image, ImageTk
import tkinter as tk
import json
import os
import signal
from core.translations import load_translations

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
        play_sound_multiple("data/audio/cat-laugh-meme.wav", count=10, interval=0.2)
        img_window.mainloop()
    os.makedirs("data", exist_ok=True)
    with open("data/saved-settings.json", "w") as f:
        json.dump(data, f, indent=4)
    load_translations(data.get("display_lang", "en"))