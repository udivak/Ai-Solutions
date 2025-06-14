import os
import json
import re
from typing import Dict, List, Tuple, Optional


def load_intent_keywords() -> Dict[str, Dict[str, List[str]]]:
    """
    Load intent keyword patterns from a JSON file.
    Returns:
        Dictionary mapping intent names to language-specific keyword lists.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, 'intent_keywords.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"ERROR loading intent keywords: {e}")
        return {}


def process_keywords(text: str, language: str = "en") -> List[str]:
    """
    Extract keywords from text by removing stop words.

    Args:
        text: Input user message
        language: Language code ('en' or 'he')

    Returns:
        Cleaned list of keywords
    """
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {
        "en": {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'with', 'my', 'can', 'i', 'do', 'how', 'where'},
        "he": {'אני', 'את', 'אתה', 'הוא', 'היא', 'הם', 'הן', 'אנחנו', 'אתם', 'אתן', 'של', 'שלי', 'שלך', 'שלו', 'שלה', 'שלנו', 'שלכם', 'שלכן', 'שלהם', 'שלהן', 'עם', 'על', 'אל', 'מן', 'כי', 'אם', 'או', 'אז', 'כן', 'לא', 'גם', 'רק', 'כמו', 'אבל', 'איך', 'מה'}
    }

    language_stop_words = stop_words.get(language, stop_words["he"])
    keywords = [word for word in words if word not in language_stop_words]

    if language == "he":
        keywords = [word[1:] if word.startswith('ה') else word for word in keywords]

    return keywords


def calculate_match_score(query: str, pattern: str, language: str = "en") -> Tuple[float, str]:
    """
    Calculate how well a query matches a known intent pattern.

    Args:
        query: User message
        pattern: Pattern from intent definitions
        language: Language code ('en' or 'he')

    Returns:
        (score, match_type)
    """
    query_lower = query.lower()
    pattern_lower = pattern.lower()

    if query_lower == pattern_lower:
        return 1.0, "exact"
    if pattern_lower in query_lower:
        return 0.9 * (len(pattern_lower) / len(query_lower)), "pattern_in_query"
    if query_lower in pattern_lower:
        return 0.8 * (len(query_lower) / len(pattern_lower)), "query_in_pattern"

    query_keywords = process_keywords(query_lower, language)
    pattern_keywords = process_keywords(pattern_lower, language)

    if not query_keywords or not pattern_keywords:
        return 0.0, "no_keywords"

    if language == "he":
        matches = 0
        for qk in query_keywords:
            for pk in pattern_keywords:
                if qk in pk or pk in qk:
                    matches += 1
                    break
    else:
        matches = sum(1 for kw in query_keywords if any(kw in pkw or pkw in kw for pkw in pattern_keywords))

    if matches > 0:
        multiplier = 0.8 if language == "en" else 0.7
        score = multiplier * (matches / max(len(query_keywords), len(pattern_keywords)))
        return score, "keyword"

    return 0.0, "no_match"


def detect_intent(message: str, language: str = "he") -> Optional[str]:
    """
    Determine user intent based on keyword match scoring.

    Args:
        message: Raw user message
        language: Language code ('en' or 'he')

    Returns:
        Intent name string if matched above threshold, else None
    """
    message = message.lower().strip()
    best_intent = None
    highest_score = 0.0

    for intent, patterns in INTENT_KEYWORDS.items():
        for pattern in patterns.get(language, []):
            score, _ = calculate_match_score(message, pattern, language)
            if score > highest_score:
                best_intent = intent
                highest_score = score
    print("best intent ->>>>>>", best_intent)
    threshold = 0.25 if language == "en" else 0.2
    return best_intent if highest_score >= threshold else None


# Load once globally
INTENT_KEYWORDS = load_intent_keywords()
