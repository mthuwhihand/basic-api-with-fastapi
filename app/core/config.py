import os
import ssl
from dotenv import load_dotenv
from pathlib import Path
from enum import Enum
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType


class AccountStatuses(Enum):
    ACTIVE = "Active"
    DELETED = "Deleted"
    SUSPENDING = "Suspending"


class TokenStatuses(Enum):
    ACTIVE = "Active"
    NON_LONGER_ACTIVE = "No longer active"


class Roles(Enum):
    USER = "User"
    ADMIN = "Admin"


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Mthuw")

    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Admin account
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "Admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "0862312032")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password")

    # EMAIL ACCOUNT FOR SENDMAIL SERVICE
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "Hihand Team")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "HiHand Team")
    MAIL_USE_TLS: bool = bool(os.getenv("MAIL_USE_TLS", True))
    MAIL_USE_SSL: bool = bool(os.getenv("MAIL_USE_SSL", False))

    # Database
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "database")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_HOSTNAME: str = os.getenv("POSTGRES_HOSTNAME", "127.0.0.1")

    # JWT
    RESET_PASS_ACCESS_TOKEN_EXPIRES_IN: int = int(
        os.getenv("RESET_PASS_ACCESS_TOKEN_EXPIRES_IN", 2)
    )
    ACCESS_TOKEN_EXPIRES_IN: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 5))
    REFRESH_TOKEN_EXPIRES_IN: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 30))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")

    # REGEX
    PASSWORD_REGEX: str = os.getenv("PASSWORD_REGEX", r"^(?=.{7,99}$).*")


settings = Settings()

sendmail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,  # Bỏ qua xác minh chứng chỉ
)
