from typing import Any

from app.tools.estimation import create_timeline, estimate_budget
from app.tools.reasoning import derive_assumptions


def run_tool(tool_name: str, user_request: str, context: dict[str, Any]) -> dict[str, Any] | str:
    if tool_name == "reasoning_tool":
        return {
            "insights": f"Requirements analyzed for: {user_request}",
            "assumptions": derive_assumptions(user_request),
        }

    if tool_name == "planning_tool":
        return create_timeline(user_request)

    if tool_name == "estimation_tool":
        return estimate_budget(user_request, context.get("assumptions", []))

    if tool_name == "content_tool":
        assumptions = context.get("assumptions", [])
        budget = context.get("budget", {})
        timeline = context.get("timeline", {})
        return {
            "executive_summary": f"This plan addresses the request: {user_request}",
            "risks": [
                "Budget uncertainty",
                "Timeline conflict if dependencies slip",
            ],
            "timeline": timeline,
            "budget": budget,
            "implementation_notes": "Generated with dependency-aware execution.",
            "assumptions_snapshot": assumptions,
        }

    if tool_name == "document_tool":
        return "Document artifact assembled."

    return f"Executed fallback tool: {tool_name}"

