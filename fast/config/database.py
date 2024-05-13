from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from config.settings import get_settings

settings = get_settings()

# mysql engine 
# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,
#     pool_recycle=300,
#     pool_size=5,
#     max_overflow=0
# )
    

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



