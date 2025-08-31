import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from database import get_db

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_request_code_invalid_email():
    response = client.post(f"{settings.API_V1_PREFIX}/auth/request-code", json={"email": "not-an-email"})
    assert response.status_code == 422 or response.status_code == 400

def test_verify_code_missing_fields():
    response = client.post(f"{settings.API_V1_PREFIX}/auth/verify-code", json={"email": "user@example.com"})
    assert response.status_code == 422
