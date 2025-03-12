from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


import logging
from logging.config import dictConfig
from backend.api.routers.sites import router as sites_router
from backend.api.routers.sets import router as sets_router
from backend.api.routers.jobs import router as jobs_router
from backend.api.database import engine
from backend.api.settings import ApiSettings
from backend.api.logger_config import get_log_config
from fastapi.staticfiles import StaticFiles

settings = ApiSettings()


# # Configure logging using the shared configuration
dictConfig(get_log_config(timestamp=True))

# # Get logger instance
logger = logging.getLogger(__name__)


app = FastAPI()

app.mount(
    "/static/files", StaticFiles(directory=settings.base_data_directory), name="audio"
)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add static files mounting before other middleware/routers


# Include routers
app.include_router(sites_router)
app.include_router(sets_router)
app.include_router(jobs_router)


@app.on_event("startup")
async def startup_event():
    """Initialize configuration and database on startup"""
    logger.info("Starting up application")
    try:
        async with engine.begin() as conn:
            logger.info("Connected to database")
            # Uncomment to create tables
            # await conn.run_sync(Base.payload.create_all)
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
