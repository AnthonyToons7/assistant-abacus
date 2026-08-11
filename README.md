# A.B.A.C.U.S.
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
pip install schedule
pip install winregistry
pip install python-dateutil
pip install --upgrade pywin32
pip install winrt
pip install python-dotenvs
pip install PyQtWebEngine
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
pip install dateparser
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
- Added browser data fetching

# Log 24-2-26
- Added a small notification popup for when the app has started

# Log 30-3-26
- Added SpotifyService
- Split save_settings function from popup and moved it to its own module

# Log 7-4-26
- Expanded SpotifyService
    - Full integration
    - Login with api token
    - Play/Pause/Skip/Previous/Search/Playlist
- Changed speech module
    - Abacus will now always listen once clicked, and will execute commands on the go, without needing to be clicked over and over again

# Log 5-8-26
- Added calendar
    - Add items to your calendar! This will help you keep track of things, and A.B.A.C.U.S. will definitely help you remember them.

- Added 'startup' feature
    - Based on time of day, or the day itself (based off of used data), A.B.A.C.U.S. will open up a tab with youtube to end your day with, or open up all your work applications.

- Added manual commands
    + Voice commands not working out for you? In the office so you can't speak commands out loudly? No problem! With manual commands (a middle click on A.B.A.C.U.S.), you can type out your prompt instead, and it will be passed as a normal command to abacus.

    - If you want to add a schedule item manually, then the checklist will run with popups instead of slow voice commands

- Made the settings popup longer

- Prompt menu stays when in "ai mode"

- Added Loopservice for future event checking

- Implemented the "audio response" setting


- Bug fixes
    + Fixed up some directory path fetching
    + Abacus did not save your name when inserting one
    + Fixed "Anti-French" system

## Local AI

You can now run Abacus in two modes:
- Command mode: scripted commands only (existing behavior)
- AI mode: unscripted free conversation with a local GGUF (GPT-Generated Unified Format) model

- `ai_mode` setting toggle
- Local model settings (`ai_model_path`, `ai_system_prompt`, generation knobs)
- STT provider toggle (`google` or local `sphinx`)
- TTS provider toggle (`edge` or local `pyttsx3`)

### Get a local model file
Download a GGUF instruct model (no account required for public models), for example:
- `Qwen3.5-0.8B` (fast, lightweight)
- `Qwen2.5-3B-Instruct` (better quality, heavier)

Put the model in a local folder, e.g.:
`models\Qwen3.5-0.8B-Q8_0.gguf`

I can provide a file on request. It's a small 1.8 GB

### Configure in Abacus settings
- Enable `AI mode`
- Set `AI model path` to your `.gguf` file
- Optional tuning:
    - `AI context size`: `2048`
    - `AI reply length`: `220`
    - `AI creativity`: `0.6`
    - `AI GPU layers`: `0` (CPU only)

For fully local voice loop:
- Set `Speech recognition provider` to `sphinx`
- Set `Text to speech provider` to `pyttsx3`

# Log 7-8-26

- Fixed calendar module. It had some issues with inserting the correct date, timezones, and such.
- Minor name changes
- Fixed LoopService
- Fixed history yoinker
- Fixed Spotify device finder
- Gave the AI a chat bubble ui!
- Minor UI/color changes


# Log 10-8-26
- Added error log service
- Additional settings


# Log 12-8-26
- Bugfixes
- Code cleanup