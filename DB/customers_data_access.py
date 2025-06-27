from sqlalchemy import select
from .db_connection import engine
from .tables import Customers


def get_customer_info(customer_telephone: str):
    with engine.connect() as session:
        query = select(Customers).where(Customers.c.customer_telephone == customer_telephone)
        result = session.execute(query)
        customer = result.mappings().first()
    return customer
