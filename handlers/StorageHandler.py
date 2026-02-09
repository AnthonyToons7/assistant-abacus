import os
import re
import json
import getpass
import datetime
global user

user = getpass.getuser()
opened_programs_path = '../data/openedPrograms.txt'
user_data_path = 'data/user-data.json'
web_search_data_path = 'data/web_searches/'

def get_app_by_keyword(keyword):
    if not os.path.exists(opened_programs_path):
        return None
    with open(opened_programs_path, "r") as file:
        for line in file:
            if line.lower().startswith(f"{keyword.lower()}:"):
                match = re.match(rf"{keyword}\s?:\s?(.*)", line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
    return None

def save_app_by_keyword(keyword, exePath):
    os.makedirs(os.path.dirname(opened_programs_path), exist_ok=True)
    lines = []
    if os.path.exists(opened_programs_path):
        with open(opened_programs_path, "r") as file:
            lines = file.readlines()
    if not any(line.lower().startswith(f"{keyword.lower()}:") for line in lines):
        with open(opened_programs_path, "a") as file:
            file.write(f"{keyword}: {exePath}\n")

def save_user_data(type_key, value):
    os.makedirs(os.path.dirname(user_data_path), exist_ok=True)

    if os.path.exists(user_data_path):
        with open(user_data_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
        
    data[type_key] = value
    with open(user_data_path, "w") as file:
        json.dump(data, file, indent=4)

def save_web_search(data):
    os.makedirs(os.path.dirname(web_search_data_path), exist_ok=True)
    
    today_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(web_search_data_path, today_folder)
    os.makedirs(folder_path, exist_ok=True)

    file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def get_user_data(keyword):
    with open(user_data_path, 'r') as file:
        data = json.load(file)
        return data[keyword]

def scrape(default_browser):
    default_browser_directory = get_app_by_keyword(default_browser)

    if(default_browser_directory is None):
        print('Chat, we don\'t have a browser')

    

def main():
    save_user_data('Browser', 'Google chrome')

if __name__=="__main__":
    main()