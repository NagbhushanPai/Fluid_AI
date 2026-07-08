from typing import Any


def estimate_budget(user_request: str, assumptions: list[dict[str, Any]]) -> dict[str, Any]:
    request = user_request.lower()
    budget = "$100,000"
    if "startup" in request:
        budget = "$75,000"
    if "enterprise" in request:
        budget = "$180,000"

    return {
        "budget": budget,
        "rationale": "Derived from request complexity and assumptions.",
        "risk_buffer": "15%",
    }


def create_timeline(user_request: str) -> dict[str, Any]:
    return {
        "duration": "3 months",
        "milestones": [
            "Discovery and requirements",
            "Planning and design",
            "Build and review",
            "Launch preparation",
        ],
    }

