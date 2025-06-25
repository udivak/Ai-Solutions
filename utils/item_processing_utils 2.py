import re
import unicodedata
from rapidfuzz import process, fuzz


def normalize_hebrew(text: str) -> str:
    # Normalize Unicode
    text = unicodedata.normalize('NFKC', text)
    # Remove nikkud (diacritics)
    text = re.sub(r'[\u0591-\u05C7]', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase (in case of mixed language)
    return text.lower().strip()


def find_best_match(user_input: str, items_dict: dict, score_threshold: float = 75):
    normalized_input = normalize_hebrew(user_input)
    choices = list(items_dict.keys())

    match, score, _ = process.extractOne(normalized_input, choices, scorer=fuzz.WRatio)

    if score >= score_threshold:
        return items_dict[match], score
    else:
        return None, score


