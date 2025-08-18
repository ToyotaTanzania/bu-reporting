from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services import auth_service as service
from database import get_db
import pymssql


class LoginRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    code: str

router = APIRouter()

@router.post("/request-code")
def request_code(request: LoginRequest, db: pymssql.Connection = Depends(get_db)):
    try:
        return service.request_login_code(db=db, email=request.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@router.post("/verify-code")
def verify_code(request: VerifyRequest, db: pymssql.Connection = Depends(get_db)):
    try:
        return service.verify_login_and_get_user(db=db, email=request.email, code=request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")