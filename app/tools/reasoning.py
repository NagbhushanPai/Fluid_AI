from typing import Any


def derive_assumptions(user_request: str) -> list[dict[str, Any]]:
    request = user_request.lower()
    assumptions: list[dict[str, Any]] = []

    if "budget" in request or "project plan" in request:
        assumptions.append(
            {
                "field": "budget",
                "value": "$100,000",
                "rationale": "No budget was provided by the user.",
            }
        )

    if "3 months" in request or "timeline" in request:
        assumptions.append(
            {
                "field": "team_size",
                "value": "6 people",
                "rationale": "Estimated for a 3-month delivery window.",
            }
        )

    if not assumptions:
        assumptions.append(
            {
                "field": "scope",
                "value": "Standard implementation scope",
                "rationale": "The request does not specify detailed constraints.",
            }
        )

    return assumptions


def summarize_assumptions(assumptions: list[dict[str, Any]]) -> str:
    lines = []
    for item in assumptions:
        lines.append(f"- {item['field']}: {item['value']} ({item.get('rationale', item.get('reason', 'No rationale provided.'))})")
    return "\n".join(lines)

