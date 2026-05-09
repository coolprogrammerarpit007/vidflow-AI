import os
from pydantic_settings import BaseSettings

# Get the absolute path of the backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # Database Settings
    DB_USER: str
    DB_PASSWORD: str = "" 
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys 
    VEO_API_KEY: str | None = None
    RUNWAY_API_KEY: str | None = None

    @property
    def database_url(self) -> str:
        return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # Dynamically point to the exact location of .env
        env_file = ENV_FILE_PATH
        extra = "ignore" 

settings = Settings()