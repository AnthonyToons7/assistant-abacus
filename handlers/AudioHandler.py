import speech_recognition as sr
import re
recognizer = sr.Recognizer()
recognizer.energy_threshold = 1000

def listen_and_recognize(source):
    recognizer.adjust_for_ambient_noise(source)
    print("Recognizing...")
    audio = recognizer.listen(source)
    return recognizer.recognize_google(audio)