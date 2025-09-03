from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings, logger
from routers.bu_router import router as bu_router
from routers.auth_router import router as auth_router
from routers.admin_router import router as admin_router
from routers.log_router import router as log_router
from database import initialize_pool, close_pool
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException

# --- Application Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application and initializing database pool.")
    try:
        initialize_pool()
        yield
    finally:
        logger.info("Shutting down application and closing database pool.")
        close_pool()

# --- App Instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API to handle monthly business unit reporting.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
if settings.ALLOWED_ORIGINS and settings.ALLOWED_ORIGINS != ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
else:
    logger.warning("CORS is set to allow all origins. This is insecure for production!")

# --- Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# --- Routers ---
app.include_router(bu_router, prefix=settings.API_V1_PREFIX, tags=["Reporting"])
app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(log_router, prefix=settings.API_V1_PREFIX, tags=["Logging"])

# --- Health Check Endpoint ---
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/", tags=["Root"])
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}."}
