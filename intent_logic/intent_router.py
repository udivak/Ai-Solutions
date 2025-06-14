from fastapi import APIRouter, Request
from pydantic import BaseModel
from . import intent_matcher
import logging
from models import MessageRequest


router = APIRouter()

@router.post("/detect_intent")
async def detect_intent(message: MessageRequest):
    print(message.text)
    try:
        intent = intent_matcher.detect_intent(message.text)
        if intent:
            return {"success": True, "intent": intent}
        else:
            return {"success": False, "intent": None}
    except Exception as e:
        logging.exception("Failed to detect intent")
        return {"success": False, "error": str(e)}
