from fastapi import APIRouter, Depends, HTTPException
import pymssql

from services.auth_service import AuthService
from exceptions import EmailNotFoundError, InvalidLoginCodeError
from database import get_db
from typing import Union
from schemas import LoginRequest, VerifyRequest, LoginSuccessResponse, LoginFailedResponse

router = APIRouter()

def get_auth_service(db: pymssql.Connection = Depends(get_db)) -> AuthService:
    return AuthService(db=db)

@router.post("/request-code")
async def request_code(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        return await service.request_login_code(email=request.email)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except pymssql.Error as e:
        raise HTTPException(status_code=500, detail="A database error occurred while requesting the login code.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred while requesting the login code.")

@router.post("/verify-code", response_model=Union[LoginSuccessResponse, LoginFailedResponse])
async def verify_code(
    request: VerifyRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        return await service.verify_login_and_get_user(email=request.email, code=request.code)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidLoginCodeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except pymssql.Error as e:
        raise HTTPException(status_code=500, detail="A database error occurred during verification.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred during verification.")