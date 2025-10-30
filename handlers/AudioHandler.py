import speech_recognition as sr
import pyttsx3
import time
import os
import simpleaudio as sa
from handlers.StorageHandler import user

recognizer = sr.Recognizer()
recognizer.energy_threshold = 1000

def listen_and_recognize():
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("Recognizing...")
            ping()
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio, language="en-EN")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Could not request results")

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
    play_obj.wait_done()