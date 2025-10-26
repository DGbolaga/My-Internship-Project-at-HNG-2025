# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 1. DETERMINE THE DATABASE URL (Don't create the engine yet)
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not explicitly set, construct it from Railway's specific Postgres vars
if not DATABASE_URL:
    DB_USER = os.getenv("PGUSER")
    DB_PASSWORD = os.getenv("PGPASSWORD")
    DB_HOST = os.getenv("PGHOST")
    DB_PORT = os.getenv("PGPORT")
    DB_NAME = os.getenv("PGDATABASE")

    # Use Postgres if environment variables are set
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        # The 'postgresql+psycopg2' dialect specifies the connection driver
        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to SQLite. This path is for local development only.
        raise EnvironmentError("DATABASE_URL or Railway PG_* variables not set. Cannot connect to database.")
    
# 2. DEFINE ENGINE AND SESSION FACTORY GLOBALLY (We will create them in main.py)
# Note: We must define a function to allow main.py to call it and get the engine.

def get_db_engine():
    # Only create the engine when this function is called
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,  
        max_overflow=20 # Good practice for cloud DBs
    )
    return engine

# Create a session factory (will be bound in main.py)
SessionLocal = sessionmaker(autocommit=False, autoflush=False)