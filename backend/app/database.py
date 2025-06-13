from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator # For Python 3.9+

# Placeholder for the database URL.
# For a real PostgreSQL setup, this would be like:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# For now, we can use SQLite for simplicity if actual DB setup is deferred.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Example using SQLite in-memory

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args are specific to SQLite, remove for PostgreSQL
    connect_args={"check_same_thread": False}
)

# Create a SessionLocal class, instances of which will be actual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models to inherit from
Base = declarative_base()

# Dependency to get a DB session
def get_db() -> Generator: # For Python 3.9+ use collections.abc.Generator
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
