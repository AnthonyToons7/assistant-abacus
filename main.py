import sys
from PyQt5.QtWidgets import QApplication
from ui.popup import AbacusSprite, show_toast
from core.pipeline import start
from core.translations import load_translations
from core.storage import get_saved_settings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QPoint, QPropertyAnimation, QEasingCurve, Qt


def main():
    saved = get_saved_settings()
    load_translations(saved.get("display_lang", "en"))
    
    app = QApplication(sys.argv)
    sprite = AbacusSprite(on_click=start)
    show_toast("App has started", "A.B.A.C.U.S. is running!", sprite)
    sys.exit(app.exec_())
    
    # Initiating speech model
    # pyaudio_init = pyaudio.PyAudio()
    # input_device_info = pyaudio_init.get_default_input_device_info()
    # print("Microphone:", input_device_info["name"])

if __name__ == "__main__":
    main()