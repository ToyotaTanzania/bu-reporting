from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routers.bu_router import router as bu_router
from routers.auth_router import router as auth_router
from routers.admin_router import router as admin_router
from database import initialize_pool, close_pool

# --- Application Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup:
    initialize_pool()
    yield
    # On shutdown:
    close_pool()

# --- App Instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API to handle monthly business unit reporting.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Routers ---
app.include_router(bu_router, prefix=settings.API_V1_PREFIX, tags=["Reporting"])
app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Administration"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}."}