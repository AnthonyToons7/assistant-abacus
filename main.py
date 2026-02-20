import sys
from PyQt5.QtWidgets import QApplication
from ui.popup import AbacusSprite
from core.pipeline import start
from core.translations import load_translations
from core.storage import get_saved_settings


def main():
    saved = get_saved_settings()
    load_translations(saved.get("display_lang", "en"))
    
    app = QApplication(sys.argv)
    sprite = AbacusSprite(on_click=start)
    # sprite = RockSprite()
    sys.exit(app.exec_())
    
    # Initiating speech model
    # pyaudio_init = pyaudio.PyAudio()
    # input_device_info = pyaudio_init.get_default_input_device_info()
    # print("Microphone:", input_device_info["name"])

if __name__ == "__main__":
    main()