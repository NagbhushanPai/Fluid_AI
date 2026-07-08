from uuid import uuid4

from app.agent.evaluator import evaluate_document
from app.agent.executor import execute_tasks
from app.agent.planner import create_plan
from app.core.config import OUTPUT_DIR
from app.models.content import Assumption
from app.models.response import AgentResponse, ExecutionRecord
from app.tools.content import revise_document_content, synthesize_document_content
from app.tools.document import generate_document
from app.tools.reasoning import derive_assumptions


def run_agent(user_request: str) -> AgentResponse:
    request_id = uuid4().hex[:12]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    assumptions = derive_assumptions(user_request)
    plan = create_plan(user_request)
    context, trace = execute_tasks(plan, user_request, assumptions)

    content = context.get("document_content")
    if content is None:
        content = synthesize_document_content(user_request, context)

    evaluation = evaluate_document(user_request, content)
    revisions = 0
    while revisions < 2 and not evaluation.passed:
        content = revise_document_content(
            content=content,
            issues=evaluation.issues,
            request=user_request,
            context=context,
        )
        evaluation = evaluate_document(user_request, content)
        revisions += 1

    document_path = generate_document(OUTPUT_DIR / f"{request_id}.docx", content)

    execution_records = [
        ExecutionRecord(
            task_id=item["task_id"],
            status=item["status"],
            duration_ms=item["duration_ms"],
            tool=item["tool"],
            result_preview=item.get("result_preview"),
        )
        for item in trace
    ]

    completed_count = sum(1 for item in trace if item.get("status") == "completed")
    failed_count = sum(1 for item in trace if item.get("status") == "failed")
    normalized_assumptions = _normalize_assumptions(context.get("assumptions", assumptions))

    status = "completed" if failed_count == 0 else "partial"
    return AgentResponse(
        status=status,
        request_id=request_id,
        plan=plan,
        assumptions=normalized_assumptions,
        execution=execution_records,
        quality_score=float(evaluation.average_score),
        revisions=revisions,
        document_url=str(document_path),
        execution_summary=(
            f"Executed {len(trace)} tasks: {completed_count} completed, {failed_count} failed. "
            f"Evaluation score: {evaluation.average_score}."
        ),
        content=content,
        evaluation=evaluation,
    )


def _normalize_assumptions(items: list[dict] | list[Assumption]) -> list[Assumption]:
    normalized: list[Assumption] = []
    for item in items:
        if isinstance(item, Assumption):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(Assumption(**item))
    return normalized
