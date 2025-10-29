import speech_recognition as sr
import pyttsx3
import re
from handlers.StorageHandler import user

text_to_speech = pyttsx3.init()

recognizer = sr.Recognizer()
recognizer.energy_threshold = 1000

def listen_and_recognize():
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source)
            print("Recognizing...")
            audio = recognizer.listen(source)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Could not request results")

def give_audio_response(message):
    text_to_speech.say(f'A message, {user}? Sure, on what platform?')
    text_to_speech.runAndWait()