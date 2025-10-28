import pyaudio
import speech_recognition as sr
import getpass
import sys
import re
from handlers.FilterHandler import filter
from handlers.AudioHandler import listen_and_recognize
# from deepmultilingualpunctuation import PunctuationModel

# model = PunctuationModel()
p = pyaudio.PyAudio()
input_device_info = p.get_default_input_device_info()

print("Microphone:", input_device_info["name"])
p.terminate()

recognized_names = ['Abacus', 'Ryui', 'Aba cus', 'Ryu i', 'Abe cus', 'Ryu yi']
recognized_names_pattern = "|".join(recognized_names)

# TODO: save all audio executed to a folder named 'audio-logs'. Everytime Abacus is initiated, check for the audio logs, and remove them if they're older than a week
def analyze(text):
    # TODO: create a big filter function that filters out words that are like 'Abacus', and accept those too
    if(re.search(recognized_names_pattern, text, re.IGNORECASE)):
        suc = filter(text)
        if(suc is not None):
            # TODO: find out how to kill all scripts, but keep the program running outside of the in-project terminal
            print("Exiting script...") 
            sys.exit()
        else:
            print(f"Hello {getpass.getuser()}, how can I help you?")

    else:
        # TODO: allow Abacus to speak back with 'Sorry, I could not understand. Could you repeat that for me?'
        print("Activation word not found in text.")

def main():

    with sr.Microphone() as source:
        try:
            # text = listen_and_recognize(source)
            # Default test message
            text = 'Abacus, open notepad'
            # print("Input: [ ", model.restore_punctuation(text), " ]")
            analyze(text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Could not request results")

if __name__=="__main__":
    main()