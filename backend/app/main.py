from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .api import admin, ai, chapters, characters, novels, plots, worlds
from .core.config import settings
from .core.database import Base, engine
from .core.logger import logger
from .core.rate_limit import limiter

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="AI-powered novel writing platform",
    version="1.0.0",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

app.include_router(novels.router)
app.include_router(characters.router)
app.include_router(worlds.router)
app.include_router(plots.router)
app.include_router(chapters.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {
        "message": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME
    }


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")
