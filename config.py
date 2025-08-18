import logging
from pydantic_settings import BaseSettings
from typing import List, Union

# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Settings(BaseSettings):
    # --- Project Metadata ---
    PROJECT_NAME: str = "Business Unit Reporting API"
    API_V1_PREFIX: str = "/bu-rpt/v1"

    # --- CORS ---
    ALLOWED_ORIGINS: List[str] = [
        "*" # Please advice in case of specific domains
    ]

    # --- Database Connection Pool Settings ---
    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_POOL_SIZE: int = 5

    # --- Email Settings ---
    SENDER_EMAIL: str
    SENDER_PASSWORD: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()