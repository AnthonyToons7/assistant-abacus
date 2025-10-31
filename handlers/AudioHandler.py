import speech_recognition as sr
import pyttsx3
import threading
import time
import os
import simpleaudio as sa
import datetime
import tkinter as tk
from PIL import Image, ImageTk
from handlers.StorageHandler import user

recognizer = sr.Recognizer()

class MicWindow:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        if os.path.exists("mic.png"):
            img = Image.open("mic.png").resize((50, 50))
            self.photo = ImageTk.PhotoImage(img)
            self.label = tk.Label(self.root, image=self.photo)
        else:
            self.label = tk.Label(self.root, text="🎤", font=("Arial", 24))
        self.label.pack()

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

def record_audio(mic_win):
    with sr.Microphone() as source:
        print("Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        print("Speak now!")
        audio = recognizer.listen(source)
        print("Captured!")

    os.makedirs("data/audio-logs", exist_ok=True)
    file_path = f"data/audio-logs/test-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.wav"
    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())
    print(f"Audio saved to {file_path}")

    try:
        text = recognizer.recognize_google(audio)
        print("Recognized:", text)
    except Exception as e:
        print("Recognition failed:", e)
        text = ""

    mic_win.hide()
    return text

def listen_and_recognize():
    # Tkinter root must be created in main thread
    root = tk.Tk()
    mic_win = MicWindow()

    # Start recording in a separate thread
    threading.Thread(target=record_audio, args=(mic_win,), daemon=True).start()

    # Run GUI mainloop (blocks main thread)
    root.mainloop()

def give_audio_response(message):    
    text_to_speech = pyttsx3.init()
    voices = text_to_speech.getProperty('voices')
    text_to_speech.setProperty('voice', voices[1].id)
    text_to_speech.say(message)
    text_to_speech.runAndWait()
    time.sleep(0.5)

def ping():
    if not os.path.exists('data/audio/ping.wav'):
        return None
    
    wave_obj = sa.WaveObject.from_wave_file("data/audio/ping.wav")
    play_obj = wave_obj.play()

def save_audio_file(audio):
    os.makedirs("data/audio-logs", exist_ok=True)
    with open(f"data/audio-logs/test-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.wav", "wb") as f:
        f.write(audio.get_wav_data())


class SpeakNowWindow:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)      # remove title bar
        self.root.attributes("-topmost", True)  # always on top
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        # Display text
        self.label = tk.Label(self.root, text="Speak now!", font=("Arial", 18), bg="yellow")
        self.label.pack(padx=10, pady=5)

        # Bottom-right corner
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = screen_width - width - 20
        y = screen_height - height - 50
        self.root.geometry(f"+{x}+{y}")

    def disable_event(self):
        pass  # prevent closing manually

    def hide(self):
        self.root.destroy()


def record_audio(window):
    # Record
    with sr.Microphone() as source:
        print("Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        print("Listening now!")
        audio = recognizer.listen(source)
        print("Captured!")

    # Save audio
    os.makedirs("data/audio-logs", exist_ok=True)
    file_path = f"data/audio-logs/test-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.wav"
    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())
    print(f"Audio saved to {file_path}")

    # Recognition
    try:
        text = recognizer.recognize_google(audio)
        print("Recognized:", text)
    except Exception as e:
        print("Recognition failed:", e)
        text = ""

    # Destroy the GUI window
    window.hide()


def listen_and_recognize():
    root = tk.Tk()
    window = SpeakNowWindow(root)
    threading.Thread(target=record_audio, args=(window,), daemon=True).start()

    root.mainloop()
