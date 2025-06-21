from sqlalchemy import insert, select, and_, text
from utils.item_processing_utils import normalize_hebrew, find_best_match
from .db_connection import engine
from .tables import *
from utils.models import *
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound
#from utils.item_processing_utils import *
import rapidfuzz
from rapidfuzz import fuzz


def get_all_items():
    with engine.connect() as session:
        query = select(Items)
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


def get_item_info_by_id(item_id: int):
    with engine.connect() as session:
        query = select(Items).where(Items.c.item_id == item_id)             # type: ignore
        result = session.execute(query)
        result_row = result.mappings().first()
    return result_row


def get_items_by_name(item_name: str):
    with engine.connect() as session:
        query = select(Items).where(Items.c.item_name == item_name)         # type: ignore
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


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
        if type(max_order_id) != int:
            max_order_id = 0
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
    with engine.connect() as session:
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
def find_upsells(current_order: list[dict], customer_id) -> list[dict]:
    three_months_ago = datetime.now() - timedelta(days=90)
    with engine.connect() as session:
        query = select(Orders.c.item_id,
                       Items.c.item_name,
                       func.avg(Orders.c.quantity).label("avg_quantity")
                       ).join(Items, Items.c.item_id == Orders.c.item_id                            # type: ignore
                        ).where(and_(Orders.c.customer_id == customer_id,
                                    Orders.c.created_at >= three_months_ago)
                               ).group_by(Orders.c.item_id)
        result = session.execute(query)
        result_rows = list(result)

    past_ordered_items = dict()
    for row in result_rows:
        past_ordered_items[row[1]] = { "item_id": row[0], "quantity": float(row[2])}

    current_order = map_item_names_to_ids(current_order)

    deltas = []
    for item in current_order:
        item_id = item["item_id"]
        current_qty = item["quantity"]
        item_name = item["item_name"]
        if item_name in past_ordered_items.keys():
            avg_qty = round(past_ordered_items[item_name]["quantity"])
            if current_qty < avg_qty:
                delta = avg_qty - current_qty
                deltas.append( { "item_id": item_id, "item_name": item_name, "delta": delta } )
    return deltas


def get_links_by_item_id(item_id: int):
    with engine.connect() as session:
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


def get_customer_info(customer_telephone: str):
    with engine.connect() as session:
        query = select(Customers).where(Customers.c.customer_telephone == customer_telephone)       # type: ignore
        result = session.execute(query)
        customer = result.mappings().first()
    return customer


def get_order_items_info(order_id: int):
    with engine.connect() as session:
        query = select(Orders, Items).join(Items, Orders.c.item_id == Items.c.item_id).where(Orders.c.order_id == order_id)         # type: ignore
        result = session.execute(query)
        rows = list(result.mappings())
    cleaned_items = []
    for row in rows:
        row_dict = dict(row)
        # Remove duplicate / renamed item_id_1
        row_dict.pop("item_id_1", None)
        cleaned_items.append(row_dict)
    return cleaned_items


def get_query_result(query: str):
    with engine.begin() as session:
        result = session.execute(text(query))
        result_rows = list(result.mappings())
    return result_rows


def map_item_names_to_ids(items: list[dict]) -> list[dict]:
    mapped_items = []
    with engine.connect() as session:
        all_items_result = session.execute(select(Items.c.item_id, Items.c.item_name))
        all_items = list(all_items_result.mappings())                           # [ (item_id, item_name), (...) ]
        normalized_map = {
            normalize_hebrew(item["item_name"]): item
            for item in all_items
        }

        for item in items:
            item_name = item["item_name"]
            quantity = item["quantity"]
            # Do LIKE query (e.g., WHERE item_name LIKE '%<item_name>%')
            like_query = select(Items).where(Items.c.item_name.like(f"%{item_name}%"))
            result = session.execute(like_query)
            matched = result.mappings().first()
            if not matched:
                # Normalize and fuzzy match
                normalized_input = normalize_hebrew(item_name)
                candidates = list(normalized_map.keys())
                # best_match, score, _ = rapidfuzz.process.extractOne(                                                #type: ignore
                #     normalized_input,
                #     candidates,
                #     scorer=fuzz.WRatio
                # )
                best_match, score = find_best_match(normalized_input, candidates)
                if not best_match or score < 75:
                    raise ValueError(f"No good match for item: {item_name} (Score: {score})")
                item_name = best_match
                matched = normalized_map[best_match]

            mapped_items.append( {
                "item_name": item_name,
                "item_id": matched["item_id"],
                "quantity": quantity
            } )

    return mapped_items