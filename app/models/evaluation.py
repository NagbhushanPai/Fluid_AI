from typing import Literal

from pydantic import BaseModel, Field


class EvaluationIssue(BaseModel):
    section: str
    problem: str
    severity: Literal["low", "medium", "high"]
    suggested_fix: str


class EvaluationResult(BaseModel):
    requirement_coverage: float
    content_depth: float
    clarity: float
    consistency: float
    professional_quality: float
    issues: list[EvaluationIssue] = Field(default_factory=list)
    passed: bool = False
    average_score: float = 0.0
