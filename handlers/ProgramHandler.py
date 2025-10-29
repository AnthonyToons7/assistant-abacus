import os
import json
import subprocess
from handlers.StorageHandler import get_app_by_keyword, save_app_by_keyword
from handlers.AudioHandler import listen_and_recognize
from services.ProtocolService import get_protocol 

def find_app(keyword):
    # Step 1: Try storage cache
    app_in_storage = get_app_by_keyword(keyword)
    if app_in_storage:
        return app_in_storage
    
    # Step 2: Try MS Store apps
    app_id = find_ms_store_appid(keyword)
    print(app_id)
    if app_id:
        save_app_by_keyword(keyword, app_id)
        return app_id

    # Step 3: Try to find installed .exe
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
                if file.lower().endswith(".exe") and keyword.lower() in file.lower():
                    path = os.path.join(root, file)
                    save_app_by_keyword(keyword, path)
                    return path
                
    return None

def find_ms_store_appid(keyword):
    print(keyword)
    ps_command = f"""Get-StartApps | Where-Object {{ $_.Name -like '*{keyword}*' }} | Select-Object Name, AppID | ConvertTo-Json"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if not output:
            return None
        data = json.loads(output)

        if isinstance(data, list):
            return data[0].get("AppID")
        else:
            return data.get("AppID")
    except Exception as e:
        print("Error:", e)
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
        print(f'Could not find {keyword}.')
        return False
    return launch_program(app)

def message_checklist(application):
    # TODO in data/protocols is a json that needs to be looped through
    #  It contains the 3 important factors for sending a message: app, receiver and message
    #  With each protocol, you check if there is data for that protocol. If there isn't, ask for data using listen_and_recognize()

    # TODO: when confirming your selections for app, receiver and message, make a function in AudioHandler, that checks for 'Yes' and 'No',
    #  returning True or False depending on the answer, then, use a ternary operator for decision making.
    
    # messaging_platform = listen_and_recognize()
    # print(messaging_platform)

    protocols = get_protocol('message_checklist')

    for protocol in protocols:
        print(protocol)