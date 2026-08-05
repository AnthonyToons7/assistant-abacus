import os
import json
import time
from datetime import datetime, timedelta, timezone
import schedule
import tempfile
from dateutil import parser

from core.storage import get_user_data, set_user_data
from core.listener import give_audio_response
from core.executor import find_app, open_program, give_audio_response, search_web
from ui.popup import open_manual_input

def get_events():
    return get_user_data()["calendar"]

def check_reminders():
    events = get_events()
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")

    for event in events:
        for reminder in event['reminder']:
            if reminder['reminded']:
                continue

            event_start = datetime.strptime(event['start_date'], "%H:%M:%S")
            difference = now - event_start.strftime("%H:%M:%S")

            if difference.total_seconds() <= datetime.strptime(reminder['time'], "%H:%M:%S").total_seconds():
                give_audio_response(f"Reminder: {event['title']} is starting at {event['start_date']}")
                reminder['reminded'] = True
                
def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

def reminder_loop():
    schedule.every(10).seconds.do(check_reminders)
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()

def create_event(title, description, start_date, end_date, reminder=[]):
    schedule = get_events()
    schedule.append({
        "title": title,
        "description": description,
        # TODO: string to datetime string
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "reminder": reminder
    })
    set_user_data("calendar", schedule)

def delete_event(title):
    schedule = get_events()
    schedule = [event for event in schedule if event['title'] != title]
    set_user_data("calendar", schedule)

def startup():
    user_data = get_user_data()
    current_date = datetime.now()
    greeting = get_greeting(current_date.hour)

    # TODO: add dropdown for user to select their working days and hours
    work_data = user_data["work_days"]
    work_days = work_data["days"]
    work_apps = work_data["applications"]

    if current_date.hour >= 8 and current_date.strftime("%A") in work_days:
        give_audio_response(f'{greeting}, {user_data["name"]}. Opening your work applications.')

        for app in work_apps:
            print(f"Opening {app}...")
            # open_program(app)
    
    else:
        give_audio_response(f'{greeting}, {user_data["name"]}. Day off? Enjoy your day!')
        open_program('Firefox', 'https://youtube.com')
        # search_web("", 'https://youtube.com')

def get_greeting(time):
    if time < 12:
        return 'Good morning'
    elif 12 <= time < 18:
        return 'Good afternoon'
    else:
        return 'Good evening'

def schedule_checklist(source):
    data = {}
    required_fields = {
        "title": {
            "question": "What is the title of the event?",
            "value": None
        },
        "description": {
            "question": "Add a description?",
            "value": None
        },
        "start_date": {
            "question": "When does it start?",
            "value": None
        },
        "end_date": {
            "question": "When does it end?",
            "value": None
        },
        "reminder": {
            "question": "Do you want a reminder?",
            "value": None
        }
    }

    print(source)
    for field_key, field_value in required_fields.items():
        if source == "voice":
            give_audio_response(field_value["question"])
        
        data[field_key] = listen_and_recognize() if source == "voice" else open_manual_input(field_value["question"])

    # old
    # give_audio_response("What is the title of the event?")
    # data['title'] = listen_and_recognize() if source == "voice" else open_manual_input()

    # give_audio_response("Add a description?")
    # data['description'] = listen_and_recognize() if source == "voice" else open_manual_input()

    # give_audio_response("When does it start?")
    # start = parse_date(listen_and_recognize() if source == "voice" else open_manual_input())

    # give_audio_response("When does it end?")
    # end = parse_date(listen_and_recognize() if source == "voice" else open_manual_input())

    # give_audio_response("Do you want a reminder?")
    # reminder = listen_and_recognize() if source == "voice" else open_manual_input()

    # TODO: convert comma seperated reminders to array


    create_event(
        data['title'],
        data['description'],
        data['start_date'],
        data['end_date'],
        reminder=[data['reminder']] if data['reminder'] else []
    )

    give_audio_response("Event added.")