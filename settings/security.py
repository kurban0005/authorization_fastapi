from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jwt import encode, decode, PyJWTError
from settings.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка соответствия обычного пароля и хешированного пароля."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием bcrypt."""
    # Генерируем хеш пароля
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание токена доступа с указанием времени истечения."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Декодирование токена и возврат данных, если токен действителен."""
    try:
        return decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError:
        return None
