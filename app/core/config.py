import os
from dotenv import load_dotenv
from pathlib import Path
from enum import Enum


class Roles(Enum):
    USER = 0
    ADMIN = 1


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Mthuw")

    #Admin account
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "Admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password")

    # Database
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "database")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_HOSTNAME: str = os.getenv("POSTGRES_HOSTNAME", "127.0.0.1")

    # JWT
    ACCESS_TOKEN_EXPIRES_IN: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 5))
    REFRESH_TOKEN_EXPIRES_IN: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 30))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")


settings = Settings()
