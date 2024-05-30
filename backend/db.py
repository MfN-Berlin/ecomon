import os
import databases
from dotenv import load_dotenv
from logging import getLogger
logger = getLogger(__name__)
load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = int(os.getenv("POSTGRES_PORT"))
dbname = os.getenv("POSTGRES_DATABASE")

database_connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
logger.debug(f"Database connection string: {database_connection_string}")
database = databases.Database(database_connection_string)

async def connect_to_db():
    await database.connect()

async def disconnect_from_db():
    await database.disconnect()
