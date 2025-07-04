from datetime import date
import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from main import app
from intent_logic.intent_matcher import process_keywords, detect_intent
from utils.utils import get_mapped_item_name

client = TestClient(app)


def test_get_today_date():
    today = date.today().strftime('%d-%m-%Y')
    response = client.get("/orders/get_today_date")
    assert response.status_code == 200
    assert response.json() == {"today": today}


def test_detect_intent_endpoint():
    payload = {"sender": "user", "text": "אני רוצה להזמין", "language": "he"}
    response = client.post("/intent/detect_intent", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "success", "intent": "create_order"}


def test_translate_item_name():
    assert get_mapped_item_name("מלפפון") == "מלפ"


def test_process_keywords():
    keywords = process_keywords("אני רוצה להזמין מלפפון", "he")
    assert keywords == ["רוצה", "להזמין", "מלפפון"]


def test_detect_intent_function():
    intent = detect_intent("אני רוצה להזמין", "he")
    assert intent == "create_order"
