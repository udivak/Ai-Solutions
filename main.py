import json
import db_connection
import crud
import tables
from fastapi import FastAPI
import mysql.connector

from models import OrderRequest

app = FastAPI()

# async def connect_db():
#     db = mysql.connector.connect(
#         host="127.0.0.1",
#         user="root",
#         password="160199",
#         database="Ai Direct"
#     )
#     return db
#
# async def get_cursor():
#     db = await connect_db()
#     return db.cursor()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/get_orders/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    # db = mysql.connector.connect(
    #     host="127.0.0.1",
    #     user="root",
    #     password="160199",
    #     database="Ai Direct"
    # )
    # db = await connect_db()
    # cursor = db.cursor()
    # cursor.execute("SELECT * FROM Orders WHERE customer_id = %s", (customer_id,))
    # result = cursor.fetchall()
    # db.close()
    return crud.get_orders_by_customer_id(customer_id)


@app.post("/create_order")
async def create_order(order_request: OrderRequest):
    # db = await connect_db()
    # cursor = db.cursor()
    # for item in order_request.items:
    #     cursor.execute("INSERT INTO O")
    crud.insert_order_items(order_request)
    return {"message": "Order created successfully"}

