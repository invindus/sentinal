from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):

    class Config:
        env_file = ".env"
        extra = "ignore"    # if extra keys not defined here, ignore them

    # Database
    DATABASE_URL: str

settings = Settings()