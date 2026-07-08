import json
from typing import Any

from app.llm.client import llm_call
from app.models.task import Task


def create_plan(user_request: str) -> list[Task]:
    prompt = f"""
Return only valid JSON for a dependency-aware task list.
Each task must have: id, description, tool, dependencies.
Use document-specific tools such as reasoning_tool, planning_tool,
estimation_tool, risk_tool, and content_synthesis_tool.

Request: {user_request}
"""
    raw = llm_call(prompt)
    tasks = _parse_tasks(raw)
    if tasks:
        return tasks
    return _fallback_plan(user_request)


def create_corrective_plan(issues: list[Any]) -> list[Task]:
    prompt = """
Create corrective tasks as valid JSON.
Each task must have: id, description, tool, dependencies.
Issues:
""" + "\n".join(
        f"- {getattr(issue, 'section', 'general')}: {getattr(issue, 'problem', str(issue))}"
        for issue in issues
    )
    raw = llm_call(prompt)
    tasks = _parse_tasks(raw)
    if tasks:
        return tasks

    corrective_tasks: list[Task] = []
    for index, issue in enumerate(issues, start=1):
        section = str(getattr(issue, "section", "")).lower()
        problem = str(getattr(issue, "problem", issue)).lower()
        if "budget" in section or "budget" in problem:
            corrective_tasks.append(
                Task(
                    id=f"fix_budget_{index}",
                    description="Clarify budget assumptions",
                    tool="estimation_tool",
                    dependencies=[],
                )
            )
        elif "timeline" in section or "timeline" in problem:
            corrective_tasks.append(
                Task(
                    id=f"fix_timeline_{index}",
                    description="Fix timeline conflict",
                    tool="planning_tool",
                    dependencies=[],
                )
            )
        elif "risk" in section or "risk" in problem:
            corrective_tasks.append(
                Task(
                    id=f"fix_risks_{index}",
                    description="Expand and clarify risk analysis",
                    tool="risk_tool",
                    dependencies=[],
                )
            )
        else:
            corrective_tasks.append(
                Task(
                    id=f"fix_{index}",
                    description=str(getattr(issue, "problem", issue)),
                    tool="reasoning_tool",
                    dependencies=[],
                )
            )
    return corrective_tasks


def _parse_tasks(raw: str) -> list[Task]:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            return []
        tasks = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            tasks.append(
                Task(
                    id=item["id"],
                    description=item["description"],
                    tool=item["tool"],
                    dependencies=item.get("dependencies", []),
                )
            )
        return tasks
    except Exception:
        return []


def _fallback_plan(user_request: str) -> list[Task]:
    return [
        Task(id="task_1", description="Analyze project requirements", tool="reasoning_tool", dependencies=[]),
        Task(id="task_2", description="Define project scope and objectives", tool="reasoning_tool", dependencies=["task_1"]),
        Task(id="task_3", description="Create 90-day implementation timeline", tool="planning_tool", dependencies=["task_1", "task_2"]),
        Task(id="task_4", description="Estimate detailed project budget", tool="estimation_tool", dependencies=["task_2"]),
        Task(id="task_5", description="Perform project risk analysis", tool="risk_tool", dependencies=["task_2", "task_3"]),
        Task(
            id="task_6",
            description="Synthesize final project plan",
            tool="content_synthesis_tool",
            dependencies=["task_2", "task_3", "task_4", "task_5"],
        ),
    ]
