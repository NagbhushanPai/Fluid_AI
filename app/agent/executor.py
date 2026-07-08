import time
from typing import Any

from app.models.task import Task
from app.tools.registry import run_tool


def execute_tasks(
    tasks: list[Task],
    user_request: str,
    assumptions: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context: dict[str, Any] = {"request": user_request, "assumptions": assumptions or []}
    trace: list[dict[str, Any]] = []
    task_map = {task.id: task for task in tasks}
    completed: set[str] = set()

    while len(completed) < len(tasks):
        progress = False
        for task in tasks:
            if task.id in completed:
                continue
            if any(dep not in completed for dep in task.dependencies):
                continue

            start = time.perf_counter()
            task.status = "running"
            try:
                result = run_tool(task.tool, user_request, context)
                task.result = _stringify_result(result)
                task.status = "completed"
                _merge_context(context, task, result)
                completed.add(task.id)
                trace.append(
                    {
                        "task_id": task.id,
                        "status": task.status,
                        "duration_ms": int((time.perf_counter() - start) * 1000),
                        "tool": task.tool,
                        "result_preview": task.result[:180] if task.result else None,
                    }
                )
                progress = True
            except Exception as exc:
                task.status = "failed"
                task.result = str(exc)
                trace.append(
                    {
                        "task_id": task.id,
                        "status": task.status,
                        "duration_ms": int((time.perf_counter() - start) * 1000),
                        "tool": task.tool,
                        "result_preview": task.result,
                    }
                )
                completed.add(task.id)
                progress = True

        if not progress:
            break

    return context, trace


def _merge_context(context: dict[str, Any], task: Task, result: Any) -> None:
    if task.tool == "reasoning_tool" and isinstance(result, dict):
        context["insights"] = result.get("insights")
        assumptions = result.get("assumptions", [])
        if assumptions:
            context["assumptions"] = assumptions
    elif task.tool == "planning_tool" and isinstance(result, dict):
        context["timeline"] = result
    elif task.tool == "estimation_tool" and isinstance(result, dict):
        context["budget"] = result
    elif task.tool == "content_tool" and isinstance(result, dict):
        context["report_sections"] = result
    elif task.tool == "document_tool":
        context["document_status"] = result


def _stringify_result(result: Any) -> str:
    if isinstance(result, str):
        return result
    return str(result)

