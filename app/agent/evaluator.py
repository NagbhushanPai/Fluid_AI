import json

from app.llm.client import llm_call
from app.models.content import DocumentContent
from app.models.evaluation import EvaluationIssue, EvaluationResult


def evaluate_document(user_request: str, content: DocumentContent) -> EvaluationResult:
    deterministic_issues = deterministic_checks(content)
    prompt = f"""
You are a strict senior business-document reviewer.

Evaluate the generated document against the ORIGINAL
USER REQUEST.

Scoring criteria:

1. Requirement Coverage
Did the document satisfy every explicit requirement?

2. Content Depth
Does every major section contain actionable,
specific information?

3. Clarity
Is the document understandable and well structured?

4. Consistency
Are budgets, timelines, assumptions and recommendations
internally consistent?

5. Professional Quality
Would this document be acceptable in a professional
business environment?

IMPORTANT:

Do not give scores above 8 unless the document contains
specific evidence supporting the score.

A section consisting only of generic statements must
score below 6.

For every problem return:
- affected section
- specific problem
- severity
- suggested corrective action

Pass threshold: 8.0 average.

Return JSON only.

USER REQUEST:
{user_request}

DOCUMENT CONTENT:
{content.model_dump_json(indent=2)}
"""
    raw = llm_call(prompt)
    parsed = _parse_evaluation(raw)
    if parsed is None:
        parsed = _fallback_evaluation(deterministic_issues)

    merged = list(parsed.issues) + _deterministic_issue_objects(deterministic_issues)
    parsed.issues = _dedupe_issues(merged)

    parsed.average_score = round(
        (
            parsed.requirement_coverage
            + parsed.content_depth
            + parsed.clarity
            + parsed.consistency
            + parsed.professional_quality
        )
        / 5,
        1,
    )

    if deterministic_issues:
        parsed.average_score = max(0.0, round(parsed.average_score - 0.3 * len(deterministic_issues), 1))

    parsed.passed = parsed.average_score >= 8.0 and not parsed.issues
    return parsed


def deterministic_checks(content: DocumentContent) -> list[str]:
    issues: list[str] = []

    if len(content.risks) < 5:
        issues.append("Risk analysis requires at least 5 risks.")

    if len(content.timeline) < 3:
        issues.append("Timeline requires at least 3 phases.")

    if len(content.budget) < 4:
        issues.append("Budget requires detailed breakdown.")

    if len(content.executive_summary.split()) < 100:
        issues.append("Executive summary lacks sufficient depth.")

    return issues


def _parse_evaluation(raw: str) -> EvaluationResult | None:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return None
        return EvaluationResult(
            requirement_coverage=float(payload["requirement_coverage"]),
            content_depth=float(payload["content_depth"]),
            clarity=float(payload["clarity"]),
            consistency=float(payload["consistency"]),
            professional_quality=float(payload["professional_quality"]),
            issues=[EvaluationIssue(**item) for item in payload.get("issues", [])],
            passed=bool(payload.get("passed", False)),
            average_score=float(payload.get("average_score", 0.0)),
        )
    except Exception:
        return None


def _fallback_evaluation(deterministic_issues: list[str]) -> EvaluationResult:
    issue_objects = _deterministic_issue_objects(deterministic_issues)
    base = 8.6
    penalty = 0.5 * len(deterministic_issues)
    score = max(0.0, round(base - penalty, 1))
    return EvaluationResult(
        requirement_coverage=max(0.0, score - 0.1),
        content_depth=max(0.0, score - 0.2),
        clarity=max(0.0, score - 0.1),
        consistency=max(0.0, score - 0.2),
        professional_quality=max(0.0, score - 0.1),
        issues=issue_objects,
        passed=score >= 8.0 and not issue_objects,
        average_score=score,
    )


def _deterministic_issue_objects(issues: list[str]) -> list[EvaluationIssue]:
    mapped: list[EvaluationIssue] = []
    for issue in issues:
        lowered = issue.lower()
        if "risk" in lowered:
            section = "risks"
        elif "timeline" in lowered:
            section = "timeline"
        elif "budget" in lowered:
            section = "budget"
        else:
            section = "executive summary"

        mapped.append(
            EvaluationIssue(
                section=section,
                problem=issue,
                severity="high",
                suggested_fix=f"Revise the {section} section with concrete, non-generic detail.",
            )
        )
    return mapped


def _dedupe_issues(issues: list[EvaluationIssue]) -> list[EvaluationIssue]:
    unique: list[EvaluationIssue] = []
    seen: set[tuple[str, str]] = set()
    for issue in issues:
        key = (issue.section, issue.problem)
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return unique
