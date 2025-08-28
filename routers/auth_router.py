from fastapi import APIRouter, Depends, HTTPException
import pymssql

from services.auth_service import AuthService
from database import get_db
from typing import Union
from schemas import LoginRequest, VerifyRequest, LoginSuccessResponse, LoginFailedResponse

router = APIRouter()

def get_auth_service(db: pymssql.Connection = Depends(get_db)) -> AuthService:
    return AuthService(db=db)

@router.post("/request-code")
def request_code(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        return service.request_login_code(email=request.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred while requesting the login code.")

@router.post("/verify-code", response_model=Union[LoginSuccessResponse, LoginFailedResponse])
def verify_code(
    request: VerifyRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        return service.verify_login_and_get_user(email=request.email, code=request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred during verification.")