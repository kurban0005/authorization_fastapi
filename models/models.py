from sqlalchemy import Column, Integer, String
from settings.database import Base


class User(Base):
    """Модель пользователя для базы данных."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User (id={self.id}, username='{self.username}')>"
