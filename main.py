import json
from http.client import HTTPException

import db_connection
import crud
import tables
from fastapi import FastAPI
import mysql.connector
from utils import utils
from models import *

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/get_orders/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    return crud.get_orders_by_customer_id(customer_id)


@app.get("/get_all_items")
async def get_all_items():
    return crud.get_all_items()


@app.get("/get_item_info_by_id/{item_id}")
async def get_item_info_by_id(item_id: int):
    return crud.get_item_info_by_id(item_id)


@app.get("/get_item_info_by_name/{hebrew_item_name}")
async def get_item_info_by_name(hebrew_item_name: str):
    english_name = utils.translate_item_name(hebrew_item_name)
    if english_name:
        items = crud.get_items_by_name(english_name)
        return items
    else:
        return {"error": "Item name not found"}


@app.post("/create_order")
async def create_order(order_request: OrderRequest):
    new_order_id = crud.insert_order_items(order_request)
    upsell_items = crud.find_upsells(order_request, new_order_id)
    print(upsell_items)
    return {"message": "Order created successfully"}


@app.get("/upsell_test")
async def upsell_test():
    test_order = OrderRequest(customer_id=1, items=[OrderItem(item_id=1, quantity=2)])
    print(crud.find_upsells(test_order, 9))
    return {"test": "test"}


@app.get("/get_item_links/{item_id}")
async def get_links_by_item_id(item_id: int):
    return crud.get_links_by_item_id(item_id)


@app.get("/get_customer_info/{customer_telephone}", response_model=Customer)
async def get_customer_info(customer_telephone: str):
    customer = crud.get_customer_info(customer_telephone)
    print(customer)
    print(type(customer))
    if not customer:
        raise HTTPException(status_code= 404, detail= "Customer not found")             # type: ignore
    return Customer(**dict(customer))






