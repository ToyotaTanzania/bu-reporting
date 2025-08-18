from fastapi import APIRouter, Request, Header, Depends, HTTPException
from typing import Optional, Callable
from services.bu_service import ReportingService
from database import get_db
import pymssql

router = APIRouter()

def get_reporting_service(db: pymssql.Connection = Depends(get_db)) -> ReportingService:
    return ReportingService(db=db)


@router.get("/business-units")
def get_business_units(
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")
    
    try:
        return service.fetch_business_units(user_id=x_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/okrs/{user_id}")
def get_okrs(user_id: int, service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.fetch_okrs(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/commentaries/{user_id}")
def get_commentaries(user_id: int, service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.fetch_commentaries(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/priorities/{user_id}")
def get_priorities(user_id: int, service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.fetch_priorities(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/tracker-statuses/{user_id}")
def get_tracker_statuses(user_id: int, service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.fetch_tracker_statuses(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/overdues/{user_id}")
def get_overdues(user_id: int, service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.fetch_overdues(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.put("/okrs/bulk-update")
async def bulk_update_okrs(
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        xml_data_bytes = await request.body()
        xml_string = xml_data_bytes.decode('utf-8')
        
        return service.bulk_update_okrs(xml_string=xml_string, user_id=x_user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.put("/commentaries/bulk-update")
async def bulk_update_commentaries(
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        xml_data_bytes = await request.body()
        xml_string = xml_data_bytes.decode('utf-8')
        
        return service.bulk_update_commentaries(xml_string=xml_string, user_id=x_user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.put("/priorities/bulk-update")
async def bulk_update_priorities(
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        xml_data_bytes = await request.body()
        xml_string = xml_data_bytes.decode('utf-8')
        
        return service.bulk_update_priorities(xml_string=xml_string, user_id=x_user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.put("/tracker-statuses/bulk-update")
async def bulk_update_tracker_statuses(
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        xml_data_bytes = await request.body()
        xml_string = xml_data_bytes.decode('utf-8')
        
        return service.bulk_update_tracker_statuses(xml_string=xml_string, user_id=x_user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.put("/overdues/bulk-update")
async def bulk_update_overdues(
    request: Request,
    x_user_id: Optional[int] = Header(None),
    service: ReportingService = Depends(get_reporting_service)
):
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-ID header is missing or invalid.")

    try:
        xml_data_bytes = await request.body()
        xml_string = xml_data_bytes.decode('utf-8')
        
        return service.bulk_update_overdues(xml_string=xml_string, user_id=x_user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
