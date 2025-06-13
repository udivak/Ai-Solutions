import json
from pathlib import Path

# Get the absolute path to the JSON file relative to this Python file
MAP_PATH = Path(__file__).resolve().parent / "item_name_map.json"

with open(MAP_PATH, "r", encoding="utf-8") as f:
    ITEM_NAME_MAP = json.load(f)

def translate_item_name(hebrew_name: str) -> str | None:
    return ITEM_NAME_MAP.get(hebrew_name)
