from typing import List, Optional, Literal, Dict, Any, Tuple
import json
from datetime import datetime
import os
from pathlib import Path
from contextlib import asynccontextmanager
import difflib
import ast
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from dotenv import load_dotenv

import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from deepmcpagent import HTTPServerSpec, FastMCPMulti, MCPToolLoader
from builder import RPAWorkflowBuilder


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
    is_hearing: Optional[bool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await get_pool()
    try:
        yield
    finally:
        pool: asyncpg.Pool = app.state.pool
        await pool.close()


app = FastAPI(title="RPA Backend API", lifespan=lifespan)

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


# startup/shutdown は lifespan へ移行済み


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
def _build_embeddings(model: Optional[str]) -> OpenAIEmbeddings:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return OpenAIEmbeddings(model=model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"), api_key=api_key)


def _to_pgvector_literal(vec: List[float]) -> str:
    # pgvector は '[v1,v2,...]' の文字列表現で受け取れる
    # 文字列で渡すことで asyncpg の型不一致を回避
    return "[" + ",".join(str(float(x)) for x in vec) + "]"



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


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STEP_SCHEMA_DOC = PROJECT_ROOT / "docs" / "ashirobo-step-list-schema.md"
STEP_LIST_PATH = Path(__file__).resolve().parent / "generated_step_list.json"
MCP_MAIN_PATH = PROJECT_ROOT / "rpa-mcp" / "main.py"


MANUAL_CMD_TOOL_MAP: Dict[str, Optional[str]] = {

}

def _normalize_text(value: str) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", value)
    replacements = ["／", "·", "・"]
    for rep in replacements:
        text = text.replace(rep, "")
    for ch in "（）()　 ,:：-_/\\":
        text = text.replace(ch, "")
    return text


@lru_cache(maxsize=1)
def get_step_tool_mappings() -> Tuple[Dict[str, Optional[str]], Dict[str, Dict[str, Any]]]:
    """Return mapping from step command id to MCP tool name (if available)."""

    cmd_nickname_map: Dict[str, str] = {}
    if STEP_LIST_PATH.exists():
        try:
            data = json.loads(STEP_LIST_PATH.read_text(encoding="utf-8"))
            for step in data.get("sequence", []):
                cmd = step.get("cmd")
                nickname = step.get("cmd-nickname")
                if cmd:
                    cmd_nickname_map[cmd] = nickname or ""
        except Exception:
            pass

    # Map commands to categories using documentation
    cmd_category_map: Dict[str, Optional[str]] = {}
    if STEP_SCHEMA_DOC.exists():
        category_letter_map: Dict[str, str] = {}
        try:
            for line in STEP_SCHEMA_DOC.read_text(encoding="utf-8").splitlines():
                section = line.strip()
                header_match = re.match(r"##\s+([A-Z])\.\s+(.+)", section)
                if header_match:
                    letter, title = header_match.groups()
                    category_letter_map[letter] = f"{letter}_" + title
                    continue
                detail_match = re.match(r"####\s+([A-Z])-\d+\s+.+?\s+\(`([^`]+)`\)", section)
                if detail_match:
                    letter, cmd = detail_match.groups()
                    category = category_letter_map.get(letter)
                    cmd_category_map[cmd] = category
        except Exception:
            pass

    # Build tool name candidates from MCP definitions
    category_tool_entries: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if MCP_MAIN_PATH.exists():
        try:
            module_ast = ast.parse(MCP_MAIN_PATH.read_text(encoding="utf-8"))
            for node in module_ast.body:
                if not isinstance(node, ast.FunctionDef):
                    continue
                if not any(
                    isinstance(dec, ast.Call) and getattr(dec.func, "attr", None) == "tool"
                    for dec in getattr(node, "decorator_list", [])
                ):
                    continue
                tool_name = node.name
                category = None
                operation = None
                subcategory = None
                for stmt in ast.walk(node):
                    if not isinstance(stmt, ast.Call):
                        continue
                    func = getattr(stmt, "func", None)
                    if isinstance(func, ast.Name) and func.id in {"create_rpa_step_from_template", "create_rpa_step"}:
                        for kw in stmt.keywords:
                            if kw.arg == "category" and isinstance(kw.value, ast.Constant):
                                category = kw.value.value
                            if kw.arg == "operation" and isinstance(kw.value, ast.Constant):
                                operation = kw.value.value
                            if kw.arg == "subcategory" and isinstance(kw.value, ast.Constant):
                                subcategory = kw.value.value
                        break
                if not category or not operation:
                    continue
                name_candidates = {operation}
                if subcategory:
                    name_candidates.add(f"{subcategory}{operation}")
                category_tool_entries[category].append(
                    {
                        "tool": tool_name,
                        "candidates": list(name_candidates),
                    }
                )
        except Exception:
            pass

    cmd_tool_map: Dict[str, Optional[str]] = {}
    metadata: Dict[str, Dict[str, Any]] = {}
    for cmd, nickname in cmd_nickname_map.items():
        category = cmd_category_map.get(cmd)
        auto_tool = None
        auto_score = 0.0
        auto_name = None
        if category and category_tool_entries.get(category):
            target = _normalize_text(nickname)
            for entry in category_tool_entries[category]:
                for candidate_name in entry["candidates"]:
                    score = difflib.SequenceMatcher(
                        None, target, _normalize_text(candidate_name)
                    ).ratio()
                    if score > auto_score:
                        auto_score = score
                        auto_tool = entry["tool"]
                        auto_name = candidate_name
        manual_value = MANUAL_CMD_TOOL_MAP.get(cmd, ...)
        if manual_value is ...:
            final_tool = auto_tool if auto_tool and auto_score >= 0.6 else None
            source = "auto" if final_tool else "none"
        else:
            final_tool = manual_value
            source = "manual"
        cmd_tool_map[cmd] = final_tool
        metadata[cmd] = {
            "category": category,
            "nickname": nickname,
            "source": source,
            "auto_tool": auto_tool,
            "auto_name": auto_name,
            "auto_score": auto_score,
            "tool": final_tool,
        }

    # Include commands that appear in manual map but not in generated list
    for cmd, manual_value in MANUAL_CMD_TOOL_MAP.items():
        if cmd in cmd_tool_map:
            continue
        cmd_tool_map[cmd] = manual_value
        metadata[cmd] = {
            "category": cmd_category_map.get(cmd),
            "nickname": cmd_nickname_map.get(cmd, ""),
            "source": "manual",
            "auto_tool": None,
            "auto_name": None,
            "auto_score": 0.0,
            "tool": manual_value,
        }

    return cmd_tool_map, metadata


def _safe_json(value: Any) -> Any:
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    try:
        json_str = json.dumps(value, ensure_ascii=False)
        return json.loads(json_str)
    except Exception:
        return repr(value)


def _get_mcp_server_url() -> str:
    return (
        os.getenv("MCP_SERVER_URL")
        or os.getenv("MCP_HTTP_SERVER_URL")
        or "http://localhost:8080/mcp"
    )


def _truncate_text(text: Optional[str], length: int = 160) -> str:
    if not text:
        return ""
    return text if len(text) <= length else text[:length].rstrip() + "…"


async def initialize_filtered_agent(
    tool_names: List[str],
    instructions: str,
    model: ChatOpenAI,
    *,
    trace_tools: bool = True,
) -> Tuple[Any, List[str], List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """Build a DeepMCP agent limited to the specified tool names."""

    server_url = _get_mcp_server_url()
    if not server_url:
        raise HTTPException(status_code=500, detail="MCP server URL is not configured")

    tool_call_log: List[Dict[str, Any]] = []

    def _on_before(name: str, kwargs: Dict[str, Any]) -> None:
        entry = {"tool": name, "input": _safe_json(kwargs), "status": "running"}
        tool_call_log.append(entry)

    def _on_after(name: str, result: Any) -> None:
        if tool_call_log and tool_call_log[-1].get("tool") == name and tool_call_log[-1].get("status") == "running":
            tool_call_log[-1]["status"] = "succeeded"
            tool_call_log[-1]["output"] = _safe_json(result)
        else:
            tool_call_log.append(
                {"tool": name, "status": "succeeded", "output": _safe_json(result)}
            )

    def _on_error(name: str, error: Exception) -> None:
        tool_call_log.append(
            {"tool": name, "status": "error", "error": repr(error)}
        )

    servers = {
        "rpa": HTTPServerSpec(
            url=server_url,
            transport="http",
        )
    }

    loader = MCPToolLoader(
        FastMCPMulti(servers),
        on_before=_on_before if trace_tools else None,
        on_after=_on_after if trace_tools else None,
        on_error=_on_error if trace_tools else None,
    )

    try:
        discovered_tools = await loader.get_all_tools()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load MCP tools: {exc}") from exc

    tool_map = {tool.name: tool for tool in discovered_tools}
    requested_unique: List[str] = []
    seen_names: set[str] = set()
    for name in tool_names:
        if name and name not in seen_names:
            requested_unique.append(name)
            seen_names.add(name)
    available_tool_objects = [tool_map[name] for name in requested_unique if name in tool_map]
    missing_tools = [name for name in requested_unique if name not in tool_map]

    if not available_tool_objects:
        raise HTTPException(
            status_code=422,
            detail="No matching MCP tools are available for the selected candidate steps",
        )

    agent = create_react_agent(
        model=model,
        tools=available_tool_objects,
        state_modifier=instructions,
    )

    tool_info_dicts: List[Dict[str, Any]] = []
    try:
        infos = await loader.list_tool_info()
    except Exception:
        infos = []
    info_map = {info.name: info for info in infos}
    for name in requested_unique:
        info = info_map.get(name)
        if not info:
            continue
        tool_info_dicts.append(
            {
                "name": info.name,
                "description": info.description,
                "input_schema": info.input_schema,
                "server": info.server_guess,
            }
        )

    return (
        agent,
        [tool.name for tool in available_tool_objects],
        tool_info_dicts,
        missing_tools,
        tool_call_log,
    )


def parse_agent_workflow_response(response: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    messages = response.get("messages", []) if isinstance(response, dict) else []
    if not messages:
        raise HTTPException(status_code=500, detail="Agent returned no messages")

    last_message = messages[-1]
    if hasattr(last_message, "content"):
        content = last_message.content
    elif isinstance(last_message, dict):
        content = last_message.get("content", "")
    else:
        content = str(last_message)

    default_workflow = {
        "name": "Generated RPA Workflow",
        "description": "ユーザー要件に基づいて生成されたワークフロー",
        "version": "1.0.0",
        "steps": [],
    }

    try:
        json_pattern = r"```json\s*(.*?)\s*```"
        matches = re.findall(json_pattern, content, re.DOTALL)
        workflow_data: Dict[str, Any]
        if matches:
            workflow_data = json.loads(matches[0])
        else:
            workflow_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Agent response was not valid JSON")

    workflow = {
        "name": workflow_data.get("name", default_workflow["name"]),
        "description": workflow_data.get("description", default_workflow["description"]),
        "version": workflow_data.get("version", "1.0.0"),
        "steps": workflow_data.get("steps", []) or [],
    }
    return workflow, content


def format_workflow_steps(workflow: Dict[str, Any], max_steps: Optional[int] = None) -> Dict[str, Any]:
    steps = workflow.get("steps") or []
    if not isinstance(steps, list):
        steps = []
    if max_steps is not None:
        steps = steps[:max_steps]
    formatted: List[Dict[str, Any]] = []
    for index, step in enumerate(steps, start=1):
        step_dict = dict(step or {})
        step_dict["id"] = f"step-{index:03d}"
        formatted.append(step_dict)
    workflow["steps"] = formatted
    return workflow

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


@app.get("/workflow/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str) -> Workflow:
    pool: asyncpg.Pool = app.state.pool
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


class WorkflowUpdateIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@app.patch("/workflow/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, payload: WorkflowUpdateIn) -> Workflow:
    if payload.name is None and payload.description is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    pool: asyncpg.Pool = app.state.pool
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


class WorkflowGeneratedOut(BaseModel):
    groups: list
    steps: list


class WorkflowBuildRequest(BaseModel):
    user_input: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_steps: Optional[int] = None


@app.get("/workflow/{workflow_id}/generated", response_model=WorkflowGeneratedOut)
async def get_workflow_generated(workflow_id: str) -> WorkflowGeneratedOut:
    # まだワークフローの詳細生成は未実装のため、空配列を返す
    # 将来的には DB や生成結果から返却する
    return WorkflowGeneratedOut(groups=[], steps=[])


class WorkflowSaveIn(BaseModel):
    groups: list
    steps: list


class WorkflowSaveOut(BaseModel):
    scenario_version_id: str
    version: int


@app.post("/workflow/{workflow_id}/save", response_model=WorkflowSaveOut)
async def save_workflow(workflow_id: str, payload: WorkflowSaveIn) -> WorkflowSaveOut:
    # クライアントから受け取った表示中のワークフローをそのまま保存（簡易）
    pool: asyncpg.Pool = app.state.pool
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


@app.get("/workflow/{workflow_id}/latest")
async def get_latest_step_list(workflow_id: str) -> dict:
    pool: asyncpg.Pool = app.state.pool
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

@app.post("/workflow/{workflow_id}/build")
async def build_workflow(workflow_id: str) -> dict:
    pool: asyncpg.Pool = app.state.pool
    async with pool.acquire() as conn:
        # 1) workflow の存在確認 + hearing 終了フラグ更新（将来的な意味合い）
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

        # Step 1 ベクトル検索で 40-50 のステップ定義まで絞り込みを行う
        # 2) ヒアリングメッセージ取得（user/assistant問わず全文）
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
    # - 空行/重複の削除、改行圧縮
    text = "\n".join(dict.fromkeys([c for c in contents if c]))  # preserve order, drop dups
    text = "\n".join([ln.strip() for ln in text.splitlines() if ln.strip()])

    # step1.log: ヒアリング内容を出力
    with open("step1.log", "w", encoding="utf-8") as f:
        f.write("=== ヒアリング内容 (ベクトル化前) ===\n\n")
        f.write(text)
        f.write("\n\n")

    # 4) 埋め込みモデルでベクトル化
    try:
        embedder = _build_embeddings(None)
        embedding = await embedder.aembed_query(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    # 5) ベクトル検索（上位40件）
    # step_embeddings(embedding vector(1536)) に対して cosine 距離で類似検索
    async with pool.acquire() as conn:
        # パラメータは vector 文字列表現で渡す
        emb_literal = _to_pgvector_literal(embedding)
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
    with open("step1.log", "a", encoding="utf-8") as f:
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
    # 1) 正規マッピング（cmd -> MCPツール名）
    # 2) マップに無い場合はフォールバックで step_key 自体も候補に含める
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
    with open("step1.log", "a", encoding="utf-8") as f:
        f.write("=== 許可されたツール名 ===\n\n")
        for i, name in enumerate(allowed_tool_names, 1):
            f.write(f"{i}. {name}\n")
        f.write(f"\n合計: {len(allowed_tool_names)} ツール\n")

    # ビルダーでワークフロー生成（ヒアリング全文を渡す）
    builder = RPAWorkflowBuilder(
        mcp_server_url=_get_mcp_server_url(),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        allowed_tool_names=allowed_tool_names,
    )
    generated_workflow = await builder.build(text)

    return {
        "status": "ok",
        "workflow_id": workflow_id,
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
        "generated": generated_workflow,
    }



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
