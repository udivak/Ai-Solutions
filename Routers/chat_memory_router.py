from fastapi import APIRouter, Request
from DB import redis_chat_memory
from utils.models import *

router = APIRouter()

@router.get("/get_key/{customer_telephone}")
async def get_key(customer_telephone: str):
    key = redis_chat_memory.get_today_key(customer_telephone)
    return { "key": key }


@router.get("/get_chat_memory/{customer_telephone}")
async def get_chat_memory(customer_telephone: str):
    messages = await redis_chat_memory.get_chat_history(customer_telephone)
    order = await redis_chat_memory.get_order_items(customer_telephone)
    return {
        "messages": messages,
        "order": order
    }


@router.post("/append_message/{customer_telephone}")
async def append_message(customer_telephone: str, request: Request):
    message_request = await request.json()
    sender = message_request.get('sender', '')
    text = message_request.get('text', '')
    await redis_chat_memory.append_chat_message(customer_telephone, sender, text)
    return { "status": "message append successfully"}


@router.post("/append_items/{customer_telephone}")
async def append_items(customer_telephone: str, request: Request):
    data = await request.json()
    items = data.get('items', [])
    await redis_chat_memory.store_order_items(customer_telephone, items)
    return { "status": "order updated successfully" }


@router.post("/set_order_flag/{customer_telephone}")
async def set_order_flag(customer_telephone: str, request: Request):
    data = await request.json()
    flag = data.get("is_creating_order", False)
    await redis_chat_memory.set_order_flag(customer_telephone, flag)
    return { "status": f"order flag set to {flag}" }


@router.get("/get_order_flag/{customer_telephone}")
async def get_order_flag(customer_telephone: str):
    flag = await redis_chat_memory.get_order_flag(customer_telephone)
    return { "is_creating_order": flag }


@router.delete("/clear_memory/{customer_telephone}")
async def clear_memory(customer_telephone: str):
    await redis_chat_memory.clear_order_context(customer_telephone)
    return { "status": "chat memory and order cleared" }
