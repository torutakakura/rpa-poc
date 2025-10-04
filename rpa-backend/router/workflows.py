"""Workflow CRUD endpoints."""
from typing import List
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException

from models import (
    Workflow,
    WorkflowIn,
    WorkflowUpdateIn,
    WorkflowSaveIn,
    WorkflowSaveOut,
)
from dependencies import PoolDep

router = APIRouter(tags=["workflows"])


@router.get("/workflows", response_model=List[Workflow])
async def list_workflows(pool: PoolDep) -> List[Workflow]:
    """全ワークフローのリストを取得"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select
              w.id::text as id,
              w.name,
              w.description,
              w.is_hearing,
              (
                select max(coalesce(r.finished_at, r.started_at))
                from scenario_versions sv
                join runs r on r.scenario_version_id = sv.id
                where sv.scenario_id = w.id
              ) as last_run_at
            from workflows w
            where w.deleted_at is null
            order by w.created_at desc
            """
        )
        return [Workflow(**dict(row)) for row in rows]


@router.get("/workflow/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str, pool: PoolDep) -> Workflow:
    """指定されたワークフローの詳細を取得"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            select
              w.id::text as id,
              w.name,
              w.description,
              w.is_hearing,
              (
                select max(coalesce(r.finished_at, r.started_at))
                from scenario_versions sv
                join runs r on r.scenario_version_id = sv.id
                where sv.scenario_id = w.id
              ) as last_run_at
            from workflows w
            where w.id = $1 and w.deleted_at is null
            """,
            workflow_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return Workflow(**dict(row))


@router.post("/workflows", response_model=Workflow, status_code=201)
async def create_workflow(payload: WorkflowIn, pool: PoolDep) -> Workflow:
    """新規ワークフローを作成"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            insert into workflows (name, description)
            values ($1, $2)
            returning id::text, name, description
            """,
            payload.name,
            payload.description,
        )
        if row is None:
            raise HTTPException(status_code=500, detail="Failed to create workflow")
        return Workflow(**dict(row))


@router.patch("/workflow/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, payload: WorkflowUpdateIn, pool: PoolDep) -> Workflow:
    """ワークフローを更新"""
    if payload.name is None and payload.description is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            update workflows
            set
              name = coalesce($2, name),
              description = coalesce($3, description),
              updated_at = now()
            where id = $1 and deleted_at is null
            """,
            workflow_id,
            payload.name,
            payload.description,
        )
        if not result.endswith(" 1"):
            raise HTTPException(status_code=404, detail="Workflow not found")

        row = await conn.fetchrow(
            """
            select
              w.id::text as id,
              w.name,
              w.description,
              w.is_hearing,
              (
                select max(coalesce(r.finished_at, r.started_at))
                from scenario_versions sv
                join runs r on r.scenario_version_id = sv.id
                where sv.scenario_id = w.id
              ) as last_run_at
            from workflows w
            where w.id = $1 and w.deleted_at is null
            """,
            workflow_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return Workflow(**dict(row))


@router.delete("/workflows/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str, pool: PoolDep) -> None:
    """ワークフローを削除（論理削除）"""
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            update workflows
            set deleted_at = now()
            where id = $1 and deleted_at is null
            """,
            workflow_id,
        )
        # result is like 'UPDATE 1'
        if not result.endswith(" 1"):
            raise HTTPException(status_code=404, detail="Workflow not found or already deleted")


@router.post("/workflow/{workflow_id}/save", response_model=WorkflowSaveOut)
async def save_workflow(workflow_id: str, payload: WorkflowSaveIn, pool: PoolDep) -> WorkflowSaveOut:
    """ワークフローを保存"""
    # クライアントから受け取った表示中のワークフローをそのまま保存（簡易）
    async with pool.acquire() as conn:
        # workflow の存在確認
        row = await conn.fetchrow(
            """
            select id from workflows where id = $1 and deleted_at is null
            """,
            workflow_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # 次バージョンを採番
        row_ver = await conn.fetchrow(
            """
            select coalesce(max(version), 0) + 1 as next_version
            from scenario_versions
            where scenario_id = $1
            """,
            workflow_id,
        )
        next_version: int = int(row_ver[0])

        # 保存
        row_sv = await conn.fetchrow(
            """
            insert into scenario_versions (scenario_id, version, steps_json)
            values ($1, $2, $3::jsonb)
            returning id::text as id, version
            """,
            workflow_id,
            next_version,
            json.dumps({"groups": payload.groups, "steps": payload.steps}, ensure_ascii=False),
        )
        return WorkflowSaveOut(scenario_version_id=row_sv[0], version=row_sv[1])


@router.get("/workflow/{workflow_id}/latest")
async def get_latest_step_list(workflow_id: str, pool: PoolDep) -> dict:
    """最新のステップリストを取得"""
    async with pool.acquire() as conn:
        # workflow meta
        wf = await conn.fetchrow(
            """
            select id::text as id, name, description
            from workflows
            where id = $1 and deleted_at is null
            """,
            workflow_id,
        )
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # latest scenario version
        row = await conn.fetchrow(
            """
            select version, steps_json
            from scenario_versions
            where scenario_id = $1
            order by version desc
            limit 1
            """,
            workflow_id,
        )

        version = str(row[0]) if row is not None else "0"
        steps_json = row[1] if row is not None else {"steps": [], "groups": []}
        # steps_json が文字列で返る環境に備えてデコード
        if isinstance(steps_json, str):
            try:
                steps_json = json.loads(steps_json)
            except Exception:
                steps_json = {"steps": [], "groups": []}
        steps = steps_json.get("steps") if isinstance(steps_json, dict) else []

        # map saved steps -> sequence (generated_step_list-ish)
        sequence: list[dict] = []
        for s in steps or []:
            step_type = s.get("type", "action")
            cmd_type = "branching" if step_type == "condition" else "basic"
            sequence.append({
                "uuid": s.get("id"),
                "cmd": step_type,
                "cmd-nickname": s.get("title") or step_type,
                "cmd-type": cmd_type,
                "description": s.get("description", ""),
            })

        # response similar to generated_step_list.json
        # フロントエンドが期待する形式に合わせる
        return {
            "version": version,
            "uuid": wf["id"],
            "name": wf["name"] or "",
            "description": wf["description"] or "",
            "timestamp-last-modified": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
            "flags": {},
            "sequence": sequence,
            # フロントエンドが期待する generated フィールドも追加
            "generated": {
                "name": wf["name"] or "",
                "description": wf["description"] or "",
                "version": version,
                "steps": steps if steps else []
            }
        }

