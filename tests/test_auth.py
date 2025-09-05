import pytest
from services.auth_service import AuthService
from exceptions import EmailNotFoundError, InvalidLoginCodeError, UserNotActiveError

class DummyCursor:
    def __init__(self, result=None, permissions=None):
        self.result = result
        self.permissions = permissions or []
        self.proc_calls = []
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def callproc(self, proc, args):
        self.proc_calls.append((proc, args))
    def fetchone(self):
        return self.result
    def fetchall(self):
        return self.permissions

class DummyDB:
    def __init__(self, result=None, permissions=None):
        self._result = result
        self._permissions = permissions
        self.committed = False
    def cursor(self, as_dict=True):
        return DummyCursor(self._result, self._permissions)
    def commit(self):
        self.committed = True

# --- request_login_code ---
def test_request_login_code_invalid_email():
    service = AuthService(DummyDB())
    with pytest.raises(ValueError):
        service.request_login_code("bad-email")

def test_request_login_code_email_not_found():
    service = AuthService(DummyDB(result=None))
    with pytest.raises(EmailNotFoundError):
        service.request_login_code("notfound@example.com")

def test_request_login_code_no_login_code():
    service = AuthService(DummyDB(result={"login_code": None}))
    with pytest.raises(Exception):
        service.request_login_code("user@example.com")

def test_request_login_code_failed_generation():
    service = AuthService(DummyDB(result={"login_code": ""}))
    with pytest.raises(Exception):
        service.request_login_code("user@example.com")

# --- verify_login_and_get_user ---
def test_verify_login_and_get_user_email_not_found():
    service = AuthService(DummyDB(result=None))
    with pytest.raises(EmailNotFoundError):
        service.verify_login_and_get_user("notfound@example.com", "123456")

def test_verify_login_and_get_user_user_not_active():
    service = AuthService(DummyDB(result={"is_active": False, "user_id": 1}))
    with pytest.raises(UserNotActiveError):
        service.verify_login_and_get_user("user@example.com", "123456")

def test_verify_login_and_get_user_invalid_code():
    db_result = {"is_active": True, "user_id": 1, "login_code": "expectedcode"}
    service = AuthService(DummyDB(result=db_result))
    with pytest.raises(InvalidLoginCodeError):
        service.verify_login_and_get_user("user@example.com", "wrongcode")

def test_verify_login_and_get_user_success():
    permissions = [
        {"module_name": "mod", "bu_name": "bu", "access_type": "read"},
        {"module_name": "mod2", "bu_name": "bu2", "access_type": "write"}
    ]
    result = {
        "is_active": True,
        "user_id": 42,
        "first_name": "Test",
        "is_admin": True,
        "period_start": None,
        "period_end": None,
        "is_period_closed": False,
        "is_priorities_month": False,
        "login_code": "goodcode"
    }
    db = DummyDB(result=result, permissions=permissions)
    service = AuthService(db)
    resp = service.verify_login_and_get_user("user@example.com", "goodcode")
    assert resp["user_id"] == 42
    assert resp["status"] == "success"
    assert resp["message"].startswith("Welcome")
    assert resp["data"]["is_admin"] is True
    assert resp["data"]["permissions"] == permissions
    assert db.committed is True
    assert isinstance(resp["data"]["permissions"], list)
    assert all("module_name" in perm and "bu_name" in perm and "access_type" in perm for perm in resp["data"]["permissions"])
