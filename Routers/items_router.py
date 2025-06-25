import json

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

import DB.redis_chat_memory
from utils import utils
from DB import data_access, redis_chat_memory
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


@router.get("/get_item_info_by_he_name/{hebrew_item_name}")
async def get_item_info_by_he_name(hebrew_item_name: str):
    english_name = utils.translate_item_name(hebrew_item_name)
    if english_name:
        items = data_access.get_items_by_name(english_name)
        return items
    else:
        raise (HTTPException(status_code=404, detail={ "error": "Error fetching item" }))


@router.get("/get_item_info_by_name/{eng_item_name}")
async def get_item_info_by_eng_name(eng_item_name: str):
    items = data_access.get_items_by_name(eng_item_name)
    if not items:
        raise HTTPException(status_code=404, detail={ "error": "Error fetching item" })
    return items


@router.get("/get_item_links_by_id/{item_id}")
async def get_links_by_item_id(item_id: int):
    links = data_access.get_links_by_item_id(item_id)
    if len(links) == 0:
        raise HTTPException(status_code=404, detail={ "error": "No links found" })
    return links


@router.post("/suggest_linked_items")
async def suggest_linked_items(request: Request):
    data = await request.json()
    items = data.get("items", [])
    item_ids = [i["item_id"] for i in data_access.map_item_names_to_ids(items)]
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
    data = await request.json()
    items = data.get("items", [])
    if isinstance(data.get("items"), str):
        try:
            data["items"] = json.loads(data["items"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in 'items' field")

    try:
        mapped_items = data_access.map_item_names_to_ids(data["items"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    mapped_order = {
        "customer_id": data["customer_id"],
        "customer_telephone": data["customer_telephone"],
        "items": mapped_items
    }

    flag = False
    for item in mapped_order["items"]:
        if item["item_id"] is None:
            flag = True
        # else:
        #     await DB.redis_chat_memory.store_order_items(data.get("customer_telephone"), item)

    mapped_order["flag"] = flag

    return { "mapped_order": mapped_order }







# @router.post("/map_item_names_to_ids")
# async def match_names_to_ids(order_request: OrderRequest):
#     items = [dict(item) for item in order_request.items]
#     mapped_items = data_access.map_item_names_to_ids(items)



















