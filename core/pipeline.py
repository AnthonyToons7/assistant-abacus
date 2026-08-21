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
from core.ai_abacus import ai_abacus, ModelPathNotSetError
from core.storage import get_saved_settings
from services.BrowserService import get_default_browser, yoink_browser_history
from services.SpotifyService import SpotifyService
from services.LoopService import loop_list
from services.ErrorLogService import add_log_entry

recognized_names = ['Abacus','Aba cus','Abe cus','Abakus','Abak us','Abacuss','Abakuss','Abacusss','Abakusss','Abakuz','Abacuz','Abacusz','Abaxus','Abaxuss','Abakos','Abakoss','Abacous','Abacoush','Abacush','Abacose','Abacosee','Abakose','Abakosee','Abakuzh','Abacuzh','Abacushh','Abakush','Abakushh','Abakusse','Abacusse','Abakuse','Abacuse','Abakusseh','Abacuseh','Abacushe','Abakushhe','Abakushh','Abacuzze','Abakuzze','Abacuzzeh','Abakuzzeh','Abakuzzehh','Abacuzzehh','Abacuzzeh','Abakuzzehh', 'Abacuzzeh','Abakuzzeh','Abacuzzehh','Abakuzzehh','Abacuzzehh','Abakuzzehh']
recognized_names_pattern = "|".join(recognized_names)
repeat_counter = 0
on_speech = None
chat_listeners = []
typing_listeners = []

def register_chat_listener(listener):
    if callable(listener) and listener not in chat_listeners:
        chat_listeners.append(listener)

def register_typing_listener(listener):
    if callable(listener) and listener not in typing_listeners:
        typing_listeners.append(listener)

def emit_chat(role, message, session_id=""):
    if isinstance(session_id, tuple):
        session_id = session_id[0] if session_id else ""
    session_id = "" if session_id is None else str(session_id)
    for listener in list(chat_listeners):
        try:
            listener(role, message, session_id)
        except Exception as e:
            print(f"Chat listener error: {e}")
            add_log_entry("Chat listener error", str(e), type(e).__name__)

def emit_typing(is_typing):
    for listener in list(typing_listeners):
        try:
            listener(bool(is_typing))
        except Exception as e:
            print(f"Typing listener error: {e}")
            add_log_entry("Typing listener error", str(e), type(e).__name__)

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
            give_audio_response("Sorry, I could not understand. Could you repeat that for me?")
            QApplication.processEvents()
            text = listen_and_recognize()
            analyze_user_audio(text.lower())

def get_on_speech():
    return on_speech

def speak_if_enabled(message):
    settings = get_saved_settings()
    if settings.get("audio_response", False):
        give_audio_response(message)

def handle_ai_chat(text):
    try:
        reply = ai_abacus.chat(text)
    except ModelPathNotSetError:
        reply = "AI mode is enabled, but ai_model_path is empty in settings."
    except FileNotFoundError as e:
        reply = (
            "AI mode is enabled, but the model file path is invalid. "
            "Open settings and set a valid .gguf path."
        )
        print(f"AI model path error: {e}")
        add_log_entry("AI model path error", str(e), type(e).__name__)
    except ValueError as e:
        reply = f"AI mode failed to generate a response: {e}"
        print(f"AI generation error: {e}")
        add_log_entry("AI generation error", str(e), type(e).__name__)
    except RuntimeError:
        reply = "AI mode needs llama-cpp-python installed first."
    except Exception as e:
        reply = "AI mode failed to generate a response. Check the console for details."
        print(f"AI generation error: {e}")
        print(f"Python executable: {sys.executable}")
        add_log_entry("AI generation error", f"{e}\nPython executable: {sys.executable}", type(e).__name__)

    print(f"A.B.A.C.U.S.: {reply}")
    emit_chat("assistant", reply, ai_abacus.session_id or "")
    speak_if_enabled(reply)

def _on_speech_handler(text, source):
    settings = get_saved_settings() 
    name = settings["name"]

    if source == "voice" and settings.get("toggle_activation_word", True):
        match = re.match(rf"^\s*(?:{recognized_names_pattern})[\s,]*", text, re.IGNORECASE)
        if not match:
            return
        text = text[match.end():].strip() or text

    print(f"{name}: {text}")
    emit_chat("user", text, ai_abacus.session_id or "")

    settings = get_saved_settings()
    ai_mode = settings.get("ai_mode", False)

    if ai_mode:
        emit_typing(True)
        try:
            handle_ai_chat(text)
        finally:
            emit_typing(False)
        return

    result = filter(text, source)

    if result:
        print("Waiting...")
        emit_chat("assistant", "Working on that...", ai_abacus.session_id or "")
        return

    print("Unknown command")
    emit_chat("assistant", "Unknown command.", ai_abacus.session_id or "")

def init_pipeline():
    global on_speech
    on_speech = _on_speech_handler

    loop_list()

def start():
    if on_speech is None:
        init_pipeline()
    threading.Thread(target=start_always_on, args=(on_speech,), daemon=True).start()