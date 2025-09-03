from fastapi import APIRouter, Depends, Header, Request
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
    request_data: LogRequest,
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: LogService = Depends(get_log_service)
):
    if x_user_id is None:
        return {"status": "failed", "message": "User ID is missing"}

    client_ip = request.client.host

    result = service.create_log_entry(
        level=request_data.level,
        message=request_data.message,
        module_name=request_data.module_name or "general",
        user_id=x_user_id,
        client_ip=client_ip
    )
    return result