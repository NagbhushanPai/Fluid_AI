import json
from typing import Any

from app.llm.client import llm_call
from app.models.content import Risk


def analyze_risks(user_request: str, context: dict[str, Any]) -> list[Risk]:
    prompt = f"""
Analyze project risks.

USER REQUEST:
{user_request}

AVAILABLE CONTEXT:
{context}

Identify 5-8 meaningful risks.
For every risk provide:
- risk
- probability: Low, Medium, High
- impact: Low, Medium, High
- mitigation

Avoid generic risks.
Return valid JSON only.
"""
    raw = llm_call(prompt)
    parsed = _parse_risks(raw)
    if parsed:
        return parsed
    return _fallback_risks()


def _parse_risks(raw: str) -> list[Risk]:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            return []
        return [Risk(**item) for item in payload if isinstance(item, dict)]
    except Exception:
        return []


def _fallback_risks() -> list[Risk]:
    return [
        Risk(
            risk="Scope creep from late feature expansion",
            probability="High",
            impact="High",
            mitigation="Freeze MVP scope and require formal change approval.",
        ),
        Risk(
            risk="Data quality issues reduce model accuracy",
            probability="Medium",
            impact="High",
            mitigation="Create data quality gates and weekly validation checks.",
        ),
        Risk(
            risk="Integration delays with ATS and external APIs",
            probability="Medium",
            impact="Medium",
            mitigation="Prototype integrations in week 2 and track interface owners.",
        ),
        Risk(
            risk="Security and compliance findings delay launch",
            probability="Medium",
            impact="High",
            mitigation="Start security review in parallel and schedule remediation sprint.",
        ),
        Risk(
            risk="User adoption is lower than expected",
            probability="Medium",
            impact="Medium",
            mitigation="Run pilot cohort onboarding and collect weekly usage feedback.",
        ),
    ]
