import json

_translations = {}
_lang = "en"

def load_translations(lang="en"):
    global _translations, _lang
    _lang = lang
    with open("core/settings/translations.json", "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    _translations = all_translations.get(lang, all_translations["en"])

def t(key):
    return _translations.get(key, key)