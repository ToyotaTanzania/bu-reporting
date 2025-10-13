from pydantic import BaseModel, Field
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

class ClosePeriodRequest(BaseModel):
    closed_at: datetime

    class Config:
        json_schema_extra = {
            "example": {"closed_at": "2025-09-30T23:59:59"}
        }

class LogRequest(BaseModel):
    level: str
    message: str
    module_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {"level": "info", "message": "This is a log message", "module_name": "auth"}
        }

class OkrMasterItem(BaseModel):
    id: int = 0
    bu_id: int
    value_driver_id: int
    sub_value_driver_id: int
    name: str = Field(..., max_length=255)
    alt_name1: Optional[str] = None
    alt_name2: Optional[str] = None
    alt_name3: Optional[str] = None
    alt_name4: Optional[str] = None
    ppt_row_name: Optional[str] = None
    ppt_row_sort_order: int = 0
    ppt_column_name: Optional[str] = None
    ppt_column_sort_order: int = 0
    is_aggregated: bool = False
    is_calculated: bool = False
    calculation_formula: Optional[str] = None
    is_active: bool = True
    data_type_id: Optional[int] = None
    currency_id: Optional[int] = None
    aggregation_type_id: Optional[int] = None
    metric_type_id: Optional[int] = None
    data_source_id: Optional[int] = None
    sort_order: int = 0
    is_dashboard_item: bool = False
    is_kjops_item: bool = False
    start_date: datetime
    end_date: datetime = datetime(9999, 12, 31)