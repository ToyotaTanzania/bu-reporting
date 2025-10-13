from typing import Optional
import pymssql
from fastapi import APIRouter, Depends, HTTPException, Header
from services.admin_service import AdminService
from database import get_db
from security import require_admin
from schemas import ClosePeriodRequest, OkrMasterItem, SetPeriodRequest


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
    
@router.post("/okrs/upsert")
def upsert_okr_item(
    item: OkrMasterItem,
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.upsert_okr_master_item(item=item, user_id=x_user_id)
    except pymssql.Error as db_error:
        if "UQ_okr_master" in str(db_error):
            raise HTTPException(status_code=409, detail="An item with the same Name, Business Unit, Value Driver, and Sub Value Driver already exists.")
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.get("/okrs/list/{bu_id}")
def get_okr_master_list(
    bu_id: int,
    search_term: Optional[str] = None,
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)  
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.fetch_okr_master_list(bu_id=bu_id, search_term=search_term)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/lookup-data")
def get_all_lookup_data(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_all_lookup_data()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/okrs/{okr_master_id}")
def get_okr_master_by_id(
    okr_master_id: int,
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_okr_master_by_id(okr_master_id=okr_master_id)
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")