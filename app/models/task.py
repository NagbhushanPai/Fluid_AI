from typing import Any, Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["pending", "running", "completed", "failed"]


class Task(BaseModel):
    id: str
    description: str
    tool: str
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = "pending"
    result: Any | None = None

