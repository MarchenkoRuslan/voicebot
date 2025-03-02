from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Поддержка обоих вариантов подключения к БД
    DATABASE_URL: Optional[str] = None
    PGUSER: Optional[str] = None
    PGPASSWORD: Optional[str] = None
    PGHOST: Optional[str] = None
    PGPORT: Optional[str] = None
    PGDATABASE: Optional[str] = None
    
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    ASSISTANT_ID: str
    
    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            # Если есть полный URL, используем его
            base_url = self.DATABASE_URL
            if "+asyncpg" not in base_url:
                return base_url.replace("postgresql://", "postgresql+asyncpg://")
            return base_url
        
        # Иначе собираем из компонентов
        if all([self.PGUSER, self.PGPASSWORD, self.PGHOST, self.PGPORT, self.PGDATABASE]):
            return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"
        
        raise ValueError("No database configuration provided")

    class Config:
        env_file = ".env"

settings = Settings()

if __name__ == "__main__":
    print(f"Database URL: {settings.get_database_url}")
    print("All settings loaded successfully!") 