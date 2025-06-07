from sqlalchemy import (
    Table, Column, BigInteger, Text, DateTime, Integer,
    ForeignKey, MetaData, func, PrimaryKeyConstraint, Index
)

metadata = MetaData()

customers = Table(
    "Customers",
    metadata,
    Column("Customer_id", BigInteger, primary_key=True, autoincrement=True),
    Column("Customer_name", Text, nullable=False),
    Column("Customer_telephone", Text, nullable=False)
)

items = Table(
    "Items",
    metadata,
    Column("Item_id", BigInteger, primary_key=True, autoincrement=True),
    Column("Item_name", Text, nullable=False),
    Column("Type", Text, nullable=False)
)

orders = Table(
    "Orders",
    metadata,
    Column("Order_id", BigInteger, autoincrement=True, nullable=False),
    Column("Customer_id", BigInteger, ForeignKey("Customers.Customer_id"), nullable=False),
    Column("Created_at", DateTime, server_default=func.now(), nullable=False),
    Column("Item_id", BigInteger, ForeignKey("Items.Item_id"), nullable=False),
    Column("Quantity", BigInteger, nullable=False),
    PrimaryKeyConstraint("Order_id", "Customer_id", "Item_id"),
    Index("Customer_id", "Customer_id"),
    Index("Item_id", "Item_id")
)
