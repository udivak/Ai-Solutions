from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+pymysql://root:160199@127.0.0.1/Ai Direct"

engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()
