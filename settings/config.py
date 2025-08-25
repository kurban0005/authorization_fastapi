import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Конфигурационные настройки приложения."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@db/auth_db"
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
