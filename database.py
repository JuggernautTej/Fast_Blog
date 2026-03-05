"""Database configuration for the FastAPI blog application aka FastBlog."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL ="sqlite:///.blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

def get_db():
    """Dependency function that provides a database session and handles cleanup independently."""
    with SessionLocal() as db:
        yield db


