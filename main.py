import json
import db_connection
import crud
import tables
from fastapi import FastAPI
import mysql.connector

from models import *

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/get_orders/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    return crud.get_orders_by_customer_id(customer_id)


@app.get("/get_item_info/{item_id}")
async def get_item_info(item_id: int):
    return crud.get_item_info(item_id)


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





