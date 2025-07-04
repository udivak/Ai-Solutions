import re
import unicodedata
from rapidfuzz import process, fuzz
import json
from pathlib import Path


# Get the absolute path to the JSON file relative to this Python file
MAP_PATH = Path(__file__).resolve().parent / "item_name_map.json"

with open(MAP_PATH, "r", encoding="utf-8") as f:
    ITEM_NAME_MAP = json.load(f)

def get_mapped_item_name(item_name: str) -> str | None:
    return ITEM_NAME_MAP.get(item_name)


def normalize_hebrew(text: str) -> str:
    # Normalize Unicode
    text = unicodedata.normalize('NFKC', text)
    # Remove nikkud (diacritics)
    text = re.sub(r'[\u0591-\u05C7]', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase (in case of mixed language)
    return text.lower().strip()


def find_best_match(user_input: str, choices: list, score_threshold: float = 75):
    normalized_input = normalize_hebrew(user_input)
    #choices = list(items_dict.keys())

    match, score, _ = process.extractOne(normalized_input, choices, scorer=fuzz.WRatio)     #type: ignore

    if score >= score_threshold:
        return match, score
    else:
        return None, score


