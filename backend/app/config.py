from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Settings
    DB_USER: str
    DB_PASSWORD: str = "" # Default to empty string if not provided
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys (Optional for now)
    VEO_API_KEY: str | None = None
    RUNWAY_API_KEY: str | None = None

    @property
    def database_url(self) -> str:
        """Constructs the MySQL connection string dynamically."""
        return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # Tells Pydantic to read variables from the .env file
        env_file = ".env"
        # If true, ignores variables in .env that aren't defined in this class
        extra = "ignore" 

# Instantiate the settings so they can be imported elsewhere
settings = Settings()