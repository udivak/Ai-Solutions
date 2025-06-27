from sqlalchemy import text
from .db_connection import engine
from .customers_data_access import *
from .orders_data_access import *
from .items_data_access import *



def get_query_result(query: str):
    """Execute a raw SQL query and return the results as a list of mappings.

    Parameters
    ----------
    query : str
        The SQL query to execute.

    Returns
    -------
    list[dict]
        The returned rows represented as dictionaries.
    """

    with engine.begin() as session:
        result = session.execute(text(query))
        result_rows = list(result.mappings())
    return result_rows
