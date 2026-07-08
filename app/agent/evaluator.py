from typing import Any


def evaluate_output(context: dict[str, Any]) -> dict[str, Any]:
    sections = context.get("report_sections", {})
    assumptions = context.get("assumptions", [])
    budget = sections.get("budget", {})
    timeline = sections.get("timeline", {})
    request = str(context.get("request", "")).lower()

    issues: list[str] = []
    if not assumptions:
        issues.append("Assumptions are missing.")
    if not budget:
        issues.append("Budget section is incomplete.")
    if not timeline:
        issues.append("Timeline section is incomplete.")
    if "3 months" in request:
        duration = str(timeline.get("duration", "")).lower()
        if "3 months" not in duration:
            issues.append("Timeline does not match the requested three-month window.")
    if "budget" in request and not budget.get("budget"):
        issues.append("Budget amount was not generated.")

    completeness = 9 if not issues else 6
    clarity = 9 if not issues else 7
    consistency = 9 if not issues else 6
    requirement_coverage = 9 if not issues else 6
    score = round((completeness + clarity + consistency + requirement_coverage) / 4, 1)

    return {
        "completeness": completeness,
        "clarity": clarity,
        "consistency": consistency,
        "requirement_coverage": requirement_coverage,
        "issues": issues or ["No major issues detected."],
        "passed": score >= 7.5 and not issues,
        "score": score,
    }


def needs_recovery(evaluation: dict[str, Any]) -> bool:
    return not bool(evaluation.get("passed"))
