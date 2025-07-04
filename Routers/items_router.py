import json
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import DB.redis_chat_memory
from DB import items_data_access as data_access, redis_chat_memory
from utils.models import OrderRequest

router = APIRouter()

@router.get("/get_all_items")
async def get_all_items():
    all_items = data_access.get_all_items()
    if len(all_items) == 0:
        raise HTTPException(status_code=404, detail={ "error": "Error fetching items" })
    return all_items


@router.get("/get_item_info_by_id/{item_id}")
async def get_item_info_by_id(item_id: int):
    item_info = data_access.get_item_info_by_id(item_id)
    if item_info:
        return item_info
    else:
        raise HTTPException(status_code=404, detail={ "error": "Error fetching item" })


@router.get("/get_item_links_by_id/{item_id}")
async def get_links_by_item_id(item_id: int):
    links = data_access.get_links_by_item_id(item_id)
    if len(links) == 0:
        raise HTTPException(status_code=404, detail={ "error": "No links found" })
    return links


@router.post("/suggest_linked_items")
async def suggest_linked_items(request: Request):
    """Get suggested linked items for the provided items."""
    mapped_items = await _map_and_validate_items(request)
    item_ids = [i["item_id"] for i in mapped_items]
    suggestions = data_access.get_missing_linked_items_with_context(item_ids)
    return { "suggested_items": suggestions }


@router.get("/get_item_links_by_name/{item_name}")
async def get_links_by_item_name(item_name: str):
    item_id = (data_access.map_item_names_to_ids([{ "item_name": item_name, "quantity": 0 }]))[0]["item_id"]
    links = data_access.get_links_by_item_id(item_id)
    if len(links) == 0:
        raise HTTPException(status_code=404, detail={ "error": "No links found" })
    return links


@router.post("/map_item_names_to_ids")
async def map_item_names_to_ids(request: Request):
    """Map item names to their corresponding IDs and prepare order data."""
    data = await request.json()
    mapped_items = await _map_and_validate_items(request)
    
    mapped_order = {
        "customer_id": data["customer_id"],
        "customer_telephone": data["customer_telephone"],
        "items": mapped_items,
        "flag": any(item["item_id"] is None for item in mapped_items)        # flag = True -> there are unmatched items
    }

    # Store non-null items (commented out as per original code)
    for item in mapped_order["items"]:
        if item["item_id"] is not None:
            await DB.redis_chat_memory.store_order_items(data["customer_telephone"], item)
    
    return { "mapped_order": mapped_order }


async def _map_and_validate_items(request: Request):
    """Helper function to map item names to IDs and validate the request."""
    data = await request.json()
    items = data.get("items", [])

    if isinstance(items, str):
        try:
            items = json.loads(items)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in 'items' field")

    try:
        return data_access.map_item_names_to_ids(items)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

