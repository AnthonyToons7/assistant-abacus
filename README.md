# Abacus
'Absolutely Brutal And Completely Unhinged Sociopath' or A.B.A.C.U.S., is an small voice 'assistant' system made by me. I designed him to help with small tasks and make my life a little bit easier and more fun.

## How does Abacus work?
Abacus listens to its activation name:
- Abacus

When the keyword name is recognized, it will then start listening to your words, and based on what you said, it will execute it!
It calculates with the words you said to form a proper command, and then executes this command. It's easier said than done.

Abacus will learn from you depending on the way you talk, and what he recognizes

## Permissions
As dangerous as it sounds, Abacus DOES need terminal permissions. It needs to access more than a normal user would be comfortable with. 


## Settings
When starting the application you have a small panel where you can decide Abacus' his actions. If you want a popup overlay sprite where his response is showed, then turn that on in the settings!
There are a couple settings available:
- Show / Hide sprites
- Voice responses on/off
- Text responses on/off
- Default browser
- Allow browser history access (he needs that for... experimental reasons)
- Background listening (application is closed and abacus will ALWAYS listen to you, but wont execute anything until his name is called)

## Commands for model installations
When installing, use `venv\Scripts\activate`. These are the models you need installed into the project, so you don't need to install them globally. This python project is built in a virtual environment.
```
pip install pyautogui
pip install SpeechRecognition
pip install deepmultilingualpunctuation
pip install pyaudio
pip install pyttsx3
pip install simpleaudio
pip install pocketsphinx
pip install PyQt5
pip install pywhatkit
pip install pyqtgraph
pip install OpenGL
pip install PyOpenGL PyOpenGL_accelerate
pip install ddgs
pip install -U duckduckgo-search
pip install numpy
pip install edge-tts
pip install pygame
pip install -U deep-translator
```

## Structure
    main.py
        └─> starts the UI (popup.py)
        └─> starts pipeline.py

    pipeline.py
        └─> listener.py     (capture audio)
            └─> filter.py  (clean and validate it)
                    └─> executor.py  (run the command)

### Protocols
Protocols are simple tasks that are meant to be executed in a specific order. These protocols are saved in a JSON file, and are meant to follow specific scenarios.

# Log 27-10
- Name change
- Added better scraping and an extra section for executables for programs in the MS store
- Splitted more functions to handlers to keep each functionality in it's own handler
- Renamed brain to storage

# Log 31-10
- record/listen does not work when you play an adio que before it, resorted to text showing instead
- TODO: Better visual indicator for indicating listener is listening

# Log 7-10
- Made a seperate branch for phone-remote-control
- Merged speaking border and cross platform messaging

# Log 3-2-26
- Chat, we can search

# Log 20-2-26
- New file structure. The 'handler' structure was getting tangled up, so I made it shorter and more streamlined:
    main.py
        └─> starts the UI (popup.py)
        └─> starts pipeline.py

    pipeline.py
        └─> listener.py     (capture audio)
            └─> filter.py  (clean and validate it)
                    └─> executor.py  (run the command)

# Log 23-2-26
- Added a TTS module so text to speech sounds a little bit more human
- Added a translation module in order to translate the TTS messages to the correct language that was selected in your settings