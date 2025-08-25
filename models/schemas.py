from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Базовая модель для пользователя, содержащая обные поля."""

    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")


class UserRegister(UserBase):
    """Модель для регистрации пользователя."""

    pass


class UserLogin(UserBase):
    """Модель для входа пользователя."""

    pass


class Token(BaseModel):
    """Модель для токена доступа."""

    access_token: str
    token_type: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "your_access_token",
                "token_type": "bearer"
            }
        }
    )
