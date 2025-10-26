# database.py - Optimized for Railway's Postgres service
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os



DATABASE_URL = os.getenv("DATABASE_URL")

# If the standard DATABASE_URL is not set, construct it from Railway's specific Postgres vars
if not DATABASE_URL:
    DB_USER = os.getenv("PGUSER")
    DB_PASSWORD = os.getenv("PGPASSWORD")
    DB_HOST = os.getenv("PGHOST")
    DB_PORT = os.getenv("PGPORT")
    DB_NAME = os.getenv("PGDATABASE")

    # If any PG var is set, use Postgres
    if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to local SQLite, but this will fail on Railway.
        DATABASE_URL = "sqlite:///./countries.db" 

# Create engine - remove connect_args for cloud deployment (only needed for local SQLite)
# Use a pool size to prevent connection errors on Postgres
engine = create_engine(
    DATABASE_URL,
    pool_size=10, 
    max_overflow=20 # Good practice for cloud DBs
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)