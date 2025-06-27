from sqlalchemy import select, and_
from utils.item_processing_utils import normalize_hebrew, find_best_match
from .db_connection import engine
from .tables import Items, Links, ItemLinks


def get_all_items():
    """Return a list of all items in the database."""

    with engine.connect() as session:
        query = select(Items)
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


def get_item_info_by_id(item_id: int):
    """Fetch a single item record by its identifier."""

    with engine.connect() as session:
        query = select(Items).where(Items.c.item_id == item_id)
        result = session.execute(query)
        result_row = result.mappings().first()
    return result_row


def get_items_by_name(item_name: str):
    """Return items with an exact matching name."""

    with engine.connect() as session:
        query = select(Items).where(Items.c.item_name == item_name)
        result = session.execute(query)
        result_rows = list(result.mappings())
    return result_rows


def get_links_by_item_id(item_id: int):
    """Retrieve items that are linked to the given item ID."""

    with engine.connect() as session:
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


def get_missing_linked_items_with_context(ordered_item_ids: list[int]) -> list[dict]:
    """Suggest linked items that were not part of the order.

    Parameters
    ----------
    ordered_item_ids : list[int]
        IDs of the items included in the current order.

    Returns
    -------
    list[dict]
        Suggestions grouped by link name with context for why they were
        suggested.
    """

    with engine.connect() as session:
        il1 = ItemLinks.alias("il1")
        il2 = ItemLinks.alias("il2")

        link_query = (
            select(il1.c.link_id)
            .where(il1.c.item_id.in_(ordered_item_ids))
            .distinct()
        )
        link_ids = [row[0] for row in session.execute(link_query).fetchall()]

        suggestions_by_group = []

        for link_id in link_ids:
            link_name_query = select(Links.c.link_name).where(Links.c.link_id == link_id)
            link_name_row = session.execute(link_name_query).first()
            link_name = link_name_row[0] if link_name_row else f"Link {link_id}"

            group_items_query = (
                select(il2.c.item_id, Items.c.item_name)
                .select_from(il2.join(Items, il2.c.item_id == Items.c.item_id))
                .where(il2.c.link_id == link_id)
            )
            group_items = list(session.execute(group_items_query).mappings())

            ordered_in_group = [item for item in group_items if item["item_id"] in ordered_item_ids]
            missing_in_group = [item for item in group_items if item["item_id"] not in ordered_item_ids]

            if len(ordered_in_group) >= 1 and missing_in_group:
                suggestions_by_group.append({
                    "link_name": link_name,
                    "suggested_because_of": ordered_in_group,
                    "suggested_items": missing_in_group
                })

        return suggestions_by_group


def map_item_names_to_ids(items: list[dict]) -> list[dict]:
    """Translate item names to database IDs using fuzzy matching.

    Each dictionary in ``items`` should contain ``item_name`` and ``quantity``
    keys. The function attempts to match the given names against names in the
    database and returns the mapped list preserving the quantities.

    Parameters
    ----------
    items : list[dict]
        Raw item information with names and quantities.

    Returns
    -------
    list[dict]
        The input list where item names were replaced with the corresponding
        database name and IDs when a match was found.
    """

    mapped_items = []
    with engine.connect() as session:
        all_items_result = session.execute(select(Items.c.item_id, Items.c.item_name))
        all_items = list(all_items_result.mappings())
        normalized_map = {
            normalize_hebrew(item["item_name"]): item
            for item in all_items
        }

        for item in items:
            user_input_name = item["item_name"]
            quantity = item["quantity"]

            like_query = select(Items).where(Items.c.item_name.like(f"%{user_input_name}%"))
            result = session.execute(like_query)
            matched = result.mappings().first()

            if matched:
                db_item_name = matched["item_name"]
                item_id = matched["item_id"]
            else:
                normalized_input = normalize_hebrew(user_input_name)
                candidates = list(normalized_map.keys())
                best_match, score = find_best_match(normalized_input, candidates)

                if not best_match or score < 85:
                    db_item_name = user_input_name
                    item_id = None
                else:
                    matched = normalized_map[best_match]
                    db_item_name = matched["item_name"]
                    item_id = matched["item_id"]

            mapped_items.append({
                "item_name": db_item_name,
                "item_id": item_id,
                "quantity": quantity
            })

    return mapped_items
