from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./countries.db")

# Normalize Railway-style URLs and ensure proper driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}

# SQLite needs this flag for multithreaded use (e.g., uvicorn workers)
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
# Prefer SSL in hosted Postgres unless explicitly overridden
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    sslmode = os.getenv("DB_SSLMODE", "require")
    # psycopg2 reads sslmode from connect_args when URL lacks it
    connect_args = {"sslmode": sslmode}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_table():
    # Models must be imported so SQLAlchemy knows about tables
    from models import Country  # noqa: F401
    Base.metadata.create_all(bind=engine)

