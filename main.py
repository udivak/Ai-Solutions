from fastapi import FastAPI
from Routers import orders_router, items_router, customers_router, intent_router, chat_memory_router

app = FastAPI()

app.include_router(intent_router.router, prefix="/intent", tags=["Intent Routing"])
app.include_router(orders_router.router, prefix="/orders", tags=["Orders Routing"])
app.include_router(items_router.router, prefix="/items", tags=["Items Routing"])
app.include_router(customers_router.router, prefix="/customers", tags=["Customers Routing"])
app.include_router(chat_memory_router.router, prefix="/chat_memory", tags=["Redis Chat Memory"])

@app.get("/")
async def root():
    return { "message": "Welcome to Ai Direct" }




# from http.client import HTTPException
# from Routers.intent_router import router
# import data_access
# from fastapi import FastAPI
# from utils import utils
# from models import *
#
# app = FastAPI()
# app.include_router(router)
#
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/get_orders/{customer_id}")
# async def get_orders_by_customer_id(customer_id: int):
#     # return data_access.get_orders_by_customer_id(customer_id)
#     orders = data_access.get_orders_by_customer_id(customer_id)
#     if orders:
#         return orders
#     else:
#         return { "error": "no orders found" }
#
# @app.get("/get_all_items")
# async def get_all_items():
#     return data_access.get_all_items()
#
#
# @app.get("/get_item_info_by_id/{item_id}")
# async def get_item_info_by_id(item_id: int):
#     return data_access.get_item_info_by_id(item_id)
#
#
# @app.get("/get_item_info_by_name/{hebrew_item_name}")
# async def get_item_info_by_name(hebrew_item_name: str):
#     english_name = utils.translate_item_name(hebrew_item_name)
#     if english_name:
#         items = data_access.get_items_by_name(english_name)
#         return items
#     else:
#         return {"error": "Item name not found"}
#
#
# @app.post("/create_order")
# async def create_order(order_request: OrderRequest):
#     new_order_id = data_access.insert_order_items(order_request)
#     upsell_items = data_access.find_upsells(order_request, new_order_id)
#     print(upsell_items)
#     return {"message": "Order created successfully"}
#
#
# @app.get("/upsell_test")
# async def upsell_test():
#     test_order = OrderRequest(customer_id=1, items=[OrderItem(item_id=1, quantity=2)])
#     print(data_access.find_upsells(test_order, 9))
#     return {"test": "test"}
#
#
# @app.get("/get_item_links/{item_id}")
# async def get_links_by_item_id(item_id: int):
#     return data_access.get_links_by_item_id(item_id)
#
#
# @app.get("/get_customer_info/{customer_telephone}", response_model=Customer)
# async def get_customer_info(customer_telephone: str):
#     customer = data_access.get_customer_info(customer_telephone)
#     print(customer)
#     print(type(customer))
#     if not customer:
#         raise HTTPException(status_code= 404, detail= "Customer not found")             # type: ignore
#     return Customer(**dict(customer))
#
#
#
#
#
#
