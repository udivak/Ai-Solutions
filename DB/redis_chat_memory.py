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


async def append_chat(customer_telephone: str, sender: str, message: str):
    context = await get_order_context(customer_telephone)
    chat = context.get("chat_history", [])
    chat.append({"sender": sender, "message": message})
    await update_order_context(customer_telephone, { "chat_history": chat })


async def append_order_items(customer_telephone: str, items: list[dict]):
    context = await get_order_context(customer_telephone)
    order = context.get("order", [])

    # Convert existing order to a dict for quick lookup
    order_dict = {item["item_name"]: item["quantity"] for item in order}

    # Update or add new items
    for item in items:
        name = item["item_name"]
        qty = item["quantity"]

        # Replace or sum quantities based on your logic
        order_dict[name] = order_dict.get(name, 0) + qty
        # OR: order_dict[name] = order_dict.get(name, 0) + qty  # to sum

    # Reconstruct order list
    new_order = [{"item_name": k, "quantity": v} for k, v in order_dict.items()]
    await update_order_context(customer_telephone, { "order": new_order })



async def clear_order_context(customer_telephone: str):
    await r.delete(f"order:{customer_telephone}")
