from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com"}
        }


class VerifyRequest(BaseModel):
    email: str
    code: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "code": "123456"}
        }

class Permission(BaseModel):
    module_name: str
    bu_name: str
    access_type: str

    class Config:
        from_attributes = True

class UserData(BaseModel):
    is_admin: bool = False
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    is_period_closed: bool
    is_priorities_month: bool
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

class LoginSuccessResponse(BaseModel):
    user_id: int
    status: str = "success"
    message: str
    data: UserData

    class Config:
        from_attributes = True

class LoginFailedResponse(BaseModel):
    user_id: int
    status: str
    message: str

    class Config:
        from_attributes = True

class SetPeriodRequest(BaseModel):
    year: int
    month: int
    user_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {"year": 2025, "month": 9}
        }

class LogRequest(BaseModel):
    level: str
    message: str
    module_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {"level": "info", "message": "This is a log message", "module_name": "auth"}
        }