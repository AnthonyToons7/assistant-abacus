import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import sys
import speech_recognition as sr
import pyttsx3
import threading
import time
import simpleaudio as sa
import datetime
import edge_tts
import asyncio
import pygame
import io
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from deep_translator import GoogleTranslator

from core.storage import user
from ui.popup import SpeakNowWindow, TransparentOverlay
from core.storage import get_saved_settings

recognizer = sr.Recognizer()
pygame.mixer.init()

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

async def _speak(message, voice):
    communicate = edge_tts.Communicate(message, voice, rate="+10%")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def give_audio_response(message, gender="male"):
    lang = get_saved_settings().get("speaking_lang", "en")

    VOICE_MAP = {
        "nl": {"male": "nl-NL-MaartenNeural", "female": "nl-NL-FennaNeural"},
        "en": {"male": "en-US-GuyNeural", "female": "en-US-JennyNeural"},
    }

    if lang in VOICE_MAP:
        message = GoogleTranslator(source='auto', target=lang).translate(message)
    
    voice = VOICE_MAP.get(lang, VOICE_MAP["en"]).get(gender, "male")
    audio_data = asyncio.run(_speak(message, voice))
    pygame.mixer.music.load(io.BytesIO(audio_data))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
def ping():
    if not os.path.exists('data/audio/ping.wav'):
        return None
    
    wave_obj = sa.WaveObject.from_wave_file("data/audio/ping.wav")
    play_obj = wave_obj.play()
