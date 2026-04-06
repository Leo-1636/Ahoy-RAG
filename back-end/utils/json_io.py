import json
from pathlib import Path

def open_json(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, "r", encoding = "utf-8") as file:
        return json.load(file)

def save_json(path: Path, json_list: list[dict]):
    with open(path, "w", encoding = "utf-8") as file:
        json.dump(json_list, file, indent = 4, ensure_ascii = False)