import pyaudio
import speech_recognition as sr
import getpass
import sys
import re
from handlers.FilterHandler import filter
from handlers.AudioHandler import listen_and_recognize

# Fallback in case pyaudio picks up the wrong name
recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)

# TODO: save all audio executed to a folder named 'audio-logs'. Everytime Abacus is initiated, check for the audio logs, and remove them if they're older than a week
def analyze_user_audio(text):
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
    pyaudio_init = pyaudio.PyAudio()
    input_device_info = pyaudio_init.get_default_input_device_info()
    print("Microphone:", input_device_info["name"])
    # Default test message
    text = 'Abacus, send a message'
    print("Input: [ ", text, " ]")
    
    # text = listen_and_recognize() or ''
    analyze_user_audio(text)

if __name__=="__main__":
    main()