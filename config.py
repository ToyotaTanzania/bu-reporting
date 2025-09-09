import os
import logging
from typing import List
from pydantic import EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

# -------------------- Logging --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bu-reporting")

# -------------------- Secret Fetching --------------------
def get_secret(secret_name: str) -> str:
    """
    Fetch secret from Google Secret Manager if running in production,
    otherwise read from environment variables (local development).
    """
    running_locally = os.getenv("RUNNING_LOCALLY", "0") == "1"
    
    print(f"[DEBUG] RUNNING_LOCALLY={running_locally}") 

    if running_locally:
        print(f"[DEBUG] Fetching {secret_name} from local environment")
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Secret {secret_name} not found in .env")
        return value

    # Production: use Secret Manager
    from google.cloud import secretmanager
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "devproject212")
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    
    print(f"[DEBUG] Fetching {secret_name} from Secret Manager : {secret_path}")
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
    DB_SERVER: str = get_secret("DB_SERVER")
    DB_DATABASE: str = get_secret("DB_DATABASE")
    DB_USER: str = get_secret("DB_USER")
    DB_PASSWORD: str = get_secret("DB_PASSWORD")
    DB_POOL_SIZE: int = 5

    # Email
    SENDER_EMAIL: EmailStr = get_secret("SENDER_EMAIL")
    SENDER_PASSWORD: str = get_secret("SENDER_PASSWORD")

# -------------------- Load settings --------------------
settings = Settings()

# Optional quick test for local vs production
print("[DEBUG] DB_SERVER:", settings.DB_SERVER)
print("[DEBUG] SENDER_EMAIL:", settings.SENDER_EMAIL)
