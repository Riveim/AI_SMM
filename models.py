from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Numeric, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    businesses: Mapped[list["Business"]] = relationship(back_populates="user")


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tone: Mapped[str] = mapped_column(String(100), default="нейтральный")
    target_audience: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="businesses")
    products: Mapped[list["Product"]] = relationship(back_populates="business", cascade="all, delete")
    prompt_templates: Mapped[list["PromptTemplate"]] = relationship(back_populates="business", cascade="all, delete")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="business", cascade="all, delete")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)

    business: Mapped["Business"] = relationship(back_populates="products")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    platform: Mapped[str] = mapped_column(String(50), default="telegram")
    content_type: Mapped[str] = mapped_column(String(50), default="reply")
    template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship(back_populates="prompt_templates")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    telegram_chat_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sender_username: Mapped[str] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_reply: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="chat_messages")
