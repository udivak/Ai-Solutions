from sqlalchemy import select
from .db_connection import engine
from .tables import Customers


def get_customer_info(customer_telephone: str):
    """Fetch a customer record using the telephone number.

    Parameters
    ----------
    customer_telephone : str
        Telephone number used to identify the customer.

    Returns
    -------
    Mapping | None
        The customer row as a mapping object or ``None`` if not found.
    """

    with engine.connect() as session:
        query = select(Customers).where(Customers.c.customer_telephone == customer_telephone)
        result = session.execute(query)
        customer = result.mappings().first()
    return customer
