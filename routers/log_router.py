from fastapi import APIRouter, Depends, Header
from typing import Optional
from services.log_service import LogService
from database import get_db
from schemas import LogRequest
import pymssql


router = APIRouter()

def get_log_service(db: pymssql.Connection = Depends(get_db)):
    return LogService(db=db)

@router.post("/logs")
def add_log_entry(
    request: LogRequest,
    x_user_id: Optional[int] = Header(None),
    service: LogService = Depends(get_log_service)
):
    if x_user_id is None:
        return {"status": "failed", "message": "User ID is missing"}

    result = service.create_log_entry(
        level=request.level,
        message=request.message,
        module_name=request.module_name or "general",
        user_id=x_user_id
    )
    return result