from fastapi import APIRouter, Request
from DB import redis_chat_memory
from utils.models import *

router = APIRouter()

@router.get("/get_chat_memory/{customer_telephone}")
async def get_memory(customer_telephone: str):
    return await redis_chat_memory.get_order_context(customer_telephone)


# @router.post("/append_message/{customer_telephone}")
# async def append_message(customer_telephone: str, message_request: MessageRequest):
#     new_message = { "sender": message_request.sender, "message": message_request.text }
#     current = await redis_chat_memory.get_order_context(customer_telephone)
#     messages = current.get("chat_history", [])
#     messages.append(new_message)
#     await redis_chat_memory.update_order_context(customer_telephone, {"chat_history": messages})
#     return ({ "status": "chat history updated" }


@router.post("/append_message/{customer_telephone}")
async def append_message(customer_telephone: str, message_request: MessageRequest):
    await redis_chat_memory.append_chat(customer_telephone, message_request.sender, message_request.text)
    return { "status": "message append successfully"}


@router.post("/append_items/{customer_telephone}")
async def append_items(customer_telephone: str, request: Request):
    data = await request.json()
    items = data.get('items', [])
    await redis_chat_memory.append_order_items(customer_telephone, items)
    return { "status": "item added successfully" }


@router.delete("/clear_memory/{customer_telephone}")
async def clear_memory(customer_telephone: str):
    await redis_chat_memory.clear_order_context(customer_telephone)
    return { "status": "chat history cleared" }
