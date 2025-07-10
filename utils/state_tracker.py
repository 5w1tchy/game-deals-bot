import json
import os

STATE_FILE = "data/last_posted.json"  # ensure this points to correct folder


def read_last_post():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}  # empty file
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {}  # corrupted file or read error
    return {}


def write_last_post(month, year):
    with open(STATE_FILE, "w") as f:
        json.dump({"month": month, "year": year}, f, indent=2)
