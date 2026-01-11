from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    EXA_API_KEY: str
    OPENAI_API_KEY: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:80"

    # App settings
    LOG_LEVEL: str = "INFO"
    DATA_DIR: str = "data"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
