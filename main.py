from contextlib import asynccontextmanager

from sqlalchemy import text

from crud import user_crud
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from settings.database import engine, get_db
from settings.security import verify_password, hash_password, create_access_token, decode_token
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import models
from sqlalchemy.exc import SQLAlchemyError

from models import schemas


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Создание таблиц при запуске приложения."""
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Auth API",
    lifespan=lifespan,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный ввод"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    },
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Получение текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    username: str = payload.get("sub")
    if not username:
        raise credentials_exception

    user = user_crud.get_user_by_username(db, username)
    if not user:
        raise credentials_exception
    return user


@app.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserRegister, db: Session = Depends(get_db)) -> dict:
    """Регистрация нового пользователя."""
    if user_crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже зарегистрировано",
        )

    try:
        hashed_password = hash_password(user.password)
        user_crud.create_user(db, user.username, hashed_password)
        return {"message": "Пользователь успешно зарегистрирован"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка базы данных: {str(e)}",
        )


@app.post("/token", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.Token:
    """Логин пользователя и получение токена доступа."""
    db_user = user_crud.get_user_by_username(db, user.username)

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное имя пользователя или пароль",
        )

    access_token = create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/health")
async def health_check(db: Session = Depends(get_db)) -> dict:
    """Проверка состояния сервиса и подключения к базе данных."""
    try:
        # Проверяем соединение с базой данных (оборачиваем запрос в text())
        db.execute(text("SELECT 1"))

        # Дополнительно проверяем наличие таблицы пользователей
        # Для разных СУБД используем разные запросы
        try:
            # Для PostgreSQL
            table_exists = db.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            ).scalar()
        except:
            # Для SQLite
            table_exists = db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            ).fetchone() is not None

        return {
            "status": "healthy",
            "database": "connected",
            "users_table_exists": bool(table_exists),
        }
    except SQLAlchemyError as e:
        # Логируем ошибку для диагностики
        print(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
