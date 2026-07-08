from typing import Any

from pydantic import BaseModel, Field

from app.models.task import Task


class ExecutionRecord(BaseModel):
    task_id: str
    status: str
    duration_ms: int
    tool: str
    result_preview: str | None = None


class AgentResponse(BaseModel):
    status: str
    request_id: str
    plan: list[Task]
    assumptions: list[dict[str, Any]]
    execution: list[ExecutionRecord]
    quality_score: float
    revisions: int = 0
    document_url: str
    execution_summary: str = Field(default="")

