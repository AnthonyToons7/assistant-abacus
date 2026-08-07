import sys
from PyQt5.QtWidgets import QApplication

from ui.popup import AbacusSprite, ChatDock, show_toast
from core.pipeline import start, init_pipeline, register_chat_listener
from core.translations import load_translations
from core.storage import get_saved_settings
from services.SpotifyService import SpotifyService

def main():
    saved = get_saved_settings()
    load_translations(saved.get("display_lang", "en"))

    app = QApplication(sys.argv)
    init_pipeline()
    sprite = AbacusSprite(on_click=start)
    chat_dock = ChatDock(sprite)
    sprite.attach_chat_dock(chat_dock)
    register_chat_listener(chat_dock.enqueue_message)
    # show_toast("App has started", "A.B.A.C.U.S. is running!", sprite)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()