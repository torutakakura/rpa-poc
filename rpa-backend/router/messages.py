"""Message history endpoints."""
from typing import List
from fastapi import APIRouter

from models import MessageOut
from dependencies import PoolDep

router = APIRouter(tags=["messages"])


@router.get("/workflows/{workflow_id}/messages", response_model=List[MessageOut])
async def list_messages(workflow_id: str, pool: PoolDep) -> List[MessageOut]:
    """指定されたワークフローのメッセージ履歴を取得"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select role, content, created_at
            from messages
            where workflow_id = $1
            order by created_at asc
            """,
            workflow_id,
        )
        return [MessageOut(**dict(row)) for row in rows]

