# app/database.py
import os
import databases
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("MDAS_MARIADB_USER")
password = os.getenv("MDAS_MARIADB_PASSWORD")
host = os.getenv("MDAS_MARIADB_HOST")
port = int(os.getenv("MDAS_MARIADB_PORT"))
database_name = os.getenv("MDAS_MARIADB_DATABASE")
database_connection_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4".format(
    user=user, password=password, host=host, port=port, dbname=database_name
)

database = databases.Database(database_connection_string)

async def connect_to_db():
    await database.connect()

async def disconnect_from_db():
    await database.disconnect()
