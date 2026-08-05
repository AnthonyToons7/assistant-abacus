import re
import os
import sys
import threading
from PyQt5.QtWidgets import QApplication

from core.web import search_web
from core.executor import open_program, message_checklist
from services.SpotifyService import run as spotify_run
from services.CalendarService import startup, schedule_checklist

def filter(text, source):
    text = text.lower()
    activation_commands = ['send', 'open', 'fetch', 'search', 'look', 'settings', 'play', 'pause', 'resume', 'skip', 'startup', 'schedule', 'plan', 'add', 'kys']

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
        
        if activation_word == 'play':
            match = re.search(r'play\s+(my|the)?\s*(song|playlist)\s+(.+?)(?:\s+(?:on|from|in my)\s+(.+))?$', text, re.IGNORECASE)
            
            if not match:
                print(f"Unrecognized command format: '{text}'")
                return

            prompt_owner = match[1]  # 'my' or 'the'
            prompt_type  = match[2]  # 'playlist' or 'song'
            prompt_qry   = match[3]  # the name of the playlist or song
            prompt_extra = match[4]  # connect to a different device
            
            # examples:
            # "Abacus, play my playlist Lofi"
            # "Abacus, play the song Bohemian Rhapsody"
            # "Abacus, play my playlist Lofi on my phone"
            break;

        if activation_word in ['schedule', 'plan', 'add']:
            print("Scheduling command detected")
            if 'event' in text or 'calendar' in text:
                print("Calendar event command detected")
                activation_word = 'schedule'
                break

        if activation_word == 'kys':
            os._exit(1)

    match activation_word:
        case 'send':
            message_checklist(application, source)
        case 'open':
            open_program(application)
        case 'search':
            search_web(search_prompt)
        case 'play':
            spotify_run(prompt_type, prompt_qry, prompt_owner, prompt_extra)
        case 'pause' | 'resume' | 'skip' | 'previous':
            spotify_run(None, None, None, None, command=activation_word)
        case 'startup':
            startup()
        case 'schedule':
            schedule_checklist(source)
        case _:
            return None
            
    return 'Success!'
