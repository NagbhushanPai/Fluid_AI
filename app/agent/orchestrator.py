from pathlib import Path
from uuid import uuid4

from app.agent.evaluator import evaluate_output, needs_recovery
from app.agent.executor import execute_tasks
from app.agent.planner import create_corrective_plan, create_plan
from app.core.config import OUTPUT_DIR, QUALITY_THRESHOLD
from app.models.response import AgentResponse, ExecutionRecord
from app.tools.document import generate_document
from app.tools.reasoning import derive_assumptions


def run_agent(user_request: str) -> AgentResponse:
    request_id = str(uuid4())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    assumptions = derive_assumptions(user_request)
    plan = create_plan(user_request)
    executed_plan = list(plan)
    context, trace = execute_tasks(plan, user_request, assumptions)
    evaluation = evaluate_output(context)
    revisions = 0

    if needs_recovery(evaluation):
        corrective_tasks = create_corrective_plan(evaluation.get("issues", []))
        executed_plan.extend(corrective_tasks)
        corrective_context, corrective_trace = execute_tasks(corrective_tasks, user_request, context.get("assumptions", assumptions))
        context.update(corrective_context)
        trace.extend(corrective_trace)
        revised_evaluation = evaluate_output(context)
        if revised_evaluation.get("score", 0) >= evaluation.get("score", 0):
            evaluation = revised_evaluation
        revisions = 1

    final_sections = context.get("report_sections", {})
    if not final_sections:
        final_sections = {
            "executive_summary": "A report was generated from the agent plan.",
            "timeline": context.get("timeline", {}),
            "risks": ["Budget uncertainty", "Dependency drift"],
        }

    document_path = generate_document(
        OUTPUT_DIR / f"{request_id}.docx",
        request_id,
        user_request,
        context.get("assumptions", assumptions),
        trace,
        final_sections,
        evaluation,
    )

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

    status = "completed" if evaluation.get("score", 0) >= QUALITY_THRESHOLD else "completed_with_warnings"
    return AgentResponse(
        status=status,
        request_id=request_id,
        plan=executed_plan,
        assumptions=context.get("assumptions", assumptions),
        execution=execution_records,
        quality_score=float(evaluation.get("score", 0)),
        revisions=revisions,
        document_url=str(document_path),
        execution_summary=f"Generated {len(trace)} task executions with quality score {evaluation.get('score', 0)}.",
    )
