"""LLM and embeddings utilities."""
from typing import Optional, List
from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL, OPENAI_SUMMARY_MODEL
from prompts import SUMMARY_SYSTEM_PROMPT
from models import AIChatMessage


def build_llm(model: Optional[str], temperature: Optional[float]) -> ChatOpenAI:
    """Build and return a ChatOpenAI instance."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return ChatOpenAI(
        model=model or OPENAI_MODEL,
        temperature=temperature if temperature is not None else 0.2,
        api_key=OPENAI_API_KEY,
    )


def build_embeddings(model: Optional[str]) -> OpenAIEmbeddings:
    """Build and return an OpenAIEmbeddings instance."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return OpenAIEmbeddings(
        model=model or OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )


def to_pgvector_literal(vec: List[float]) -> str:
    """Convert a vector to pgvector literal format."""
    return "[" + ",".join(str(float(x)) for x in vec) + "]"


async def generate_summary_from_messages(
    messages: List[AIChatMessage], model_hint: Optional[str]
) -> str:
    """Generate a summary from chat messages."""
    llm = build_llm(OPENAI_SUMMARY_MODEL or model_hint or OPENAI_MODEL, 0.0)
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

