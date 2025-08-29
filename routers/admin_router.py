import pymssql
from fastapi import APIRouter, Header, Depends, HTTPException
from typing import Optional
from services.admin_service import AdminService
from database import get_db
from security import require_admin


router = APIRouter()
def get_admin_service(db: pymssql.Connection = Depends(get_db)) -> AdminService:
    return AdminService(db=db)


@router.post("/close-reporting-period") # Renamed for clarity
def close_reporting_period(
    user_id: int = Depends(require_admin), # <-- Apply the security check here
    service: AdminService = Depends(get_admin_service)
):
    try:
        return service.close_reporting_period(user_id=user_id)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/okrs-submissions")
def get_okr_submissions(
    x_user_id: Optional[int] = Header(None),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        return service.fetch_okr_submissions(user_id=x_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")