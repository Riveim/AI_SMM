from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    FRONTEND_URL: str = "http://localhost:5500"

    class Config:
        env_file = ".env"


settings = Settings()
