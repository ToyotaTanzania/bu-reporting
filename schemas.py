from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str = Field(..., example="user@example.com")

class VerifyRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    code: str = Field(..., example="123456")

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

class SetPeriodRequest(BaseModel):
    year: int = Field(..., example=2025)
    month: int = Field(..., example=9)