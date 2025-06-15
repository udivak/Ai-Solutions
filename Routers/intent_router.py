from fastapi import APIRouter, HTTPException
from DB import data_access
from intent_logic import intent_matcher
from utils.models import MessageRequest, Other

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


@router.post("/other")
async def other(other: Other):
    return data_access.get_query_result(other.query)

