import os
import re
import json

def get_protocol(name):
    path = f"data/protocols/{name}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding='UTF-8') as file:
        data = json.load(file)
        return data
    return None