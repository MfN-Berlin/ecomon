from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from backend.worker.settings import WorkerSettings
from backend.shared.models.db.models import Base, Jobs, Records  # Import all models
from sqlalchemy.pool import NullPool

settings = WorkerSettings()

# Shared base payload
Base = declarative_base(metadata=MetaData())

# Configure both engines with the same payload
database_engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=settings.debug,  # Add SQL logging in debug mode
)

# Create a scoped session factory
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=database_engine)
)


def get_new_Session():
    return scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=database_engine)
    )
