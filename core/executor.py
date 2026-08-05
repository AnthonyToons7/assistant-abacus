import os
import json
import subprocess
import time
import pyautogui
import sys
import os
import shutil
import psutil
from core.storage import get_app_by_keyword, save_app_by_keyword
from core.listener import listen_and_recognize, give_audio_response
from services.ProtocolService import get_protocol
from services.WhatsAppService import send_message as send_whatsapp
from services.DiscordService import send_message as send_discord

def find_app(keyword):
    # Step 1: Try storage cache
    app_in_storage = get_app_by_keyword(keyword)
    if app_in_storage is not None:
        return app_in_storage

    # Step 2: Try MS Store apps
    app_id = find_ms_store_appid(keyword)
    if app_id:
        save_app_by_keyword(keyword, app_id)
        return app_id

    # Step 3: Try to find installed .exe
    # path = shutil.which(keyword)
    # if path:
    #     save_app_by_keyword(keyword, path)
    #     return path
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

        app_id = data[0].get("AppID") if isinstance(data, list) else data.get("AppID")

        if app_id and ("!" in app_id or app_id.endswith(".exe")):
            return app_id
            
        return None
    except Exception as e:
        print("Error:", e)
        return None

# def launch_program(identifier, args=None):
#     try:
#         if identifier.endswith(".jpg") or identifier.endswith(".png"):
#             print("Error: Image files cannot be launched as programs.")
#             return False

#         if identifier.endswith("!App") or "!" in identifier:
#             if args:
#                 os.startfile(args) 
#             else:
#                 subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{identifier}"])
#             return True

#         cmd = [identifier]
#         if args:
#             cmd.append(args)
        
#         subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
#         return True

#     except Exception as e:
#         print(f"Error launching {identifier}: {e}")
#         return False

def open_program(keyword, args=None):
    app = find_app(keyword)
    if not app:
        print(f'Could not find {keyword}.')
        return False
    
    try:
        if keyword.endswith(".jpg") or keyword.endswith(".png"):
            print("Error: Image files cannot be launched as programs.")
            return False

        if app.endswith("!App") or "!" in app:
            if args:
                os.startfile(args) 
            else:
                subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app}"])
            return True

        cmd = [keyword]
        if args:
            cmd.append(args)
        
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        return True

    except Exception as e:
        print(f"Error launching {keyword}: {e}")
        return False

def message_checklist(application):
    protocols = get_protocol('message-checklist')
    mockup = {'application': 'whatsapp','receiver': 'anthony (jij)','message': '(automated message)'}
    message_data = mockup
    # message_data = {}
    accepted_confirmations = ['Yes', 'Yeah', 'Correct', 'That\'s right', 'Affirmative', 'Yep']

    give_audio_response('Running checklist...')

    for key, value in protocols.items():
        if 'voice_message_empty' in value:
            give_audio_response(value['voice_message_empty'])
            message_data[key] = listen_and_recognize() or 'Yes'

            # message_data[key] = mockup[key]
            
            give_audio_response(message_data[key])
            time.sleep(0.5)

    for key, value in protocols.items():
        if 'voice_message' in value:
            value['voice_message'] = value['voice_message'].replace(f'[{key}]', message_data[key])
            give_audio_response(value['voice_message'])

            user_answer = listen_and_recognize()
            
            if user_answer not in accepted_confirmations:
                give_audio_response(f'What would you like {message_data[key]} to be?')
                message_data[key] = listen_and_recognize()

                print(message_data[key])
                give_audio_response('Noted.')

            time.sleep(0.5)

    give_audio_response('Sending message . . .')

    open_program(message_data['application'])

    application_mapping = {
        "whatsapp": send_whatsapp,
        "discord": send_discord,
    }

    application_mapping[message_data['application'].lower()](message_data['receiver'], message_data['message'])

def search_web(query="", url=""):
    time.sleep(2)
    if "Firefox" not in (i.name() for i in psutil.process_iter()):
        return

    if url is not None:
        pyautogui.write(url)
        pyautogui.press('enter')
        return

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    open_program(search_url)