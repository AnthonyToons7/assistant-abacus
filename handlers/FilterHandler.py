import pyautogui
import os
import subprocess
import re
from handlers.ProgramHandler import open_program

def filter(text):
    text = text.lower()
    activation_commands = ['send', 'open']
    # availablePlatforms = ['discord', 'whatsapp', 'spotify']

    # TODO: make arrays with apps based off of what the commands are. for example:
    # activation_commands = 'send'
    # availableApps = ['discord', 'whatsapp', 'telegram']
    # Try to filter through what purpose is what app. Furthermore, add additional filters for misspeaking just like 'jar fish'

    for activation_word in activation_commands:
        if activation_word in text:
            activation_word = activation_word
            break 

    before_keyword, keyword, after_keyword = text.partition(activation_word)

    if activation_word == 'open':
        if keyword == '':
            return None

        program = open_program(after_keyword.strip())
        return 'Success!'
