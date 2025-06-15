import redis.asyncio as redis
import json

# Configure Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def get_order_context(customer_telephone: str) -> dict:
    data = await r.get(f"order:{customer_telephone}")
    return json.loads(data) if data else {}


async def update_order_context(customer_telephone: str, new_data: dict):
    current = await get_order_context(customer_telephone)
    current.update(new_data)
    await r.set(f"order:{customer_telephone}", json.dumps(current), ex=3600)            # ex -> expire in 1 hour


async def clear_order_context(customer_telephone: str):
    await r.delete(f"order:{customer_telephone}")
