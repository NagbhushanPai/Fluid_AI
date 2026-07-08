from typing import Any

from app.models.content import BudgetItem, BudgetPlan


def estimate_budget(user_request: str, assumptions: list[dict[str, Any]]) -> BudgetPlan:
    request = user_request.lower()
    baseline_total = 100000.0
    if "startup" in request:
        baseline_total = 85000.0
    if "enterprise" in request:
        baseline_total = 180000.0

    items = [
        BudgetItem(category="Engineering", amount=45000, rationale="Three-month development effort"),
        BudgetItem(category="AI Infrastructure", amount=12000, rationale="LLM and model inference costs"),
        BudgetItem(category="Cloud Infrastructure", amount=8000, rationale="Development and production hosting"),
        BudgetItem(category="Testing and Security", amount=10000, rationale="QA, penetration testing and compliance"),
        BudgetItem(category="Launch and Operations", amount=10000, rationale="Deployment and initial operations"),
        BudgetItem(category="Contingency", amount=15000, rationale="15% project contingency"),
    ]

    if baseline_total > 100000:
        items[0] = BudgetItem(category="Engineering", amount=70000, rationale="Expanded engineering effort")
        items[5] = BudgetItem(category="Contingency", amount=30000, rationale="Expanded contingency for enterprise scope")
    elif baseline_total < 100000:
        items[0] = BudgetItem(category="Engineering", amount=38000, rationale="Lean startup delivery effort")
        items[5] = BudgetItem(category="Contingency", amount=12000, rationale="Reduced contingency for startup scope")

    total = round(sum(item.amount for item in items), 2)
    plan = BudgetPlan(currency="USD", items=items, total=total)
    plan.validate_total()
    return plan


def create_timeline(user_request: str) -> dict[str, Any]:
    return {
        "duration": "3 months",
        "phases": [
            {
                "phase": "Discovery",
                "duration": "2 weeks",
                "activities": ["Requirements gathering", "Stakeholder review"],
                "deliverables": ["Requirements brief", "Success criteria"],
            },
            {
                "phase": "Build",
                "duration": "6 weeks",
                "activities": ["Prototype development", "Model integration", "Testing"],
                "deliverables": ["Working prototype", "Integration notes"],
            },
            {
                "phase": "Launch Preparation",
                "duration": "4 weeks",
                "activities": ["Hardening", "Security review", "Deployment planning"],
                "deliverables": ["Launch checklist", "Go-live plan"],
            },
        ],
    }

