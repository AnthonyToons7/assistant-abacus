import getpass
import re
from core.filter import filter
from core.listener import listen_and_recognize, give_audio_response
from PyQt5.QtWidgets import QApplication

# Fallback in case pyaudio picks up the wrong name
recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh', 'Abacuzzeh','Abakuzzeh','Abacuzzehh','Abakuzzehh','Abacuzzehh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)
repeat_counter = 0

def analyze_user_audio(text):
    global repeat_counter
    if(re.search(recognized_names_pattern, text, re.IGNORECASE)):
        suc = filter(text)
        if(suc is not None):
            print("Waiting...") 
            # sys.exit()
        else:
            print(f"Hello {getpass.getuser()}, how can I help you?")

    else:
        if(repeat_counter >= 1):
            print('Stopping with trying...')
        else:
            print("Sorry, I could not understand. Could you repeat that for me?")
            give_audio_response("Sorry, I could not understand. Could you repeat that for me?")
            QApplication.processEvents()
            text = listen_and_recognize()
            analyze_user_audio(text.lower())

def start():
    # TTS TRANSLATION TEST
    # give_audio_response("This is a translation test")
    # return

    # Default test message
    text = 'Abacus, search a'
    # text = listen_and_recognize()
    
    print("Input: [ ", text, " ]")
    analyze_user_audio(text.lower())