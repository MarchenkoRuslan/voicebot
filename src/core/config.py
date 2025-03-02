from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PGUSER: str
    PGPASSWORD: str
    PGHOST: str
    PGPORT: str
    PGDATABASE: str
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    ASSISTANT_ID: str
    
    @property
    def get_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

    class Config:
        env_file = ".env"

settings = Settings()

if __name__ == "__main__":
    print(f"Database URL: {settings.get_database_url}")
    print("All settings loaded successfully!") 