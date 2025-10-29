import os
import re
import json

def get_protocol(name):
    path = "data/protocols/{name}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        data = json.loads(file)
        return data
    return None