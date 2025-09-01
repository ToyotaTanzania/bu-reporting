
# --- API Endpoint Tests ---
import sys
import os
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from database import get_db
from config import settings

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_api_request_code_invalid_email():
    response = client.post(f"{settings.API_V1_PREFIX}/auth/request-code", json={"email": "not-an-email"})
    assert response.status_code in (400, 422)
    data = response.json()
    assert "Invalid email format" in data.get("detail", "") or "value is not a valid email address" in str(data)

def test_api_verify_code_missing_fields():
    response = client.post(f"{settings.API_V1_PREFIX}/auth/verify-code", json={"email": "user@example.com"})
    assert response.status_code == 422
    data = response.json()
    # FastAPI returns a list of error dicts in 'detail', check for 'Field required' in any 'msg'
    assert any(err.get("msg") == "Field required" for err in data.get("detail", []))

# --- Service Layer Error Handling Tests ---
import services.auth_service as auth_service_mod
from exceptions import EmailNotFoundError, InvalidLoginCodeError

class DummyCursor:
    def __init__(self, result=None):
        self.result = result
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def callproc(self, proc, args):
        pass
    def fetchone(self):
        return self.result
    def fetchall(self):
        return []

class DummyDB:
    def __init__(self, result=None):
        self._result = result
    def cursor(self, as_dict=True):
        return DummyCursor(self._result)
    def commit(self):
        pass

def test_service_request_login_code_email_not_found():
    service = auth_service_mod.AuthService(DummyDB(result=None))
    with pytest.raises(EmailNotFoundError):
        service.request_login_code("notfound@example.com")

def test_service_verify_login_and_get_user_email_not_found():
    service = auth_service_mod.AuthService(DummyDB(result=None))
    with pytest.raises(EmailNotFoundError):
        service.verify_login_and_get_user("notfound@example.com", "123456")

def test_service_verify_login_and_get_user_invalid_code():
    service = auth_service_mod.AuthService(DummyDB(result={"user_id": 0}))
    with pytest.raises(InvalidLoginCodeError):
        service.verify_login_and_get_user("user@example.com", "badcode")
