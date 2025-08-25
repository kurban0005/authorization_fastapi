import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# Установка тестовых переменных окружения
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"

from main import app
from settings.database import Base, get_db

# Создание тестового движка базы данных
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Создание сессии для тестов
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    """Фикстура для создания и удаления тестовой базы данных."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Фикстура для создания тестового клиента с переопределенной зависимостью базы данных."""

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestAuthEndpoints:
    """Тесты для конечных точек аутентификации."""

    def test_register_user_success(self, client):
        """Тест успешной регистрации пользователя."""
        response = client.post(
            "/register",
            json={"username": "testuser", "password": "strongpassword"}
        )
        assert response.status_code == 201
        assert response.json() == {"message": "Пользователь успешно зарегистрирован"}

    def test_register_duplicate_user_failure(self, client):
        """Тест неудачной регистрации при попытке создать дубликат пользователя."""
        # Сначала регистрируем пользователя
        client.post(
            "/register",
            json={"username": "testuser", "password": "strongpassword"}
        )

        # Пытаемся зарегистрировать того же пользователя снова
        response = client.post(
            "/register",
            json={"username": "testuser", "password": "strongpassword"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Имя пользователя уже зарегистрировано"

    def test_login_success(self, client):
        """Тест успешного входа пользователя."""
        # Сначала регистрируем пользователя
        client.post(
            "/register",
            json={"username": "testuser", "password": "strongpassword"}
        )

        # Пытаемся войти с правильными учетными данными
        response = client.post(
            "/token",
            json={"username": "testuser", "password": "strongpassword"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Тест неудачного входа с неверными учетными данными."""
        response = client.post(
            "/token",
            json={"username": "invaliduser", "password": "wrongpassword"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Неверное имя пользователя или пароль"

    def test_health_check(self, client):
        """Тест проверки работоспособности сервиса."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "database": "connected", "users_table_exists": True}
