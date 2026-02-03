import speech_recognition as sr
import pyttsx3
import threading
import time
import os
import sys
import simpleaudio as sa
import datetime
from handlers.StorageHandler import user
from handlers.PopupHandler import SpeakNowWindow, TransparentOverlay
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget

recognizer = sr.Recognizer()

def listen_and_recognize():
    overlay = TransparentOverlay(
        glow_color=(0, 255, 255, 20),
        glow_strength=13,
        border_thickness=1,
        duration=2000,
        fade_duration=500
    )

    with sr.Microphone() as source:
        print("Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        overlay.show()
        QApplication.processEvents()
        print("Speak now!")

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
            print("Captured!") 
        except sr.WaitTimeoutError:
            print("No speech detected.")
            overlay.hide()
            return ""

    QTimer.singleShot(1000, overlay.start_fade_out)
    overlay.close_overlay();

    base_folder = "data/audio-logs"

    today_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(base_folder, today_folder)
    os.makedirs(folder_path, exist_ok=True)

    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())

    try:
        text = recognizer.recognize_google(audio)
        print("Recognized:", text)
    except Exception as e:
        print("Recognition failed:", e)
        text = ""

    return text

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
