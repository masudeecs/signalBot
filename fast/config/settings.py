import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
from functools import lru_cache

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    
    # Database
    DB_USER: str = os.getenv('MYSQL_USER')
    DB_PASSWORD: str = os.getenv('MYSQL_PASSWORD')
    DB_NAME: str = os.getenv('MYSQL_DB')
    DB_HOST: str = os.getenv('MYSQL_HOST')
    DB_PORT: str = os.getenv('MYSQL_PORT')
    DATABASE_URL: str = f"mysql+pymysql://{DB_USER}:%s@{DB_HOST}:{DB_PORT}/{DB_NAME}" % quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./health.db"
    # SQLALCHEMY_CHAT_DATABASE_URL: str = "sqlite:///./chat.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
    
    # JWT Secret Key
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "649fb93ef34e4fdf4187709c84d643dd61ce730d91856418fdcf563f895ea40f")
    JWT_ALGORITHM: str = os.environ.get("ACCESS_TOKEN_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 1440))

    # App Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "e52f9e26972be008ead024864a3d9e6ddf1946b844497d13c29f68f103fe97e1")
    
    # OPENAPI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL_NAME: str = os.getenv('OPENAI_MODEL_NAME')

@lru_cache()
def get_settings() -> Settings:
    return Settings()