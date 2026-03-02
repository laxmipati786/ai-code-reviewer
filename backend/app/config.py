from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AI Code Reviewer"
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "code_reviewer"
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    max_code_length: int = 50000

    class Config:
        env_file = ".env"


settings = Settings()
