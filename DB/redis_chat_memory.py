import redis.asyncio as redis
import json
from datetime import datetime

# Configure Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, password="Ai1615Solutions", decode_responses=True)

### === SESSION METADATA === ###

async def get_session_metadata(customer_telephone: str) -> dict:
    key = f"chat_session:{customer_telephone}"
    metadata = await r.hgetall(key)
    return metadata or {}


async def update_session_metadata(customer_telephone: str, updates: dict):
    key = f"chat_session:{customer_telephone}"
    await r.hset(key, mapping=updates)


async def set_order_flag(customer_telephone: str, value: bool):
    await update_session_metadata(customer_telephone, { "is_creating_order": str(value).lower() })


async def get_order_flag(customer_telephone: str) -> bool:
    metadata = await get_session_metadata(customer_telephone)
    return metadata.get("is_creating_order", "false") == "true"


### === CHAT HISTORY === ###

def get_today_key(customer_telephone: str) -> str:
    today = datetime.today().strftime("%d-%m-%Y")
    return f"chat:{customer_telephone}:{today}"


async def append_chat_message(customer_telephone: str, sender: str, message: str):
    key = get_today_key(customer_telephone)
    entry = {
        "sender": sender,
        "text": message
    }
    await r.rpush(key, json.dumps(entry))
    await r.expire(key, 3600)


async def get_chat_history(customer_telephone: str) -> list:
    key = get_today_key(customer_telephone)
    raw_messages = await r.lrange(key, 0, -1)
    return [json.loads(m) for m in raw_messages]


### === ORDER ITEM STORAGE (if needed) ===

async def store_order_items(customer_telephone: str, items_to_add: list[dict] | dict):
    """Persist order items in redis as a hash of ``item_name`` -> ``quantity``."""
    key = f"order:{customer_telephone}"

    if isinstance(items_to_add, dict):
        items_to_add = [items_to_add]

    mapping = {item["item_name"]: item["quantity"] for item in items_to_add}
    if mapping:
        await r.hset(key, mapping=mapping)
        await r.expire(key, 3600)


async def get_order_items(customer_telephone: str) -> dict:
    """Return stored order items as a mapping of item names to quantities."""
    key = f"order:{customer_telephone}"
    raw = await r.hgetall(key)
    return {name: int(qty) for name, qty in raw.items()}



async def clear_order_memory(customer_telephone: str):
    await r.delete(f"order:{customer_telephone}")


### === UPSELL ITEM STORAGE (if needed) ===

async def store_upsell_items(customer_telephone: str, upsell_items: list[dict]):
    key = f"upsell_items:{customer_telephone}"
    await r.set(key, json.dumps(upsell_items), ex=3600)


### === GENERAL ACTIONS ===

async def clear_order_context(customer_telephone: str):
    key = get_today_key(customer_telephone)
    await r.delete(key)
    await r.delete(f"order:{customer_telephone}")
    await r.delete(f"upsell_items:{customer_telephone}")
