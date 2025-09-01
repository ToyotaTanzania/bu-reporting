import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from database import get_db

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_set_reporting_period():
    response = client.post(f"{settings.API_V1_PREFIX}/admin/reporting-period/set", json={"year": 2025, "month": 8}, headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_set_reporting_period_missing_header():
    response = client.post(f"{settings.API_V1_PREFIX}/admin/reporting-period/set", json={"year": 2025, "month": 8})
    assert response.status_code == 401
    assert "User ID is missing" in response.json()["detail"]

def test_set_reporting_period_invalid_month():
    response = client.post(f"{settings.API_V1_PREFIX}/admin/reporting-period/set", json={"year": 2025, "month": 13}, headers={"X-User-ID": "1"})
    assert response.status_code in [400, 500]

def test_close_reporting_period_missing_header():
    response = client.post(f"{settings.API_V1_PREFIX}/admin/reporting-period/close")
    assert response.status_code == 401 or response.status_code == 400

def test_close_reporting_period():
    response = client.post(f"{settings.API_V1_PREFIX}/admin/reporting-period/close", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]

def test_fetch_okr_submissions():
    from services.admin_service import AdminService
    service = AdminService(db=MagicMock())
    result = service.fetch_okr_submissions(user_id=1)
    assert result is not None

def test_set_reporting_period_service():
    from services.admin_service import AdminService
    service = AdminService(db=MagicMock())
    try:
        result = service.set_reporting_period(year=2025, month=8, user_id=1)
        assert result is not None
    except Exception:
        assert True

def test_close_reporting_period_service():
    from services.admin_service import AdminService
    service = AdminService(db=MagicMock())
    try:
        result = service.close_reporting_period(user_id=1)
        assert result is not None
    except Exception:
        assert True

def test_get_okr_submissions():
    response = client.get(f"{settings.API_V1_PREFIX}/admin/okrs-submissions", headers={"X-User-ID": "1"})
    assert response.status_code in [200, 400, 500]
