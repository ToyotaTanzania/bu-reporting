from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from services.admin_service import AdminService
from database import get_db
import pymssql
from schemas import SetPeriodRequest


router = APIRouter()

def get_admin_service(db: pymssql.Connection = Depends(get_db)) -> AdminService:
    return AdminService(db=db)


@router.post("/reporting-period")
def set_reporting_period(
    request: SetPeriodRequest,
    x_user_id: Optional[int] = Header(None),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")
    
    try:
        return service.set_reporting_period(
            year=request.year,
            month=request.month,
            user_id=x_user_id
        )
    except pymssql.DatabaseError as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/okrs-submissions")
def get_okr_submissions(
    service: AdminService = Depends(get_admin_service)
):
    try:
        return service.fetch_okr_submissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")