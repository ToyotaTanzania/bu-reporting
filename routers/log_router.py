from fastapi import APIRouter, Depends, Header, Request
from typing import Optional
from services.log_service import LogService
from database import get_db
from schemas import LogRequest
from dependencies import get_client_ip
import pymssql


router = APIRouter()

def get_log_service(db: pymssql.Connection = Depends(get_db)) -> LogService:
    return LogService(db=db)

@router.post("/logs")
def add_log_entry(
    request_data: LogRequest,
    client_ip: str = Depends(get_client_ip),
    x_user_id: Optional[int] = Header(None),
    service: LogService = Depends(get_log_service)
):
    if x_user_id is None:
        return {"status": "failed", "message": "User ID is missing"}

    return service.create_log_entry(
        level=request_data.level,
        message=request_data.message,
        module_name=request_data.module_name or "general",
        user_id=x_user_id,
        client_ip=client_ip
    )