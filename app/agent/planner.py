import json
from typing import Any

from app.llm.client import llm_call
from app.models.task import Task


def create_plan(user_request: str) -> list[Task]:
    prompt = f"""
Return only valid JSON for a dependency-aware task list.
Each task must have: id, description, tool, dependencies.

Request: {user_request}
"""
    raw = llm_call(prompt)
    tasks = _parse_tasks(raw)
    if tasks:
        return tasks
    return _fallback_plan(user_request)


def create_corrective_plan(issues: list[str]) -> list[Task]:
    prompt = """
Create corrective tasks as valid JSON.
Each task must have: id, description, tool, dependencies.
Issues:
""" + "\n".join(f"- {issue}" for issue in issues)
    raw = llm_call(prompt)
    tasks = _parse_tasks(raw)
    if tasks:
        return tasks

    corrective_tasks: list[Task] = []
    for index, issue in enumerate(issues, start=1):
        issue_lower = issue.lower()
        if "budget" in issue_lower:
            corrective_tasks.append(
                Task(
                    id=f"fix_budget_{index}",
                    description="Clarify budget assumptions",
                    tool="estimation_tool",
                    dependencies=[],
                )
            )
        elif "timeline" in issue_lower:
            corrective_tasks.append(
                Task(
                    id=f"fix_timeline_{index}",
                    description="Fix timeline conflict",
                    tool="planning_tool",
                    dependencies=[],
                )
            )
        else:
            corrective_tasks.append(
                Task(
                    id=f"fix_{index}",
                    description=issue,
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
        Task(id="task_1", description="Identify business requirements", tool="reasoning_tool", dependencies=[]),
        Task(id="task_2", description="Create project timeline", tool="planning_tool", dependencies=["task_1"]),
        Task(id="task_3", description="Estimate project budget", tool="estimation_tool", dependencies=["task_1"]),
        Task(
            id="task_4",
            description="Generate final document sections",
            tool="content_tool",
            dependencies=["task_2", "task_3"],
        ),
        Task(id="task_5", description="Assemble DOCX report", tool="document_tool", dependencies=["task_4"]),
    ]
