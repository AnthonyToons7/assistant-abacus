from handlers.ProgramHandler import open_program, message_checklist
from handlers.WebHandler import search_web
import re

def filter(text):
    text = text.lower()
    activation_commands = ['send', 'open', 'fetch', 'search', 'look', 'settings']
    # availablePlatforms = ['discord', 'whatsapp', 'spotify']

    split_text = text.split(' ')
    application = ''
    activation_word = ''
    activation_prompt = ''
    search_prompt = ''

    for i, word in enumerate(split_text):
        if word in activation_commands:
            activation_word = word

        if activation_word == 'open':
            if i + 1 < len(split_text):
                application = split_text[i + 1]
            break

        if activation_word == 'send' and word == 'on':
            if i + 1 < len(split_text):
                application = split_text[i + 1]
            break
  
        if activation_word == 'search' or (activation_word == 'look' and word == 'up'):
            activation_word = 'search'
            search_prompt = re.search('(?:search|look up) (.*)', text)[1]
            break

    match activation_word:
        case 'send':
            message_checklist(application)
        case 'open':
            open_program(application, message)
        case 'search':
            search_web(search_prompt)
        case _:
            return None
            
    return 'Success!'
