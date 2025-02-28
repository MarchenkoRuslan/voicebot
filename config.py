from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    ASSISTANT_ID: str
    
    # Переменные для базы данных
    PGUSER: str
    PGPASSWORD: str
    PGHOST: str
    PGPORT: str
    PGDATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        field_mapping = {
            'bot_token': 'TELEGRAM_BOT_TOKEN'
        }

settings = Settings()