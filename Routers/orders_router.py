from fastapi import APIRouter, HTTPException
from models import OrderRequest, OrderItem
import data_access

router = APIRouter()

@router.get("/get_orders/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    orders = data_access.get_orders_by_customer_id(customer_id)
    if len(orders) == 0:
        raise HTTPException(status_code=404, detail={ "error": "Orders not found", "customer_id": customer_id })
    return orders


@router.post("/create_order")
async def create_order(order_request: OrderRequest):
    new_order_id = data_access.insert_order_items(order_request)
    upsell_items = data_access.find_upsells(order_request, new_order_id)
    return { "message": "Order created successfully", "upsell_items": upsell_items }


# upsell test endpoint
@router.get("/upsell_test")
async def upsell_test():
    test_order = OrderRequest(customer_id=1, items=[OrderItem(item_id=1, quantity=2)])
    print(data_access.find_upsells(test_order, 9))
    return {"test": "test"}