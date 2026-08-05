import getpass
import re
import schedule
import time
import threading
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer

from core.filter import filter
from core.listener import listen_and_recognize, give_audio_response, start_always_on
from core.ai_abacus import ai_abacus
from core.storage import get_saved_settings
from services.BrowserService import get_default_browser, yoink_browser_history
from services.SpotifyService import SpotifyService
from services.LoopService import loop_list

recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh', 'Abacuzzeh','Abakuzzeh','Abacuzzehh','Abakuzzehh','Abacuzzehh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)
repeat_counter = 0
on_speech = None

def analyze_user_audio(text):
    global repeat_counter
    if re.search(recognized_names_pattern, text, re.IGNORECASE):
        suc = filter(text, "voice")
        if(suc is not None):
            print("Waiting...")
        else:
            print(f"Hello {settings['name']}, how can I help you?")

    else:
        if(repeat_counter >= 1):
            print('Stopping with trying...')
        else:
            print("Sorry, I could not understand. Could you repeat that for me?")
            give_audio_response("Sorry, I could not understand. Could you repeat that for me?")
            QApplication.processEvents()
            text = listen_and_recognize()
            analyze_user_audio(text.lower())

def get_on_speech():
    return on_speech


def _speak_if_enabled(message):
    settings = get_saved_settings()
    if settings.get("audio_response", False):
        give_audio_response(message)


def handle_ai_chat(text):
    try:
        reply = ai_abacus.chat(text)
    except FileNotFoundError as e:
        reply = (
            "AI mode is enabled, but the model file path is invalid. "
            "Open settings and set a valid .gguf path."
        )
        print(f"AI model path error: {e}")
    except ValueError:
        reply = "AI mode is enabled, but ai_model_path is empty in settings."
    except RuntimeError:
        reply = "AI mode needs llama-cpp-python installed first."
    except Exception as e:
        reply = "AI mode failed to generate a response. Check the console for details."
        print(f"AI generation error: {e}")
        print(f"Python executable: {sys.executable}")

    print(f"A.B.A.C.U.S.: {reply}")
    _speak_if_enabled(reply)

def _on_speech_handler(text, source):
    settings = get_saved_settings() 
    name = settings["name"]
    print(f"{name}: {text}")

    settings = get_saved_settings()
    ai_mode = settings.get("ai_mode", False)

    result = filter(text, source)

    if result:
        print("Waiting...")
        return

    if ai_mode:
        handle_ai_chat(text)
        return

    print("Unknown command")

def init_pipeline():
    global on_speech
    on_speech = _on_speech_handler

    # loop_list()

def start():
    if on_speech is None:
        init_pipeline()
    threading.Thread(target=start_always_on, args=(on_speech,), daemon=True).start()

    # TODO: REMOVE
    # OLD OPTION FOR LISTENING
    # Default test message
    # text = 'Abacus, play my playlist soft rock'
    
    # text = listen_and_recognize()
    
    # print("Input: [ ", text, " ]")
    # analyze_user_audio(text.lower())