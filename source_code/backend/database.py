import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = (
    os.getenv("SQLALCHEMY_DATABASE_URL")
    or os.getenv("DATABASE_URL")
)

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        "SQLALCHEMY_DATABASE_URL is missing. Create backend/.env and add your PostgreSQL URL."
    )

# Some providers use postgres://, SQLAlchemy expects postgresql://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
