from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.shared.config import get_settings


settings = get_settings()
database_url = settings.normalized_database_url

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
