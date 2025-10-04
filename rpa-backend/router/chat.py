"""AI chat endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from models import AIChatRequest, AIChatResponse
from prompts import SYSTEM_PROMPT
from utils.llm import build_llm, generate_summary_from_messages
from dependencies import PoolDep

router = APIRouter(prefix="/ai-chat", tags=["chat"])


@router.post("", response_model=AIChatResponse)
async def ai_chat(req: AIChatRequest, pool: PoolDep) -> AIChatResponse:
    """初回のAIチャット（新規ワークフロー作成）"""
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages is required")

    llm = build_llm(req.model, req.temperature)

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


@router.post("/{workflow_id}", response_model=AIChatResponse)
async def ai_chat_append(workflow_id: str, req: AIChatRequest, pool: PoolDep) -> AIChatResponse:
    """2回目以降のAIチャット（既存ワークフローへの追加）"""
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages is required")

    llm = build_llm(req.model, req.temperature)

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

