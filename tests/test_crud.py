import pytest
from unittest.mock import Mock, create_autospec, patch
from sqlalchemy.orm import Session

from crud.user_crud import create_user, get_user_by_username
from models.models import User


class TestUserFunctions:

    def test_get_user_by_username_found(self):
        """Тест получения существующего пользователя"""
        # Arrange
        mock_db = create_autospec(Session)
        mock_user = Mock(spec=User)
        mock_query = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        # Act
        result = get_user_by_username(mock_db, "testuser")

        # Assert
        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_user_by_username_not_found(self):
        """Тест получения несуществующего пользователя"""
        # Arrange
        mock_db = create_autospec(Session)
        mock_query = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = get_user_by_username(mock_db, "nonexistent")

        # Assert
        assert result is None
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        # Arrange
        mock_db = create_autospec(Session)
        username = "newuser"
        hashed_password = "hashed123"

        # Создаем mock для нового пользователя
        mock_user = Mock(spec=User)
        mock_user.username = username
        mock_user.hashed_password = hashed_password

        # Мокаем конструктор User - ИСПРАВЛЕНО: используем правильный путь
        with patch('models.models.User') as mock_user_class:
            mock_user_class.return_value = mock_user

            # Act
            result = create_user(mock_db, username, hashed_password)

            # Assert
            assert result == mock_user
            mock_user_class.assert_called_once_with(
                username=username,
                hashed_password=hashed_password
            )
            mock_db.add.assert_called_once_with(mock_user)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

    def test_create_user_rollback_on_error(self):
        """Тест отката транзакции при ошибке"""
        # Arrange
        mock_db = create_autospec(Session)
        mock_db.commit.side_effect = Exception("DB error")

        # Создаем mock пользователя
        mock_user = Mock(spec=User)

        # Мокаем конструктор User - ИСПРАВЛЕНО: используем правильный путь
        with patch('models.models.User', return_value=mock_user):
            # Act & Assert
            with pytest.raises(Exception):
                create_user(mock_db, "testuser", "hashed123")

            # Проверяем, что был вызван rollback при ошибке
            mock_db.rollback.assert_called_once()


# Дополнительные параметризованные тесты
@pytest.mark.parametrize("username", ["user1", "admin", "test-user_123"])
def test_get_user_by_username_various_names(username):
    """Тест с различными именами пользователей"""
    mock_db = create_autospec(Session)
    mock_query = Mock()

    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    result = get_user_by_username(mock_db, username)

    assert result is None
    mock_db.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()


def test_get_user_by_username_with_any():
    """Тест с использованием ANY для проверки фильтра"""
    from unittest.mock import ANY

    mock_db = create_autospec(Session)
    mock_user = Mock(spec=User)
    mock_query = Mock()

    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_user

    result = get_user_by_username(mock_db, "testuser")

    assert result == mock_user
    mock_db.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once_with(ANY)
    mock_query.first.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
