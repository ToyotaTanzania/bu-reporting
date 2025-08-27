from pydantic import BaseModel
from typing import List
from datetime import datetime


class LoginRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    code: str

class PermissionResponse(BaseModel):
    module_name: str
    bu_name: str
    access_type: str

class LoginSuccessResponse(BaseModel):
    user_id: int
    is_admin: bool
    period_start: datetime
    period_end: datetime
    period_closed_at: datetime
    is_priorities_month: bool
    status: str
    message: str
    permissions: List[PermissionResponse]