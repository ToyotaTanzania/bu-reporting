import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from database import get_db

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_get_business_units_missing_header():
    response = client.get("/bu-rpt/v1/business-units")
    assert response.status_code == 400
    assert "X-User-ID" in response.json()["detail"]

def test_get_okrs_missing_header():
    response = client.get("/bu-rpt/v1/okrs")
    assert response.status_code == 400
    assert "X-User-ID" in response.json()["detail"]
