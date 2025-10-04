"""Workflow build and search endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException

from models import WorkflowBuildRequest
from utils.llm import build_embeddings, to_pgvector_literal
from utils.mcp import get_step_tool_mappings
from builder import RPAWorkflowBuilder
from config import MCP_SERVER_URL, OPENAI_MODEL, STEP1_LOG_PATH
from dependencies import PoolDep

router = APIRouter(tags=["workflow-build"])


@router.get("/workflow/{workflow_id}/search")
async def search_workflow_steps(workflow_id: str, pool: PoolDep) -> dict:
    """
    ステップ1: ヒアリング内容からベクトル類似度検索で候補ステップを40件取得
    """
    async with pool.acquire() as conn:
        # 1) workflow の存在確認
        row = await conn.fetchrow(
            """
            select id from workflows where id = $1 and deleted_at is null
            """,
            workflow_id,
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # 2) ヒアリングメッセージ取得
        rows = await conn.fetch(
            """
            select role, content
            from messages
            where workflow_id = $1 and deleted_at is null
            order by created_at asc
            """,
            workflow_id,
        )
        contents: list[str] = [str(r["content"]).strip() for r in rows if r and r["content"]]

    # 3) クレンジング＆結合
    text = "\n".join(dict.fromkeys([c for c in contents if c]))
    text = "\n".join([ln.strip() for ln in text.splitlines() if ln.strip()])

    # step1.log: ヒアリング内容を出力
    with open(STEP1_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("=== ヒアリング内容 (ベクトル化前) ===\n\n")
        f.write(text)
        f.write("\n\n")

    # 4) 埋め込みモデルでベクトル化
    try:
        embedder = build_embeddings(None)
        embedding = await embedder.aembed_query(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    # 5) ベクトル検索（上位40件）
    async with pool.acquire() as conn:
        emb_literal = to_pgvector_literal(embedding)
        candidates = await conn.fetch(
            """
            select
              id::text as id,
              step_key,
              title,
              description,
              metadata,
              1 - (embedding <=> $1::vector) as similarity
            from step_embeddings
            order by embedding <=> $1::vector asc
            limit 40
            """,
            emb_literal,
        )

    # step1.log: 絞り込み結果40件を追記
    with open(STEP1_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=== ベクトル検索結果 (上位40件) ===\n\n")
        for i, c in enumerate(candidates, 1):
            f.write(f"{i}. step_key: {c['step_key']}\n")
            f.write(f"   title: {c['title']}\n")
            f.write(f"   description: {c['description']}\n")
            f.write(f"   similarity: {c['similarity']:.4f}\n")
            f.write(f"   metadata: {c['metadata']}\n")
            f.write("\n")
        f.write("\n")

    # 候補40件から許可ツール名を抽出
    cmd_tool_map, _meta = get_step_tool_mappings()
    allowed_tool_names: List[str] = []
    _seen: set[str] = set()
    for c in candidates:
        step_key = c["step_key"]
        preferred = cmd_tool_map.get(step_key)
        for name in (preferred, step_key):
            if name and name not in _seen:
                _seen.add(name)
                allowed_tool_names.append(name)

    # step1.log: 許可されたツール名を追記
    with open(STEP1_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=== 許可されたツール名 ===\n\n")
        for i, name in enumerate(allowed_tool_names, 1):
            f.write(f"{i}. {name}\n")
        f.write(f"\n合計: {len(allowed_tool_names)} ツール\n")

    return {
        "status": "ok",
        "workflow_id": workflow_id,
        "hearing_text": text,
        "candidates": [
            {
                "id": str(c["id"]),
                "step_key": c["step_key"],
                "title": c["title"],
                "description": c["description"],
                "metadata": c["metadata"],
                "similarity": float(c["similarity"]) if c["similarity"] is not None else None,
            }
            for c in candidates
        ],
        "allowed_tool_names": allowed_tool_names,
    }


@router.post("/workflow/{workflow_id}/build")
async def build_workflow(workflow_id: str, payload: WorkflowBuildRequest, pool: PoolDep) -> dict:
    """
    ステップ2: 検索結果をもとにMCPエージェントでワークフローを生成
    前提: クライアントが先に /search を呼び出して、その結果を渡す
    """
    # デバッグ：リクエスト内容をログ出力
    print(f"[DEBUG] build_workflow called with workflow_id={workflow_id}")
    print(f"[DEBUG] payload.allowed_tool_names: {len(payload.allowed_tool_names)} items")
    print(f"[DEBUG] payload.hearing_text: {payload.hearing_text[:100] if payload.hearing_text else 'None'}...")
    
    # hearing更新
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            update workflows
            set is_hearing = false, updated_at = now()
            where id = $1 and deleted_at is null
            """,
            workflow_id,
        )
        if not result.endswith(" 1"):
            raise HTTPException(status_code=404, detail="Workflow not found")
    
    # ヒアリング内容: payload から取得、なければDBから取得
    hearing_text = payload.hearing_text
    if not hearing_text:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                select role, content
                from messages
                where workflow_id = $1 and deleted_at is null
                order by created_at asc
                """,
                workflow_id,
            )
            contents: list[str] = [str(r["content"]).strip() for r in rows if r and r["content"]]
        hearing_text = "\n".join(dict.fromkeys([c for c in contents if c]))
        hearing_text = "\n".join([ln.strip() for ln in hearing_text.splitlines() if ln.strip()])
    
    # ビルダーでワークフロー生成
    builder = RPAWorkflowBuilder(
        mcp_server_url=MCP_SERVER_URL,
        model_name=payload.model or OPENAI_MODEL,
        allowed_tool_names=payload.allowed_tool_names,
    )
    generated_workflow = await builder.build(hearing_text)

    return {
        "status": "ok",
        "workflow_id": workflow_id,
        "generated": generated_workflow,
    }

