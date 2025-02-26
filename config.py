from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    OPENAI_API_KEY: str
    ASSISTANT_ID: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()