from typing import Optional
import pymssql
from fastapi import APIRouter, Depends, HTTPException, Header
from services.admin_service import AdminService
from database import get_db
from security import require_admin
from schemas import ClosePeriodRequest, SetPeriodRequest, OKRMasterListRequest


router = APIRouter()

def get_admin_service(db: pymssql.Connection = Depends(get_db)) -> AdminService:
    return AdminService(db=db)


@router.post("/submission-period/set")
def set_submission_period(
    request: SetPeriodRequest,
    x_user_id: Optional[int] = Header(None),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.set_submission_period(
            year=request.year,
            month=request.month,
            user_id=x_user_id
        )
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.post("/submission-period/close")
def close_submission_period(
    request: ClosePeriodRequest,
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.close_submission_period(user_id=x_user_id, closed_at=request.closed_at)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.post("/submission-period/open")
def open_submission_period(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.open_submission_period(user_id=x_user_id)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.get(f"/okrs/list/{{bu_id}}")
def get_okr_master_list(
    bu_id: int,
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.fetch_okr_master_list(bu_id=bu_id)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    
@router.get("/okrs/business-units")
def get_business_units_with_okrs(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.fetch_business_units_with_okrs(user_id=x_user_id)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")