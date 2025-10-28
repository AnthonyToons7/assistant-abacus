import os
import re
import json
import subprocess
from handlers.StorageHandler import get_app_by_keyword, save_app_by_keyword

def find_app(keyword):
    # Step 1: Try brain cache
    brain = get_app_by_keyword(keyword)
    if brain:
        return brain


    # Step 2: Try installed .exe
    possibleDirectories = [
        os.path.expandvars("%PROGRAMFILES%"),
        os.path.expandvars("%PROGRAMFILES(X86)%"),
        os.path.expandvars("%LOCALAPPDATA%"),
        os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Packages"),
        os.path.expandvars("C:\\Program Files\\WindowsApps"),
    ]
    for directory in possibleDirectories:
        for root, _, files in os.walk(directory):
            for file in files:
                print(file)
                if file.lower().endswith(".exe") and keyword.lower() in file.lower():
                    path = os.path.join(root, file)
                    # print(f"Found {keyword} at {path}")
                    save_app_by_keyword(keyword, path)
                    return path

    # Step 3: Try MS Store apps
    app_id = find_ms_store_appid(keyword)
    print(app_id)
    if app_id:
        save_app_by_keyword(keyword, app_id)
        return app_id

    return None

def find_ms_store_appid(keyword):
    print(keyword)
    ps_command = f"Get-StartApps | Where-Object {{$_.Name -like '*{keyword}*'}}"

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if not output.startswith("{"):
            return None
        data = json.loads(output)
        return data.get("AppID")
    except Exception:
        return None

def launch_program(identifier):
    try:
        if identifier.endswith(".jpg") or identifier.endswith(".png"):
            print("Error: Image files cannot be launched as programs.")
            return False
        if identifier.endswith("!App"):  # MS Store app
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{identifier}"])
        else: 
            subprocess.Popen([identifier], creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        print(f"Error launching {identifier}: {e}")
        return False

def open_program(keyword):
    app = find_app(keyword)
    if not app:
        print(f"Could not find{keyword}.")
        return False
    return launch_program(app)
