import os
import databases
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse

from routes.records import router as records_router
from routes.predictions import router as predictions_router
from routes.collections import router as collections_router
from routes.jobs import router as jobs_router
from routes.random import router as random_router
from routes.evaluation import router as evaluation_router
from sql.initial import create_jobs_table

load_dotenv()

path_prefix = os.getenv("ROOT_PATH")
# initiliaze database connection
user = os.getenv("MDAS_MARIADB_USER")

password = os.getenv("MDAS_MARIADB_PASSWORD")
host = os.getenv("MDAS_MARIADB_HOST")
port = int(os.getenv("MDAS_MARIADB_PORT"))
database = os.getenv("MDAS_MARIADB_DATABASE")
database_connection_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4".format(
    user=user, password=password, host=host, port=port, dbname=database
)
# print(database_connection_string)
# print(user)
# print(password)

database = databases.Database(database_connection_string)


# A Pydantic model


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()

    # check if table jobs exists and create if not
    await database.execute(create_jobs_table())


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def read_root():
    return RedirectResponse(
        "{}/docs".format(path_prefix if path_prefix else ""), status_code=302
    )


# initialize routes

records_router(app, "/prefix", database)
predictions_router(app, "/prefix", database)
collections_router(app, "/prefix", database)
jobs_router(app, "/jobs", database)
evaluation_router(app, "/evaluation", database)
random_router(app, "", database)

