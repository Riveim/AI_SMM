from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    login: str
    email: EmailStr
    password: str

    @field_validator("login")
    @classmethod
    def login_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Логин должен быть не менее 3 символов")
        if len(v) > 50:
            raise ValueError("Логин не должен превышать 50 символов")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        return v


class LoginRequest(BaseModel):
    login_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    login: str
    email: str

    model_config = {"from_attributes": True}
