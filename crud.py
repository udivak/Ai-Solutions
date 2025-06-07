from sqlalchemy import insert, select, delete, update, func, and_
from db_connection import engine
from tables import customers, items, orders
from models import *
from datetime import datetime, timedelta


def insert_order_items(order_request: OrderRequest) -> int:
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
    return new_order_id


def get_orders_by_customer_id(customer_id: int):
    with engine.begin() as session:
        query = select(orders).where(orders.c.Customer_id == customer_id)         # type: ignore
        result = session.execute(query)
    return list(result.mappings())


def find_upsells(current_order: OrderRequest, new_order_id: int):
    """
    Find items that current order have less quantity than the average quantity of the customer's previous orders.

    Args:
        current_order (OrderRequest): The order to compare with.
        new_order_id (int): The id of the new order, to exclude it from the calculation.

    Returns:
        list[dict]: A list of dictionaries, each dictionary has a single key-value pair,
            where the key is the item_id and the value is the quantity difference.
    """
    three_months_ago = datetime.now() - timedelta(days=90)
    with engine.begin() as session:
        query = select(orders.c.Item_id, func.avg(orders.c.Quantity).label("avg_quantity")
                       ).where(and_(orders.c.Customer_id == current_order.customer_id,
                                    orders.c.Order_id != new_order_id,
                                    orders.c.Created_at >= three_months_ago
                                    )
                               ).group_by(orders.c.Item_id)
        result = session.execute(query)
        result_rows = list(result)

        deltas = []
        avg_quantity_map = { row[0]: float(row[1]) for row in result_rows }

        for item in current_order.items:
            item_id = item.item_id
            current_qty = item.quantity
            if item_id in avg_quantity_map.keys():
                avg_qty = round(avg_quantity_map[item_id])
                if current_qty < avg_qty:
                    delta = avg_qty - current_qty
                    deltas.append({ item_id: delta})

        return deltas


