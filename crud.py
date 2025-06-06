from sqlalchemy import insert, select, delete, update, func
from db_connection import engine
from tables import customers, items, orders
from models import *


def insert_order_items(order_request: OrderRequest):
    with engine.begin() as session:
        max_order_id = session.execute(select(func.max(orders.c.Order_id))).scalar()
        new_order_id = max_order_id + 1

        for item in order_request.items:
            query = insert(orders).values(
                Order_id= new_order_id,
                Customer_id=order_request.customer_id,
                Item_id=item.item_id,
                Quantity=item.quantity
            )
            session.execute(query)


def get_orders_by_customer_id(customer_id: int):
    with engine.connect() as session:
        query = select(orders).where(orders.c.Customer_id == customer_id)         # type: ignore
        result = session.execute(query)
        print("-------------------\nresult: ", result.mappings())
        return list(result.mappings())

