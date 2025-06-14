from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from intent_logic import intent_matcher
from models import MessageRequest

router = APIRouter()

@router.post("/detect_intent")
async def detect_intent(message: MessageRequest):
    try:
        intent = intent_matcher.detect_intent(message.text)
        if intent:
            return { "message": "success", "intent": intent }
        else:
            raise HTTPException(status_code=404, detail={ "error": "No intent found", "intent": None })
    except Exception as e:
        raise HTTPException(status_code=404, detail={ "message": "error", "Exception occurred in detect_intent": None,
                                                      "exception": str(e) })

