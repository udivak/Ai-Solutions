from sqlalchemy import insert, select, delete, update, func, and_
from db_connection import engine
from tables import *
from models import *
from datetime import datetime, timedelta

def get_all_items():
    with engine.begin() as session:
        query = select(Items)
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


def get_item_info(item_id: int):
    with engine.begin() as session:
        query = select(Items).where(Items.c.item_id == item_id)             # type: ignore
        result = session.execute(query)
        result_row = result.mappings().first()
    return result_row

"""
Insert items of the given order into the orders table.

Args:
    order_request (OrderRequest): The order to insert items from.

Returns:
    int: The new order id.
"""
def insert_order_items(order_request: OrderRequest) -> int:
    with engine.begin() as session:
        max_order_id = session.execute(select(func.max(Orders.c.order_id))).scalar()
        new_order_id = max_order_id + 1

        for item in order_request.items:
            query = insert(Orders).values(
                order_id= new_order_id,
                customer_id=order_request.customer_id,
                item_id=item.item_id,
                quantity=item.quantity
            )
            session.execute(query)
    return new_order_id


def get_orders_by_customer_id(customer_id: int):
    with engine.begin() as session:
        query = select(Orders).where(Orders.c.customer_id == customer_id)         # type: ignore
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


"""
Find items that current order have less quantity than the average quantity of the customer's previous orders.

Args:
    current_order (OrderRequest): The order to compare with.
    new_order_id (int): The id of the new order, to exclude it from the calculation.

Returns:
    list[dict]: A list of dictionaries, each dictionary has a single key-value pair,
        where the key is the item_id and the value is the quantity difference.
"""
def find_upsells(current_order: OrderRequest, new_order_id: int):
    three_months_ago = datetime.now() - timedelta(days=90)
    with engine.begin() as session:
        query = select(Orders.c.Item_id, func.avg(Orders.c.Quantity).label("avg_quantity")
                       ).where(and_(Orders.c.customer_id == current_order.customer_id,
                                    Orders.c.order_id != new_order_id,
                                    Orders.c.created_at >= three_months_ago
                                    )
                               ).group_by(Orders.c.item_id)
        result = session.execute(query)
        result_rows = list(result)

    deltas = []
    avg_quantity_by_item_id = { row[0]: float(row[1]) for row in result_rows }

    for item in current_order.items:
        item_id = item.item_id
        current_qty = item.quantity
        if item_id in avg_quantity_by_item_id.keys():
            avg_qty = round(avg_quantity_by_item_id[item_id])
            if current_qty < avg_qty:
                delta = avg_qty - current_qty
                deltas.append({ item_id: delta})
    return deltas


def get_links_by_item_id(item_id: int):
    with engine.begin() as session:
        # Aliases for the ItemLinks table
        il1 = ItemLinks.alias("il1")
        il2 = ItemLinks.alias("il2")

        query = (
            select(Items, Links)
            .select_from(
                il1
                .join(il2, il1.c.link_id == il2.c.link_id)
                .join(Items, Items.c.item_id == il2.c.item_id)
                .join(Links, il1.c.link_id == Links.c.link_id)
            )
            .where(
                and_(
                    il1.c.item_id == item_id,
                    il2.c.item_id != item_id
                )
            )
        )
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows
