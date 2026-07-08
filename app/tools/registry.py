from typing import Any

from app.tools.content import synthesize_document_content
from app.tools.estimation import create_timeline, estimate_budget
from app.tools.reasoning import derive_assumptions
from app.tools.risk import analyze_risks


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

    if tool_name == "risk_tool":
        return analyze_risks(user_request, context)

    if tool_name == "content_synthesis_tool":
        return synthesize_document_content(user_request, context)

    if tool_name == "document_tool":
        return "Document artifact assembled."

    return f"Executed fallback tool: {tool_name}"

