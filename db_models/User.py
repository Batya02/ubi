from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import create_engine

metadata = MetaData()

all_users_table = Table(
    "all_users", metadata, 
    Column("user_id", Integer), 
    Column("username", String(255)), 
    Column("date_registration", String), 
    Column("language", String)
)

data_users_table = Table(
    "data_users", metadata, 
    Column("user_id", Integer), 
    Column("date", String), 
    Column("status", String), 
    Column("last_phone", String), 
    Column("last_date", String)
)

engine = create_engine("sqlite:///database/data_bomber.db")
metadata.create_all(engine)