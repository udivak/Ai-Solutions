from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import json
from Routers import items_router
from utils.models import OrderRequest, OrderItem, OrderIDs, OrderRequestRaw
from DB import data_access

router = APIRouter()

@router.get("/get_orders/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    orders = data_access.get_orders_by_customer_id(customer_id)
    if len(orders) == 0:
        raise HTTPException(status_code=404, detail={ "error": "Orders not found", "customer_id": customer_id })
    return orders


# @router.post("/create_order")
# async def create_order(order_request: OrderRequest):
#     new_order_id = data_access.insert_order_items(order_request)
#     upsell_items = data_access.find_upsells(order_request, new_order_id)
#     return { "message": "Order created successfully", "upsell_items": upsell_items }


@router.post("/create_order")
async def create_order(request: Request):
    data = await request.json()
    print("======in create order=======\n", data)

    # Handle case where items come as JSON string
    if isinstance(data.get("items"), str):
        try:
            data["items"] = json.loads(data["items"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in 'items' field")

    try:
        mapped_items = data_access.map_item_names_to_ids(data["items"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    final_order = {
        "customer_id": data["customer_id"],
        "customer_telephone": data["customer_telephone"],
        "items": mapped_items
    }

    order_request = OrderRequest(**final_order)
    print("========= SUCCESSFULLY PARSED TO ORDEREQUEST ==========\n")
    new_order_id = data_access.insert_order_items(order_request)
    upsell_items = data_access.find_upsells(order_request, new_order_id)

    return {"message": "Order created successfully", "upsell_items": upsell_items}



# @router.post("/create_order")
# async def create_order(order_request: OrderRequestRaw):
#     try:
#         mapped_items = await map_item_names_to_ids(
#             [dict(item) for item in order_request.items]
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#
#     final_order = {
#         "customer_id": order_request.customer_id,
#         "customer_telephone": order_request.customer_telephone,
#         "items": mapped_items
#     }
#     order_model = OrderRequest(**final_order)
#     new_order_id = data_access.insert_order_items(order_model)
#     upsell_items = data_access.find_upsells(order_model, new_order_id)
#     return { "message": "Order created successfully", "upsell_items": upsell_items }
# @router.post("/create_order")
# async def create_order(order_request: Request):
#     data = await order_request.json()
#     print("======in create order=======\n", data)
#     # final_order = {
#     #     "customer_id": data.customer_id,
#     #     "customer_telephone": data.customer_telephone,
#     #     "items": data.items
#     # }
#     order_model = OrderRequest(**data)
#     new_order_id = data_access.insert_order_items(order_model)
#     upsell_items = data_access.find_upsells(order_model, new_order_id)
#     return { "message": "Order created successfully", "upsell_items": upsell_items }

@router.get("/get_order_items_info/{order_id}")
async def get_order_items_info(order_id: int):
    order_items = data_access.get_order_items_info(order_id)
    if len(order_items) == 0:
        raise HTTPException(status_code=404, detail={ "error": "An error has occurred" })
    return order_items


@router.post("/get_multiple_order_items_info")
async def get_multiple_order_items_info(order_ids_data: OrderIDs):
    all_items = []
    for order_id in order_ids_data.order_ids:
        order_items = data_access.get_order_items_info(order_id)
        if order_items:
            all_items.append({
                "order_id": order_id,
                "items": order_items
            })
        else:
            all_items.append({
                "order_id": order_id,
                "items": [],
                "error": "No items found or invalid order ID"
            })
    return all_items


# upsell test endpoint
@router.get("/upsell_test")
async def upsell_test():
    test_order = OrderRequest(customer_id=1, items=[OrderItem(item_id=1, quantity=2)])
    print(data_access.find_upsells(test_order, 9))
    return {"test": "test"}


# async def map_item_names_to_ids(items: list[dict]) -> list[dict]:
#     """
#     Given a list of { item_name, quantity } dicts,
#     returns a list of { item_id, quantity } after lookup.
#     """
#     mapped = []
#     for item in items:
#         name = item["item_name"]
#         quantity = item["quantity"]
#
#         item_info = await items_router.get_item_info_by_eng_name(name)
#         if not item_info:
#             raise ValueError(f"Item '{name}' not found")
#
#         mapped.append({
#             "item_id": item_info[0]["item_id"],
#             "quantity": quantity
#         })
#
#     return mapped