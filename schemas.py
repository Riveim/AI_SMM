from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


# ─── Auth ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    login: str
    email: EmailStr
    password: str

    @field_validator("login")
    @classmethod
    def login_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Логин должен быть не менее 3 символов")
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
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    model_config = {"from_attributes": True}


# ─── Business ────────────────────────────────────────────────────────────────

class BusinessCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tone: str = "нейтральный"
    target_audience: Optional[str] = None
    keywords: list[str] = []


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    keywords: Optional[list[str]] = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    tone: str
    target_audience: Optional[str]
    keywords: list[str]
    model_config = {"from_attributes": True}


# ─── Product ─────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Optional[float]
    category: Optional[str]
    model_config = {"from_attributes": True}


# ─── Prompt Template ─────────────────────────────────────────────────────────

class PromptTemplateCreate(BaseModel):
    platform: str = "telegram"
    content_type: str = "reply"
    template: str


class PromptTemplateResponse(BaseModel):
    id: int
    platform: str
    content_type: str
    template: str
    is_active: bool
    model_config = {"from_attributes": True}
