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

def save_results(data):
    data["browserData"]["history"].sort(key=lambda e: e["timestamp"], reverse=True)
    set_user_data("browserData", data["browserData"])

def ensure_browser_data():
    data = get_user_data()
    if "browserData" not in data:
        data["browserData"] = {"default_browser": None, "history": []}
    save_results(data)
    return data

def get_default_browser():
    path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
        prog_id, _ = winreg.QueryValueEx(key, "ProgId")
    return prog_id

def set_default_browser(browser_name):
    data = get_user_data()
    if "browserData" not in data:
        data["browserData"] = {"default_browser": None, "history": []}

    data["browserData"]["default_browser"] = browser_name
    save_results(data)

def add_history_entries(entries):
    data = get_user_data()
    last_ts_str = data["browserData"].get("last_timestamp")
    last_ts = parser.isoparse(last_ts_str) if last_ts_str else None
    new_last_ts = last_ts

    existing = {(e["url"], e["timestamp"]) for e in data["browserData"]["history"]}

    for entry in entries:
        ts = parser.isoparse(entry["timestamp"])
        if last_ts and ts < last_ts:
            continue

        key = (entry["url"], entry["timestamp"])
        if key not in existing:
            data["browserData"]["history"].append({
                "timestamp": entry["timestamp"],
                "title": entry.get("title") or "",
                "url": entry["url"]
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
            "timestamp": dt.isoformat() if dt else None,
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
        dt = datetime(1970, 1, 1) + timedelta(microseconds=visit_date)
        results.append({
            "timestamp": dt.isoformat(),
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
        print('Fetched')

    except Exception as e:
        print("Error in yoink_browser_history:", e)

