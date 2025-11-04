from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import ai, chapters, characters, novels, plots, worlds
from .core.config import settings
from .core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(novels.router)
app.include_router(characters.router)
app.include_router(worlds.router)
app.include_router(plots.router)
app.include_router(chapters.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {"message": settings.APP_NAME}


@app.get("/health")
async def health():
    return {"status": "healthy"}
