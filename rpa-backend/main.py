from typing import List, Optional, Literal
from datetime import datetime
import os
from dotenv import load_dotenv

import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser


# Load .env file if present
load_dotenv()

# Environment variables for DB connection
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "55432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "rpa")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rpa_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rpa")


class WorkflowIn(BaseModel):
    name: str
    description: Optional[str] = None


class Workflow(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    last_run_at: Optional[datetime] = None


app = FastAPI(title="RPA Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        min_size=1,
        max_size=10,
    )


@app.on_event("startup")
async def startup_event() -> None:
    app.state.pool = await get_pool()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    pool: asyncpg.Pool = app.state.pool
    await pool.close()


# ========= AI Chat =========

class AIChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AIChatRequest(BaseModel):
    messages: List[AIChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    workflow_id: Optional[str] = None


class AIChatResponse(BaseModel):
    reply: str
    workflow_id: Optional[str] = None


def _build_llm(model: Optional[str], temperature: Optional[float]) -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return ChatOpenAI(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature if temperature is not None else 0.2,
        api_key=api_key,
    )


SYSTEM_PROMPT = (
    """
あなたはRPA設計のエキスパートです。ユーザと対話しながら、RPAで自動化する業務フローを明確化します。
目的は、後でワークフローを作成できるだけの情報（入力/出力、トリガー、前提、例外時の扱い、使用アプリ、操作粒度など）を漏れなくヒアリングすることです。
一度に質問を詰め込みすぎず、要点を段階的に確認してください。回答が曖昧な場合は具体例を提示して再確認します。
最終的に十分な情報が揃ったと判断したら、ユーザに「ワークフロー詳細を作成」ボタンを押すよう促しても構いません。
"""
).strip()


# Summary generation (separate prompt from hearing)
SUMMARY_SYSTEM_PROMPT = (
    """
あなたはプロダクトマネージャーです。以下の会話履歴から、作成予定のRPAワークフローの目的を日本語で簡潔に要約してください。
出力要件:
- 20文字程度
- 記号や句読点は不要
- 固有名詞は一般化
出力は要約文のみ
"""
).strip()


async def generate_summary_from_messages(
    messages: List["AIChatMessage"], model_hint: Optional[str]
) -> str:
    llm = _build_llm(os.getenv("OPENAI_SUMMARY_MODEL", model_hint or os.getenv("OPENAI_MODEL", "gpt-4o-mini")), 0.0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SUMMARY_SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "要約を1行で出力してください")
        ]
    )
    history: List[HumanMessage | AIMessage | SystemMessage] = []
    for m in messages:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            history.append(AIMessage(content=m.content))
        else:
            history.append(SystemMessage(content=m.content))
    chain = prompt | llm | StrOutputParser()
    return await chain.ainvoke({"history": history})


@app.post("/ai-chat", response_model=AIChatResponse)
async def ai_chat(req: AIChatRequest) -> AIChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages is required")

    llm = _build_llm(req.model, req.temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ]
    )

    # build history except last user input
    history: List[HumanMessage | AIMessage | SystemMessage] = []
    for m in req.messages[:-1]:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            history.append(AIMessage(content=m.content))
        else:
            history.append(SystemMessage(content=m.content))

    last_input = req.messages[-1].content

    chain = prompt | llm | StrOutputParser()
    reply = await chain.ainvoke({"history": history, "input": last_input})

    # Persist: if workflow_idが無ければ最初の呼び出しとしてworkflowを作成し、
    # 常にmessagesへ user/assistant を保存
    pool: asyncpg.Pool = app.state.pool
    async with pool.acquire() as conn:
        workflow_id = req.workflow_id
        if not workflow_id:
            # 初回: 会話から要約を作り、workflowsを新規作成
            try:
                summary = (await generate_summary_from_messages(req.messages, req.model)).strip()
                if len(summary) > 120:
                    summary = summary[:120]
            except Exception:
                source_text = next((m.content for m in req.messages if m.role == "user"), last_input)
                summary = (source_text or "新規ワークフロー").strip()[:120]
            row_wf = await conn.fetchrow(
                """
                insert into workflows (name, description, is_hearing)
                values ($1, $2, true)
                returning id::text
                """,
                summary,
                None,
            )
            workflow_id = row_wf[0]

        # メッセージ保存（user → assistant）
        await conn.execute(
            """
            insert into messages (workflow_id, role, content)
            values ($1, 'user', $2)
            """,
            workflow_id,
            last_input,
        )
        await conn.execute(
            """
            insert into messages (workflow_id, role, content)
            values ($1, 'assistant', $2)
            """,
            workflow_id,
            reply,
        )

    return AIChatResponse(reply=reply, workflow_id=workflow_id)


@app.post("/ai-chat/{workflow_id}", response_model=AIChatResponse)
async def ai_chat_append(workflow_id: str, req: AIChatRequest) -> AIChatResponse:
    # 2回目以降: 指定workflowに対し、messagesを追加
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages is required")

    llm = _build_llm(req.model, req.temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ]
    )

    history: List[HumanMessage | AIMessage | SystemMessage] = []
    for m in req.messages[:-1]:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            history.append(AIMessage(content=m.content))
        else:
            history.append(SystemMessage(content=m.content))

    last_input = req.messages[-1].content
    chain = prompt | llm | StrOutputParser()
    reply = await chain.ainvoke({"history": history, "input": last_input})

    pool: asyncpg.Pool = app.state.pool
    async with pool.acquire() as conn:
        # 追加保存
        await conn.execute(
            """
            insert into messages (workflow_id, role, content)
            values ($1, 'user', $2)
            """,
            workflow_id,
            last_input,
        )
        await conn.execute(
            """
            insert into messages (workflow_id, role, content)
            values ($1, 'assistant', $2)
            """,
            workflow_id,
            reply,
        )

    return AIChatResponse(reply=reply, workflow_id=workflow_id)


# ========= Messages history =========

class MessageOut(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


@app.get("/workflows/{workflow_id}/messages", response_model=List[MessageOut])
async def list_messages(workflow_id: str) -> List[MessageOut]:
    pool: asyncpg.Pool = app.state.pool
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


@app.get("/workflows", response_model=List[Workflow])
async def list_workflows() -> List[Workflow]:
    pool: asyncpg.Pool = app.state.pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select
              w.id::text as id,
              w.name,
              w.description,
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


@app.post("/workflows", response_model=Workflow, status_code=201)
async def create_workflow(payload: WorkflowIn) -> Workflow:
    pool: asyncpg.Pool = app.state.pool
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


@app.delete("/workflows/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str) -> None:
    pool: asyncpg.Pool = app.state.pool
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


@app.get("/")
async def root() -> dict:
    return {"status": "ok"}
