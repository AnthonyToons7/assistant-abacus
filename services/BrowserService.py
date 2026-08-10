import os
import shutil
import sqlite3
import tempfile
import winreg
import json
import threading
import time
from datetime import datetime, timedelta, timezone
import schedule
import tempfile
from dateutil import parser
from core.storage import get_user_data, set_user_data
from services.ErrorLogService import add_log_entry


def get_local_timezone():
    return datetime.now().astimezone().tzinfo


def to_local_iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(get_local_timezone()).isoformat()


def parse_timestamp(value):
    if not value:
        return None
    ts = parser.isoparse(value)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=get_local_timezone())
    return ts


def normalize_browser_data(raw_browser_data):
    if isinstance(raw_browser_data, str):
        return {
            "default_browser": raw_browser_data,
            "history": [],
            "last_timestamp": None
        }

    if not isinstance(raw_browser_data, dict):
        return {
            "default_browser": None,
            "history": [],
            "last_timestamp": None
        }

    history = raw_browser_data.get("history", [])
    if not isinstance(history, list):
        history = []

    return {
        "default_browser": raw_browser_data.get("default_browser"),
        "history": history,
        "last_timestamp": raw_browser_data.get("last_timestamp")
    }

def save_results(data):
    browser_data = normalize_browser_data(data.get("browserData"))
    browser_data["history"].sort(
        key=lambda e: e.get("timestamp") or "",
        reverse=True
    )
    set_user_data("browserData", browser_data)

def ensure_browser_data():
    data = get_user_data()
    data["browserData"] = normalize_browser_data(data.get("browserData"))
    save_results(data)
    return data

def get_default_browser():
    path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
        prog_id, _ = winreg.QueryValueEx(key, "ProgId")
    return prog_id

def set_default_browser(browser_name):
    data = ensure_browser_data()
    data["browserData"]["default_browser"] = browser_name
    save_results(data)

def add_history_entries(entries):
    data = ensure_browser_data()
    last_ts_str = data["browserData"]["last_timestamp"]
    try:
        last_ts = parse_timestamp(last_ts_str)
    except (TypeError, ValueError):
        last_ts = None
    new_last_ts = last_ts

    existing = {
        (e.get("url"), e.get("timestamp"))
        for e in data["browserData"]["history"]
        if isinstance(e, dict)
    }

    for entry in entries:
        entry_ts = entry.get("timestamp") if isinstance(entry, dict) else None
        if not entry_ts:
            continue

        ts = parse_timestamp(entry_ts)
        if last_ts and ts < last_ts:
            continue

        key = (entry.get("url"), entry_ts)
        if key not in existing:
            data["browserData"]["history"].append({
                "timestamp": entry_ts,
                "title": entry.get("title") or "",
                "url": entry.get("url")
            })
            existing.add(key)

        if not new_last_ts or ts > new_last_ts:
            new_last_ts = ts

    if new_last_ts:
        data["browserData"]["last_timestamp"] = new_last_ts.isoformat()

    save_results(data)

def query_sqlite_db(db_path, query):
    if not os.path.exists(db_path):
        return []

    temp_path = os.path.join(tempfile.gettempdir(), f"tmp_history_{os.getpid()}.db")
    shutil.copy2(db_path, temp_path)
    
    for ext in ("-wal", "-shm"):
        src = db_path + ext
        if os.path.exists(src):
            shutil.copy2(src, temp_path + ext)

    try:
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        print("Error querying SQLite DB:", e)
        add_log_entry("Error querying SQLite DB", str(e), type(e).__name__)
        rows = []
    finally:
        conn.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return rows

def chromium_timestamp_to_datetime(ts):
    return datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ts)

def get_chromium_history(db_path):
    query = """
        SELECT url, title, last_visit_time
        FROM urls
        ORDER BY last_visit_time DESC
        LIMIT 25
    """
    rows = query_sqlite_db(db_path, query)
    results = []
    for url, title, visit_time in rows:
        dt = chromium_timestamp_to_datetime(visit_time) if visit_time else None
        results.append({
            "timestamp": to_local_iso(dt),
            "title": title,
            "url": url
        })
    return results

def get_chrome_history():
    user = os.environ["USERNAME"]
    path = fr"C:\Users\{user}\AppData\Local\Google\Chrome\User Data\Default\History"
    return get_chromium_history(path)

def get_edge_history():
    user = os.environ["USERNAME"]
    path = fr"C:\Users\{user}\AppData\Local\Microsoft\Edge\User Data\Default\History"
    return get_chromium_history(path)

def get_brave_history():
    user = os.environ["USERNAME"]
    path = fr"C:\Users\{user}\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History"
    return get_chromium_history(path)

def get_firefox_history():
    user = os.environ["USERNAME"]
    profiles_path = fr"C:\Users\{user}\AppData\Roaming\Mozilla\Firefox\Profiles"
    if not os.path.exists(profiles_path):
        return []

    profile = next((f for f in os.listdir(profiles_path) if ".default" in f), None)
    if not profile:
        return []

    db_path = os.path.join(profiles_path, profile, "places.sqlite")
    query = """
        SELECT moz_places.url, moz_places.title, moz_historyvisits.visit_date
        FROM moz_places
        JOIN moz_historyvisits
        ON moz_places.id = moz_historyvisits.place_id
        ORDER BY moz_historyvisits.visit_date DESC
        LIMIT 25
    """

    rows = query_sqlite_db(db_path, query)
    results = []
    for url, title, visit_date in rows:
        dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=visit_date)
        results.append({
            "timestamp": to_local_iso(dt),
            "title": title,
            "url": url
        })
    return results

def yoink_browser_history():
    try:
        prog_id = get_default_browser()
        prog_id = prog_id.lower()

        if "chrome" in prog_id:
            history = get_chrome_history()
        elif "msedge" in prog_id:
            history = get_edge_history()
        elif "brave" in prog_id:
            history = get_brave_history()
        elif "firefox" in prog_id:
            history = get_firefox_history()
        else:
            print("Unsupported browser")
            return

        add_history_entries(history)
    except Exception as e:
        print("Error in yoink_browser_history:", e)
        add_log_entry("Error in yoink_browser_history", str(e), type(e).__name__)

