import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
