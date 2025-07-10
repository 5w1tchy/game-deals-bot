import json
import os

# Paths inside your data folder
DAILY_STATUS_FILE = os.path.join("data", "daily_post_status.json")
WEEKLY_STATUS_FILE = os.path.join("data", "weekly_post_status.json")
POSTED_MESSAGES_FILE = os.path.join("data", "posted_messages.json")
POSTED_GAMES_FILE = os.path.join("data", "posted_games.json")


def _ensure_file(file_path, default_data):
    """
    Ensure the JSON file exists and contains required keys;
    if not, creates or fixes it with default_data.
    """
    if not os.path.exists(file_path):
        write_json(file_path, default_data)
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Make sure all expected keys exist
        for key, value in default_data.items():
            if key not in data:
                data[key] = value
        return data
    except (json.JSONDecodeError, IOError):
        write_json(file_path, default_data)
        return default_data


def read_daily_status():
    # Default with the correct key your bot checks for
    return _ensure_file(DAILY_STATUS_FILE, {"daily_post_date": None})


def write_daily_status(status):
    write_json(DAILY_STATUS_FILE, status)


def read_weekly_status():
    # Default with the correct key your bot checks for
    return _ensure_file(WEEKLY_STATUS_FILE, {"weekly_post_date": None})


def write_weekly_status(status):
    write_json(WEEKLY_STATUS_FILE, status)


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_posted_messages():
    return _ensure_file(POSTED_MESSAGES_FILE, {"messages": []})


def write_posted_messages(messages_data):
    write_json(POSTED_MESSAGES_FILE, messages_data)


def read_posted_games():
    data = _ensure_file(POSTED_GAMES_FILE, {"games": {}})
    if not isinstance(data.get("games"), dict):
        data["games"] = {}  # Fix corrupted data automatically
        write_json(POSTED_GAMES_FILE, data)
    return data


def write_posted_games(games_data):
    write_json(POSTED_GAMES_FILE, games_data)
