# app/main.py


from logging import getLogger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from os import getenv

from db import database, connect_to_db, disconnect_from_db


# Import routers
from routes.prefix.records import router as records_router
from routes.prefix.predictions import router as predictions_router
from routes.prefix.collections import router as collections_router
from routes.jobs import router as jobs_router
from routes.random import router as random_router
from routes.evaluation import router as evaluation_router

logger = getLogger(__name__)
root_path = getenv("ROOT_PATH")

app = FastAPI(root_path=root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    from logger import get_log_config
    get_log_config(getenv("LOG_LEVEL","debug"))
    await connect_to_db()
    # check if table jobs exists and create if not


@app.on_event("shutdown")
async def shutdown():
    await disconnect_from_db()

@app.get("/")
def read_root():
    return RedirectResponse(
        "/docs", status_code=302
    )

# Initialize routes
app.include_router(records_router, prefix="/prefix")
app.include_router(predictions_router, prefix="/prefix")
app.include_router(collections_router, prefix="/prefix")
app.include_router(jobs_router, prefix="/jobs")
app.include_router(evaluation_router, prefix="/evaluation")
app.include_router(random_router, prefix="")
