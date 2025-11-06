from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import admin, ai, auth, chapters, characters, novels, plots, prompts, users, worlds, chapter_versions, ai_assistants
from .core.config import settings
from .core.database import Base, engine
from .core.logger import logger
from .core.database import SessionLocal
from .core.security import hash_password
try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from .core.rate_limit import limiter as _real_limiter
    _RATE_LIMIT_ENABLED = True
except Exception as _e:  # noqa: N816
    # Gracefully handle environments where slowapi or its deps are missing
    _RATE_LIMIT_ENABLED = False
    _real_limiter = None

    class _DummyLimiter:
        def limit(self, *_args, **_kwargs):
            def _decorator(func):
                return func

            return _decorator

    # Fallback limiter to keep routes working
    limiter = _DummyLimiter()
else:
    limiter = _real_limiter

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    try:
        # Development bootstrap: ensure an admin exists for first-time login
        if settings.DEBUG:
            try:
                from .models.admin import Admin  # local import to avoid circulars
                with SessionLocal() as db:
                    count = db.query(Admin).count()
                    if count == 0:
                        logger.info("No admin accounts found. Creating default admin for development use.")
                        admin = Admin(
                            username=getattr(settings, "ADMIN_DEFAULT_USERNAME", "admin"),
                            email=f"{getattr(settings, 'ADMIN_DEFAULT_USERNAME', 'admin')}@example.com",
                            full_name="Dev Admin",
                            hashed_password=hash_password(getattr(settings, "ADMIN_DEFAULT_PASSWORD", "admin123")),
                            is_active=True,
                            is_superuser=True,
                        )
                        db.add(admin)
                        db.commit()
                        logger.info("Default admin created. You can log in via /admin/login.")
            except Exception as _exc:  # noqa: BLE001
                logger.warning(f"Admin bootstrap skipped/failed: {_exc}")
        yield
    finally:
        logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="AI-powered novel writing platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter if available
if _RATE_LIMIT_ENABLED:
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

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prompts.router)
app.include_router(novels.router)
app.include_router(characters.router)
app.include_router(worlds.router)
app.include_router(plots.router)
app.include_router(chapters.router)
app.include_router(chapter_versions.router)
app.include_router(ai.router)
app.include_router(ai_assistants.router)
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
