import os
import logging
from typing import List, Optional
from pydantic import EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bu-reporting")


# -------------------- Load local env --------------------
# Load .env.local first (highest priority), then .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
    # logger.debug("Loaded .env.local for local development.")
elif os.path.exists(".env"):
    load_dotenv(".env")
    # logger.debug("Loaded .env for local development.")



def get_secret(secret_name: str) -> str:
    """
    Fetch secret from Google Secret Manager in production,
    otherwise read from environment variables (local development).
    """
    running_locally = os.getenv("RUNNING_LOCALLY", "0") == "1"
    if running_locally:
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Secret '{secret_name}' not found in local environment.")
        logger.info("Local secrets fetching completed")
        return value.strip()
    
    # Production: use Secret Manager
    from google.cloud import secretmanager
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "devproject212")
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8").strip()

def load_all_secrets() -> dict:
    """Fetch all required secrets once."""
    return {
        "DB_SERVER": get_secret("DB_SERVER"),
        "DB_DATABASE": get_secret("DB_DATABASE"),
        "DB_USER": get_secret("DB_USER"),
        "DB_PASSWORD": get_secret("DB_PASSWORD"),
        "SENDER_EMAIL": get_secret("SENDER_EMAIL"),
        "SENDER_PASSWORD": get_secret("SENDER_PASSWORD"),
    }


# -------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------
class Settings(BaseSettings):
    PROJECT_NAME: str = "Business Unit Reporting API"
    API_V1_PREFIX: str = "/bu-rpt/v1"
    ALLOWED_ORIGINS: List[str] = ["https://devproject212.oa.r.appspot.com"]
    DB_POOL_SIZE: int = 5

    # Secrets (optional at declaration → filled later)
    DB_SERVER: Optional[str] = None
    DB_DATABASE: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        secrets = load_all_secrets()
        self.DB_SERVER = secrets["DB_SERVER"]
        self.DB_DATABASE = secrets["DB_DATABASE"]
        self.DB_USER = secrets["DB_USER"]
        self.DB_PASSWORD = secrets["DB_PASSWORD"]
        self.SENDER_EMAIL = secrets["SENDER_EMAIL"]
        self.SENDER_PASSWORD = secrets["SENDER_PASSWORD"]

        logger.info("[Config] ✅ All secrets fetched and loaded.")
    
    class Config:
        case_sensitive = True

# -------------------------------------------------------------------
# Global settings instance
# -------------------------------------------------------------------
settings = Settings()
