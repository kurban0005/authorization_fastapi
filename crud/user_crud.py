from sqlalchemy.orm import Session
from models import models


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Получить пользователя по имени пользователя.

    Args:
        db: Сессия базы данных
        username: Имя пользователя для поиска

    Returns:
        Объект пользователя или None, если не найден
    """
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, username: str, hashed_password: str) -> models.User:
    """Создать нового пользователя.

    Args:
        db: Сессия базы данных
        username: Имя пользователя
        hashed_password: Хэшированный пароль

    Returns:
        Созданный объект пользователя
    """
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise
