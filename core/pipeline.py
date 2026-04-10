import getpass
import re
import schedule
import time
import threading
import threading
import schedule
from core.filter import filter
from core.listener import listen_and_recognize, give_audio_response
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer

from services.BrowserService import get_default_browser, yoink_browser_history
from core.listener import start_always_on
from services.SpotifyService import SpotifyService

recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh', 'Abacuzzeh','Abakuzzeh','Abacuzzehh','Abakuzzehh','Abacuzzehh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)
repeat_counter = 0

def analyze_user_audio(text):
    global repeat_counter
    if re.search(recognized_names_pattern, text, re.IGNORECASE):
        suc = filter(text)
        if(suc is not None):
            print("Waiting...")
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

def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

_on_speech = None

def get_on_speech():
    return _on_speech

def _on_speech_handler(text):
    print(text)
    # if re.search(recognized_names_pattern, text, re.IGNORECASE):
        # result = filter(text)
    result = filter(text)
    print("Waiting..." if result else "Unknown command")

def init_pipeline():
    global _on_speech
    _on_speech = _on_speech_handler

    schedule.every(360).seconds.do(yoink_browser_history)
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()

def start():
    if _on_speech is None:
        init_pipeline()
    threading.Thread(target=start_always_on, args=(_on_speech,), daemon=True).start()
    # TODO: REMOVE
    # OLD OPTION FOR LISTENING
    # Default test message
    # text = 'Abacus, play my playlist soft rock'
    
    # text = listen_and_recognize()
    
    # print("Input: [ ", text, " ]")
    # analyze_user_audio(text.lower())