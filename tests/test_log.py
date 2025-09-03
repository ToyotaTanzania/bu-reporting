import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_add_log_entry_success():
    payload = {
        "level": "info",
        "message": "Test log message",
        "module_name": "test_module"
    }
    headers = {"x-user-id": "123"}
    response = client.post("/logs", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_add_log_entry_missing_user_id():
    payload = {
        "level": "info",
        "message": "Test log message",
        "module_name": "test_module"
    }
    response = client.post("/logs", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["message"] == "User ID is missing"


def test_add_log_entry_missing_required_field():
    payload = {
        "message": "Test log message"
        # Missing 'level'
    }
    headers = {"x-user-id": "123"}
    response = client.post("/logs", json=payload, headers=headers)
    assert response.status_code == 422

