import json
import os
import sys

import pyaudio

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ui.settings_ui import open_settings_window
from core.storage import get_saved_settings, get_user_data, set_user_data
from core.settings import save_settings
from core.translations import load_translations, t


def get_audio_inputs():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            devices.append({"index": i, "name": info["name"]})
    p.terminate()
    return devices


def main():
    initial_tab = sys.argv[1] if len(sys.argv) > 1 else "settings"

    saved = get_saved_settings()
    load_translations(saved.get("display_lang", "en"))

    with open(os.path.join("core", "settings", "available-settings.json"), "r", encoding="utf-8") as f:
        settings = json.load(f)

    def get_calendar_events():
        user_data = get_user_data()
        raw_calendar = user_data.get("calendar", [])

        if isinstance(raw_calendar, list):
            return raw_calendar

        if isinstance(raw_calendar, dict):
            nested_calendar = raw_calendar.get("calendar")
            if isinstance(nested_calendar, list):
                return nested_calendar

        return []

    def set_calendar_events(events):
        set_user_data("calendar", events if isinstance(events, list) else [])

    open_settings_window(
        t=t,
        get_saved_settings=get_saved_settings,
        get_audio_inputs=get_audio_inputs,
        settings=settings,
        save_callback=save_settings,
        setting_actions=None,
        initial_tab=initial_tab,
        get_calendar_events=get_calendar_events,
        set_calendar_events=set_calendar_events,
    )


if __name__ == "__main__":
    main()
