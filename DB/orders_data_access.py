from datetime import datetime, timedelta
from sqlalchemy import insert, select, and_, func
from .db_connection import engine
from .tables import Orders, Items
from utils.models import OrderRequest
from .items_data_access import map_item_names_to_ids


def insert_order_items(order_request: OrderRequest) -> int:
    """Insert order items into the database and return the new order ID.

    Parameters
    ----------
    order_request : OrderRequest
        Order request containing the customer ID and a list of items to insert.

    Returns
    -------
    int
        The generated order ID for the inserted records.
    """

    with engine.begin() as session:
        max_order_id = session.execute(select(func.max(Orders.c.order_id))).scalar()
        if type(max_order_id) != int:
            max_order_id = 0
        new_order_id = max_order_id + 1

        for item in order_request.items:
            query = insert(Orders).values(
                order_id=new_order_id,
                customer_id=order_request.customer_id,
                item_id=item.item_id,
                quantity=item.quantity
            )
            session.execute(query)
    return new_order_id


def get_orders_by_customer_id(customer_id: int):
    """Retrieve all orders associated with a specific customer.

    Parameters
    ----------
    customer_id : int
        Identifier of the customer whose orders should be fetched.

    Returns
    -------
    list[dict]
        A list of order rows represented as dictionaries.
    """

    with engine.connect() as session:
        query = select(Orders).where(Orders.c.customer_id == customer_id)
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


def find_upsells(current_order: list[dict], customer_id) -> list[dict]:
    """Suggest additional quantities based on past ordering behaviour.

    For each item in ``current_order`` the function compares the ordered
    quantity with the customer's average quantity ordered in the last three
    months. If the current quantity is lower than the historic average, the
    difference (delta) is returned.

    Parameters
    ----------
    current_order : list[dict]
        List of items in the new order. Each dictionary should contain
        ``item_name`` and ``quantity`` keys.
    customer_id : int
        ID of the customer for whom upsells are calculated.

    Returns
    -------
    list[dict]
        Suggested upsell information containing ``item_id``, ``item_name``,
        ``delta`` and ``avg_quantity`` keys.
    """

    three_months_ago = datetime.now() - timedelta(days=90)
    with engine.connect() as session:
        query = (
            select(
                Orders.c.item_id,
                Items.c.item_name,
                func.avg(Orders.c.quantity).label("avg_quantity")
            )
            .join(Items, Items.c.item_id == Orders.c.item_id)
            .where(
                and_(
                    Orders.c.customer_id == customer_id,
                    Orders.c.created_at >= three_months_ago
                )
            )
            .group_by(Orders.c.item_id)
        )
        result = session.execute(query)
        result_rows = list(result)

    past_ordered_items = {
        row[1]: {"item_id": row[0], "quantity": float(row[2])}
        for row in result_rows
    }

    current_order = map_item_names_to_ids(current_order)

    deltas = []
    for item in current_order:
        item_id = item["item_id"]
        current_qty = item["quantity"]
        item_name = item["item_name"]
        if item_name in past_ordered_items:
            avg_qty = round(past_ordered_items[item_name]["quantity"])
            if current_qty < avg_qty:
                delta = avg_qty - current_qty
                deltas.append(
                    {
                        "item_id": item_id,
                        "item_name": item_name,
                        "delta": delta,
                        "avg_quantity": avg_qty,
                    }
                )
    return deltas


def get_order_items_info(order_id: int):
    """Return detailed information about items for a specific order.

    Parameters
    ----------
    order_id : int
        The ID of the order to inspect.

    Returns
    -------
    list[dict]
        A list of dictionaries representing the joined order and item rows.
    """

    with engine.connect() as session:
        query = (
            select(Orders, Items)
            .join(Items, Orders.c.item_id == Items.c.item_id)
            .where(Orders.c.order_id == order_id)
        )
        result = session.execute(query)
        rows = list(result.mappings())
    cleaned_items = []
    for row in rows:
        row_dict = dict(row)
        row_dict.pop("item_id_1", None)
        cleaned_items.append(row_dict)
    return cleaned_items
