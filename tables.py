from sqlalchemy import (
    Table, Column, BigInteger, Text, DateTime, Integer,
    ForeignKey, MetaData, func, PrimaryKeyConstraint, Index, JSON, String
)

metadata = MetaData()


Customers = Table(
    "Customers",
    metadata,
    Column("customer_id", BigInteger, primary_key=True, autoincrement=True),
    Column("customer_name", String(255), nullable=False),
    Column("customer_telephone", String(255), nullable=False)
)

Items = Table(
    "Items",
    metadata,
    Column("item_id", BigInteger, primary_key=True, autoincrement=True),
    Column("item_name", String(255), nullable=False),
    Column("type", String(255), nullable=False),
    Column("department", String(255), nullable=True)
)

Orders = Table(
    "Orders",
    metadata,
    Column("order_id", BigInteger, autoincrement=True, nullable=False),
    Column("customer_id", BigInteger, ForeignKey("Customers.Customer_id"), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("item_id", BigInteger, ForeignKey("Items.Item_id"), nullable=False),
    Column("quantity", BigInteger, nullable=False),
    PrimaryKeyConstraint("order_id", "customer_id", "item_id"),
    Index("customer_id", "customer_id"),
    Index("item_id", "item_id")
)

Links = Table(
    "Links",
    metadata,
    Column("link_id", Integer, primary_key=True),
    Column("link_name", String(255), nullable=False),
)

ItemLinks = Table(
    "ItemLinks",
    metadata,
    Column("item_id", BigInteger, ForeignKey("Items.item_id"), primary_key=True),
    Column("link_id", Integer, ForeignKey("Links.link_id"), primary_key=True),
    Index("link_id", "link_id")
)
