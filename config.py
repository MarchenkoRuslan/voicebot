from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    ASSISTANT_ID: str
    
    # Make database variables optional
    PGUSER: Optional[str] = None
    PGPASSWORD: Optional[str] = None
    PGHOST: Optional[str] = None
    PGPORT: Optional[str] = None
    PGDATABASE: Optional[str] = None
    
    # For local development
    DATABASE_URL: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
        elif all([self.PGUSER, self.PGPASSWORD, self.PGHOST, self.PGPORT, self.PGDATABASE]):
            return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/voicebot"  # default value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        field_mapping = {
            'bot_token': 'TELEGRAM_BOT_TOKEN'
        }

settings = Settings()