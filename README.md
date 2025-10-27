# Abacus
'All Brains And Completely Unpredictable Shenanigans' or A.B.A.C.U.S., is an small A.I system made by me. I designed him to help with small tasks and make my life a little bit easier and more fun.

## How does Abacus work?
Abacus listens to 2 names:
- Abacus
- Ryui

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
```
pip install pyautogui
pip install pyaudio
pip install SpeechRecognition
pip install deepmultilingualpunctuation
```


# Log 27-10
- Name change
- Added better scraping and an extra section for executables for programs in the MS store
- Splitted more functions to handlers to keep each functionality in it's own handler
- Renamed brain to storage
