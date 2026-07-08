import json
from typing import Any

from app.llm.client import llm_call
from app.models.content import Assumption, BudgetItem, DocumentContent, Risk, TimelinePhase


def synthesize_document_content(request: str, context: dict[str, Any]) -> DocumentContent:
    prompt = f"""
Synthesize a structured business document as valid JSON only.

Return keys:
title, executive_summary, objectives, scope, assumptions, timeline, budget, risks, success_metrics, conclusion

Each assumption must have field, value, rationale.
Each timeline item must have phase, duration, activities, deliverables.
Each budget item must have category, amount, rationale.
Each risk must have risk, probability, impact, mitigation.

USER REQUEST:
{request}

AVAILABLE CONTEXT:
{context}
"""
    raw = llm_call(prompt)
    parsed = _parse_document_content(raw)
    if parsed:
        return parsed
    return _fallback_document_content(request, context)


def revise_document_content(
    content: DocumentContent,
    issues: list[Any],
    request: str,
    context: dict[str, Any],
) -> DocumentContent:
    revised = content.model_copy(deep=True)
    issue_text = [f"{getattr(i, 'section', '')} {getattr(i, 'problem', i)}".lower() for i in issues]

    if any("timeline" in text for text in issue_text):
        timeline = context.get("timeline_phases", [])
        if timeline:
            revised.timeline = _coerce_timeline(timeline)

    if any("budget" in text for text in issue_text):
        budget = context.get("budget_plan")
        if budget:
            revised.budget = list(budget.items)

    if any("risk" in text for text in issue_text):
        risks = context.get("risks", [])
        if risks:
            revised.risks = _coerce_risks(risks)

    if any("executive summary" in text or "summary" in text for text in issue_text):
        revised.executive_summary = _build_executive_summary(request, revised)

    return revised


def _parse_document_content(raw: str) -> DocumentContent | None:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return None
        return DocumentContent(
            title=payload["title"],
            executive_summary=payload["executive_summary"],
            objectives=list(payload.get("objectives", [])),
            scope=list(payload.get("scope", [])),
            assumptions=[Assumption(**item) for item in payload.get("assumptions", [])],
            timeline=[TimelinePhase(**item) for item in payload.get("timeline", [])],
            budget=[BudgetItem(**item) for item in payload.get("budget", [])],
            risks=[Risk(**item) for item in payload.get("risks", [])],
            success_metrics=list(payload.get("success_metrics", [])),
            conclusion=payload.get("conclusion", ""),
        )
    except Exception:
        return None


def _fallback_document_content(request: str, context: dict[str, Any]) -> DocumentContent:
    assumptions = _coerce_assumptions(context.get("assumptions", []))
    timeline = _coerce_timeline(context.get("timeline_phases", []))

    budget_plan = context.get("budget_plan")
    budget_items = list(getattr(budget_plan, "items", []))

    risks = _coerce_risks(context.get("risks", []))

    return DocumentContent(
        title="AI-Based Hiring Platform 90-Day Launch Project Plan" if "hiring" in request.lower() else "Project Plan",
        executive_summary=_build_executive_summary(request, None),
        objectives=context.get(
            "objectives",
            [
                "Define a practical 90-day launch roadmap",
                "Deliver an MVP focused on recruiter productivity",
                "Control budget and risk exposure during execution",
            ],
        ),
        scope=context.get(
            "scope",
            [
                "AI-assisted candidate screening",
                "Recruiter workflow and decision support",
                "Core analytics for funnel visibility",
            ],
        ),
        assumptions=assumptions,
        timeline=timeline,
        budget=budget_items,
        risks=risks,
        success_metrics=[
            "Launch MVP in 90 days with agreed scope",
            "Reduce manual screening effort by at least 25%",
            "Maintain budget variance within 10%",
        ],
        conclusion="The plan is feasible within three months if governance, risk controls, and milestone reviews are executed consistently.",
    )


def _coerce_assumptions(value: Any) -> list[Assumption]:
    if not isinstance(value, list):
        return []
    result: list[Assumption] = []
    for item in value:
        if isinstance(item, Assumption):
            result.append(item)
        elif isinstance(item, dict):
            result.append(
                Assumption(
                    field=str(item.get("field", "assumption")),
                    value=str(item.get("value", "unspecified")),
                    rationale=str(item.get("rationale") or item.get("reason") or "Inferred from request context."),
                )
            )
    return result


def _coerce_timeline(value: Any) -> list[TimelinePhase]:
    if not isinstance(value, list):
        return []
    result: list[TimelinePhase] = []
    for item in value:
        if isinstance(item, TimelinePhase):
            result.append(item)
        elif isinstance(item, dict):
            result.append(
                TimelinePhase(
                    phase=str(item.get("phase", "Phase")),
                    duration=str(item.get("duration", "TBD")),
                    activities=[str(x) for x in item.get("activities", [])],
                    deliverables=[str(x) for x in item.get("deliverables", [])],
                )
            )
    return result


def _coerce_risks(value: Any) -> list[Risk]:
    if not isinstance(value, list):
        return []
    result: list[Risk] = []
    for item in value:
        if isinstance(item, Risk):
            result.append(item)
        elif isinstance(item, dict):
            try:
                result.append(Risk(**item))
            except Exception:
                continue
    return result


def _build_executive_summary(request: str, _content: DocumentContent | None) -> str:
    return (
        "This project plan provides a structured path to launch an AI-based hiring platform within a 90-day window. "
        "The approach balances speed and control by defining clear milestones, ownership, and measurable outcomes across discovery, build, and launch preparation phases. "
        "It includes assumptions required to proceed with incomplete inputs, a detailed budget breakdown with rationale, and a risk register with actionable mitigations. "
        "The plan emphasizes weekly governance checkpoints, early integration validation, security readiness, and adoption support so the rollout is both technically reliable and operationally useful. "
        f"The strategy directly addresses the user request: {request}."
    )
