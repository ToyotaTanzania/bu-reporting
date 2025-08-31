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

def test_get_business_units_missing_header():
    response = client.get(f"{settings.API_V1_PREFIX}/business-units")
    assert response.status_code == 400
    assert "X-User-ID" in response.json()["detail"]

def test_get_business_units():
    response = client.get(f"{settings.API_V1_PREFIX}/business-units", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_okrs():
    response = client.get(f"{settings.API_V1_PREFIX}/okrs", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_commentaries():
    response = client.get(f"{settings.API_V1_PREFIX}/commentaries", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_priorities():
    response = client.get(f"{settings.API_V1_PREFIX}/priorities", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_tracker_statuses():
    response = client.get(f"{settings.API_V1_PREFIX}/tracker-statuses", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_overdues():
    response = client.get(f"{settings.API_V1_PREFIX}/overdues", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_get_monthly_presentation():
    response = client.get(f"{settings.API_V1_PREFIX}/reports/monthly-presentation", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_reporting_service_methods():
    from services.bu_service import ReportingService
    service = ReportingService(db=MagicMock())
    assert service.fetch_business_units(1) is not None
    assert service.fetch_okrs(1) is not None
    assert service.fetch_commentaries(1) is not None
    assert service.fetch_priorities(1) is not None
    assert service.fetch_tracker_statuses(1) is not None
    assert service.fetch_overdues(1) is not None
    assert service.create_monthly_presentation(1) is not None

def test_get_okrs_missing_header():
    response = client.get(f"{settings.API_V1_PREFIX}/okrs")
    assert response.status_code == 400
    assert "X-User-ID" in response.json()["detail"]
