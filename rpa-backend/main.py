"""Main FastAPI application entry point."""
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from utils.db import get_pool
from router import chat, workflows, messages, workflow_build


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    app.state.pool = await get_pool()
    try:
        yield
    finally:
        pool: asyncpg.Pool = app.state.pool
        await pool.close()


app = FastAPI(title="RPA Backend API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat.router)
app.include_router(workflows.router)
app.include_router(messages.router)
app.include_router(workflow_build.router)


@app.get("/")
async def root() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
