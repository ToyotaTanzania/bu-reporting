from typing import Optional
import pymssql
from fastapi import APIRouter, Depends, HTTPException, Header
from services.admin_service import AdminService
from database import get_db
from security import require_admin
from schemas import ClosePeriodRequest, SetPeriodRequest


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


@router.get("/okrs/business-units")
def get_business_units_with_okrs(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")
    
    try:
        return service.fetch_business_units_with_okrs()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    

@router.get("/okrs/value-drivers")
def get_value_drivers(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_value_drivers()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/okrs/sub-value-drivers")
def get_sub_value_drivers(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_sub_value_drivers()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@router.get("/okrs/aggregation-types")
def get_aggregation_types(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_aggregation_types()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@router.get("/okrs/currencies")
def get_currencies(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_currencies()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@router.get("/okrs/data-sources")
def get_data_sources(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_data_sources()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@router.get("/okrs/data-types")
def get_data_types(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_data_types()
    except pymssql.Error as db_error:
        raise HTTPException(status_code=400, detail=str(db_error))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@router.get("/okrs/metric-types")
def get_metric_types(
    x_user_id: int = Depends(require_admin),
    service: AdminService = Depends(get_admin_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID is missing.")

    try:
        return service.fetch_metric_types()
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