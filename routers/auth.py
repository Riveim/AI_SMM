from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.login == data.login))).scalar_one_or_none():
        raise HTTPException(400, "Логин уже занят")
    if (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none():
        raise HTTPException(400, "Email уже зарегистрирован")

    user = User(login=data.login, email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where((User.login == data.login_or_email) | (User.email == data.login_or_email))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Неверный логин или пароль")
    if not user.is_active:
        raise HTTPException(403, "Аккаунт деактивирован")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
