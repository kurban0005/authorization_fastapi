from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool

from settings.config import settings

# Создание движка базы данных
if "sqlite" in settings.DATABASE_URL:
    # Для тестовой среды используем SQLite с правильными настройками
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # Для продакшена используем настройки по умолчанию
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """Создать и вернуть сессию базы данных.

    Yields:
        Session: Сессия базы данных для использования в контексте зависимости.

    Examples:
        >>> with next(get_db()) as db:
        ...     # работа с базой данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
