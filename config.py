import os
import logging
from typing import List
from pydantic import EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# -------------------- Logging --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bu-reporting")

# -------------------- Load local env --------------------
# Load .env.local first (highest priority), then .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
    logger.debug("Loaded .env.local for local development.")
elif os.path.exists(".env"):
    load_dotenv(".env")
    logger.debug("Loaded .env for local development.")

# -------------------- Secret Fetching --------------------
def get_secret(secret_name: str) -> str:
    """
    Fetch secret from Google Secret Manager in production,
    otherwise read from environment variables (local development).
    """
    running_locally = os.getenv("RUNNING_LOCALLY", "0") == "1"
    if running_locally:
        logger.debug(f"[DEBUG] RUNNING_LOCALLY={running_locally}")
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Secret '{secret_name}' not found in local environment.")
        logger.debug(f"[DEBUG] Fetched {secret_name} from local environment")
        return value

    # Production: use Secret Manager
    from google.cloud import secretmanager
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "devproject212")  # update if needed
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    logger.debug(f"[DEBUG] Fetching {secret_name} from Secret Manager: {secret_path}")
    print(f"[DEBUG] Fetching {secret_name} from Secret Manager: {secret_path}")
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")


# -------------------- Settings --------------------
class Settings(BaseSettings):
    # Project Metadata
    PROJECT_NAME: str = "Business Unit Reporting API"
    API_V1_PREFIX: str = "/bu-rpt/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://devproject212.oa.r.appspot.com"
    ]

    # Database
    # DB_SERVER: str = get_secret("DB_SERVER")
    DB_SERVER="41.175.62.42"
    DB_DATABASE: str = get_secret("DB_DATABASE")
    DB_USER: str = get_secret("DB_USER")
    DB_PASSWORD: str = get_secret("DB_PASSWORD")
    DB_POOL_SIZE: int = 5

    # Email
    SENDER_EMAIL: EmailStr = get_secret("SENDER_EMAIL")
    SENDER_PASSWORD: str = get_secret("SENDER_PASSWORD")

    class Config:
        case_sensitive = True


# -------------------- Load settings --------------------
settings = Settings()
