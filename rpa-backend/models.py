"""Pydantic models for API schemas."""
from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel


# Workflow models
class WorkflowIn(BaseModel):
    name: str
    description: Optional[str] = None


class Workflow(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    last_run_at: Optional[datetime] = None
    is_hearing: Optional[bool] = None


class WorkflowUpdateIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkflowSaveIn(BaseModel):
    groups: list
    steps: list


class WorkflowSaveOut(BaseModel):
    scenario_version_id: str
    version: int


class WorkflowBuildRequest(BaseModel):
    allowed_tool_names: List[str]
    hearing_text: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_steps: Optional[int] = None


# AI Chat models
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


# Message models
class MessageOut(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

