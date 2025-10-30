import os
import re
import json
import getpass
global user

user = getpass.getuser()

def get_app_by_keyword(keyword):
    path = "data/openedPrograms.txt"
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        for line in file:
            if line.lower().startswith(f"{keyword.lower()}:"):
                match = re.match(rf"{keyword}\s?:\s?(.*)", line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
    return None

def save_app_by_keyword(keyword, exePath):
    path = "data/openedPrograms.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    if os.path.exists(path):
        with open(path, "r") as file:
            lines = file.readlines()
    if not any(line.lower().startswith(f"{keyword.lower()}:") for line in lines):
        with open(path, "a") as file:
            file.write(f"{keyword}: {exePath}\n")

def save_user_data(type_key, value):
    path = '../data/user-data.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        with open(path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
        
    data[type_key] = value
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

def scrape(default_browser):
    # TODO: Scrape files for browsing history
    print('asd')

def main():
    save_user_data('Browser', 'Google chrome')

if __name__=="__main__":
    main()