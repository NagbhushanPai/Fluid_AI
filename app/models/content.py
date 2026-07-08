from typing import Literal

from pydantic import BaseModel, Field

from app.core.exceptions import BudgetValidationError


class Assumption(BaseModel):
    field: str
    value: str
    rationale: str


class TimelinePhase(BaseModel):
    phase: str
    duration: str
    activities: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)


class BudgetItem(BaseModel):
    category: str
    amount: float
    rationale: str


class BudgetPlan(BaseModel):
    currency: str = "USD"
    items: list[BudgetItem] = Field(default_factory=list)
    total: float = 0.0

    def validate_total(self) -> None:
        calculated_total = round(sum(item.amount for item in self.items), 2)
        if round(self.total, 2) != calculated_total:
            raise BudgetValidationError("Budget items do not match total.")


class Risk(BaseModel):
    risk: str
    probability: Literal["Low", "Medium", "High"]
    impact: Literal["Low", "Medium", "High"]
    mitigation: str


class DocumentContent(BaseModel):
    title: str
    executive_summary: str
    objectives: list[str] = Field(default_factory=list)
    scope: list[str] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    timeline: list[TimelinePhase] = Field(default_factory=list)
    budget: list[BudgetItem] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    conclusion: str = ""
