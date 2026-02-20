import sys
from PyQt5.QtWidgets import QApplication
from ui.popup import AbacusSprite
from core.pipeline import start

def main():
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