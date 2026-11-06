import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import speech_recognition as sr
import pyttsx3
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
from services.ErrorLogService import add_log_entry

recognizer = sr.Recognizer()
pygame.mixer.init()


def get_microphone_device_index():
    selected_name = (get_saved_settings().get("microphone_input") or "").strip().lower()
    if not selected_name:
        return None

    try:
        microphone_names = sr.Microphone.list_microphone_names()
    except Exception as e:
        add_log_entry(
            title="Failed to list microphone devices",
            description=str(e),
            error_type=type(e).__name__,
        )
        return None

    for index, name in enumerate(microphone_names):
        normalized_name = (name or "").strip().lower()
        if (
            normalized_name == selected_name or
            normalized_name.startswith(selected_name) or
            selected_name.startswith(normalized_name)
        ):
            return index

    return None


def recognize_audio(local_recognizer, audio):
    settings = get_saved_settings()
    provider = settings.get("stt_provider", "google").lower()

    if provider == "sphinx":
        return local_recognizer.recognize_sphinx(audio)

    return local_recognizer.recognize_google(audio)


def speak_local(message):
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.say(message)
    engine.runAndWait()

def start_always_on(on_speech):
    mic = sr.Microphone(device_index=get_microphone_device_index())
    def callback(recognizer, audio):
        try:
            text = recognize_audio(recognizer, audio)
            on_speech(text, "voice")
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("Speech recognition error:", e)
            add_log_entry("Speech recognition error", str(e), type(e).__name__)
        except Exception as e:
            print("Speech recognition unexpected error:", e)
            add_log_entry("Speech recognition unexpected error", str(e), type(e).__name__)

    with mic as source:
        print("Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")

    stop = recognizer.listen_in_background(mic, callback)
    return stop

async def speak(message, voice):
    communicate = edge_tts.Communicate(message, voice, rate="+10%")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def give_audio_response(message, gender="male"):
    settings = get_saved_settings()

    if settings['audio_response'] == False:
        return

    settings = get_saved_settings()
    tts_provider = settings.get("tts_provider", "edge").lower()

    if tts_provider == "pyttsx3":
        speak_local(message)
        return

    lang = settings.get("speaking_lang", "en")

    VOICE_MAP = {
        "nl": {"male": "nl-NL-MaartenNeural", "female": "nl-NL-FennaNeural"},
        "en": {"male": "en-US-GuyNeural", "female": "en-US-JennyNeural"},
    }

    if lang in VOICE_MAP:
        message = GoogleTranslator(source='auto', target=lang).translate(message)
    
    voice = VOICE_MAP.get(lang, VOICE_MAP["en"]).get(gender, "male")
    audio_data = asyncio.run(speak(message, voice))
    pygame.mixer.music.load(io.BytesIO(audio_data))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def listen_and_recognize():
    # Placeholder for follow-up voice questions; listening is handled by start_always_on
    return ""
