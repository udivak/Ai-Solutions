from sqlalchemy import text
from .db_connection import engine
from .customers_data_access import *
from .orders_data_access import *
from .items_data_access import *



def get_query_result(query: str):
    with engine.begin() as session:
        result = session.execute(text(query))
        result_rows = list(result.mappings())
    return result_rows
