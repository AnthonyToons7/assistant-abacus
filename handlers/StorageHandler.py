import os
import re

def get_app_by_keyword(keyword):
    path = "brain/openedPrograms.txt"
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
    path = "brain/openedPrograms.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    if os.path.exists(path):
        with open(path, "r") as file:
            lines = file.readlines()
    if not any(line.lower().startswith(f"{keyword.lower()}:") for line in lines):
        with open(path, "a") as file:
            file.write(f"{keyword}: {exePath}\n")
