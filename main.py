import getpass
import sys
import re
from handlers.FilterHandler import filter
from handlers.AudioHandler import listen_and_recognize, give_audio_response
from handlers.PopupHandler import AbacusSprite
from PyQt5.QtWidgets import QApplication

# Fallback in case pyaudio picks up the wrong name
recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)

def analyze_user_audio(text):
    if(re.search(recognized_names_pattern, text, re.IGNORECASE)):
        suc = filter(text)
        if(suc is not None):
            print("Exiting...") 
            sys.exit()
        else:
            print(f"Hello {getpass.getuser()}, how can I help you?")

    else:
        give_audio_response("Sorry, I could not understand. Could you repeat that for me?")

def start():
    # # Default test message
    text = 'Abacus, send a message on Whatsapp'
    
    text = listen_and_recognize() or ''
    print("Input: [ ", text, " ]")
    analyze_user_audio(text)

def main():
    # Sprite testing
    app = QApplication(sys.argv)
    sprite = AbacusSprite()
    # sprite = RockSprite()
    sys.exit(app.exec_())

    # Initiating speech model
    # pyaudio_init = pyaudio.PyAudio()
    # input_device_info = pyaudio_init.get_default_input_device_info()
    # print("Microphone:", input_device_info["name"])

if __name__ == "__main__":
    main()