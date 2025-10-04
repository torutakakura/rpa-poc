"""FastAPI dependencies."""
from typing import Annotated
import asyncpg
from fastapi import Depends, Request


def get_pool(request: Request) -> asyncpg.Pool:
    """Get database pool from app state."""
    return request.app.state.pool


# Type alias for dependency injection
PoolDep = Annotated[asyncpg.Pool, Depends(get_pool)]

