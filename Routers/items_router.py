from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from utils import utils
from DB import data_access
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


@router.get("/get_item_links/{item_id}")
async def get_links_by_item_id(item_id: int):
    links = data_access.get_links_by_item_id(item_id)
    if len(links) == 0:
        raise HTTPException(status_code=404, detail={ "error": "No links found" })
    return links


# @router.post("/map_item_names_to_ids")
# async def match_names_to_ids(order_request: OrderRequest):
#     items = [dict(item) for item in order_request.items]
#     mapped_items = data_access.map_item_names_to_ids(items)



















