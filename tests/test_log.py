import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from database import get_db
from services.log_service import LogService
from routers.log_router import get_log_service
from config import settings

# Mock LogService
mock_log_service = MagicMock(spec=LogService)

def override_get_log_service():
    return mock_log_service

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_log_service] = override_get_log_service

client = TestClient(app)


def test_add_log_entry_success():
    mock_log_service.create_log_entry.return_value = {"status": "success"}
    response = client.post(
        f"{settings.API_V1_PREFIX}/logs",
        headers={"X-User-ID": "123"},
        json={"level": "INFO", "message": "Test log message", "module_name": "test_module"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_log_service.create_log_entry.assert_called_once_with(
        level="INFO",
        message="Test log message",
        module_name="test_module",
        user_id=123,
        client_ip="testclient"
    )
    mock_log_service.reset_mock()

def test_add_log_entry_missing_user_id():
    response = client.post(
        f"{settings.API_V1_PREFIX}/logs",
        json={"level": "INFO", "message": "Test log message", "module_name": "test_module"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "failed", "message": "User ID is missing"}

def test_add_log_entry_service_failure():
    mock_log_service.create_log_entry.return_value = {"status": "failed"}
    response = client.post(
        f"{settings.API_V1_PREFIX}/logs",
        headers={"X-User-ID": "123"},
        json={"level": "ERROR", "message": "Test failure message", "module_name": "test_failure"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "failed"}
    mock_log_service.create_log_entry.assert_called_once_with(
        level="ERROR",
        message="Test failure message",
        module_name="test_failure",
        user_id=123,
        client_ip="testclient"
    )
    mock_log_service.reset_mock()
