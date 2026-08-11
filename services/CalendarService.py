import json
import time
import schedule
import dateparser
from datetime import datetime, timedelta, timezone, date
from dateutil import parser

from core.storage import get_user_data, set_user_data
from core.listener import give_audio_response
from core.executor import open_program, give_audio_response, listen_and_recognize
from ui.popup import open_manual_input, show_toast

def get_events():
    user_data = get_user_data()
    raw_calendar = user_data.get("calendar", [])

    if isinstance(raw_calendar, list):
        return raw_calendar

    if isinstance(raw_calendar, dict):
        nested_calendar = raw_calendar.get("calendar")
        if isinstance(nested_calendar, list):
            set_user_data("calendar", nested_calendar)
            return nested_calendar

    set_user_data("calendar", [])
    return []

def check_reminders():
    events = get_events()
    now_dt = datetime.now(timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo

    for event in events:
        if not isinstance(event, dict):
            continue

        reminders = event.get('reminder', [])
        if isinstance(reminders, dict):
            reminders = [reminders]
        if not isinstance(reminders, list):
            continue

        for reminder in reminders:
            if not isinstance(reminder, dict):
                continue
            if reminder.get('reminded'):
                continue

            reminder_raw_time = reminder.get('time')
            if not reminder_raw_time:
                continue

            try:
                reminder_time = datetime.fromisoformat(str(reminder_raw_time).replace('Z', '+00:00'))
            except (TypeError, ValueError):
                continue

            if reminder_time.tzinfo is None:
                reminder_time = reminder_time.replace(tzinfo=local_tz)

            reminder_time_utc = reminder_time.astimezone(timezone.utc)
            reminder_time_local = reminder_time.astimezone(local_tz)
            now_local = now_dt.astimezone(local_tz)
            difference = now_dt - reminder_time_utc

            if reminder_time_utc <= now_dt and difference.total_seconds() < 60:
                event_title = event.get('title', 'Event')
                event_start = event.get('start_date', 'soon')
                event_start_human = format_event_time_for_people(event_start, local_tz)
                give_audio_response(f"Reminder: {event_title} is starting {event_start_human}")
                show_toast(f"Reminder: {event_title}", f"{event_title} is starting {event_start_human}")
                reminder['reminded'] = True
                set_user_data("calendar", events)

def format_event_time_for_people(event_start, local_tz):
    if not event_start:
        return "soon"

    try:
        event_dt = datetime.fromisoformat(str(event_start).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return f"at {event_start}"

    if event_dt.tzinfo is None:
        event_dt = event_dt.replace(tzinfo=local_tz)
    else:
        event_dt = event_dt.astimezone(local_tz)

    return f"on {event_dt.strftime('%A')} {event_dt.day} {event_dt.strftime('%B at %H:%M')}"

def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

def create_event(title, description, start_date, end_date, reminder=None):
    events = get_events()
    reminder_list = reminder if isinstance(reminder, list) else []

    events.append({
        "title": title,
        "description": description,
        "start_date": json_serial(dateparser.parse(start_date)),
        "end_date": json_serial(dateparser.parse(end_date)),
        "reminder": reminder_list
    })
    set_user_data("calendar", events)

def delete_event(title):
    events = get_events()
    events = [event for event in events if isinstance(event, dict) and event.get('title') != title]
    set_user_data("calendar", events)

def startup():
    user_data = get_user_data()
    current_date = datetime.now()
    greeting = get_greeting(current_date.hour)

    # TODO: add dropdown for user to select their working days and hours
    work_data = user_data["work_days"]
    work_days = work_data["days"]
    work_apps = work_data["applications"]

    if current_date.hour >= 7 and current_date.strftime("%A") in work_days:
        give_audio_response(f'{greeting}, {user_data["name"]}. Opening your work applications.')

        for app in work_apps:
            print(f"Opening {app}...")
            open_program(app)
    
    else:
        give_audio_response(f'{greeting}, {user_data["name"]}. Day off? Enjoy your day!')
        open_program('Firefox', 'https://youtube.com')

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
    if source == "voice":
        for field_key, field_value in required_fields.items():
            give_audio_response(field_value["question"])
            data[field_key] = listen_and_recognize() if source == "voice" else open_manual_input(field_value["question"])

    data['title'] = 'New event'
    data['description'] = 'New event with early reminder'
    data['start_date'] = 'Tomorrow, 18:45'
    data['end_date'] = 'Tomorrow, 18:46'

    local_tz = datetime.now().astimezone().tzinfo
    now_local = datetime.now(local_tz)
    reminder_payload = [
        {
            "time": (now_local + timedelta(minutes=1)).isoformat(),
            "reminded": False
        },
        {
            "time": (now_local + timedelta(minutes=2)).isoformat(),
            "reminded": False
        }
    ]

    create_event(
        data['title'],
        data['description'],
        data['start_date'],
        data['end_date'],
        reminder=reminder_payload
    )

    give_audio_response("Event added.")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))