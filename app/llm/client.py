import json
import os
import re
from typing import List
from urllib import request

from app.core.config import DEFAULT_MODEL


def llm_call(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            return _call_groq(prompt, api_key)
        except Exception:
            pass

    return _local_fallback(prompt)


def _call_groq(prompt: str, api_key: str) -> str:
    payload = json.dumps(
        {
            "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            "messages": [
                {"role": "system", "content": "You are an autonomous document planning agent."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
    ).encode("utf-8")

    req = request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


def _local_fallback(prompt: str) -> str:
    lowered = prompt.lower()
    if "return only valid json" in lowered and "task" in lowered:
        return json.dumps(_fallback_tasks(prompt))
    if "assumption" in lowered and "json" in lowered:
        return json.dumps(_fallback_assumptions(prompt))
    if "quality" in lowered or "evaluate" in lowered:
        return json.dumps(_fallback_evaluation(prompt))
    if "create corrective tasks" in lowered:
        return json.dumps(_fallback_corrective_tasks(prompt))
    return "Local fallback response."


def _fallback_tasks(prompt: str) -> list[dict]:
    request_text = _extract_request(prompt)
    request_lower = request_text.lower()

    tasks = [
        {
            "id": "task_1",
            "description": "Analyze project requirements",
            "tool": "reasoning_tool",
            "dependencies": [],
        },
        {
            "id": "task_2",
            "description": "Define project scope and objectives",
            "tool": "reasoning_tool",
            "dependencies": ["task_1"],
        },
        {
            "id": "task_3",
            "description": "Create 90-day implementation timeline",
            "tool": "planning_tool",
            "dependencies": ["task_1", "task_2"],
        },
        {
            "id": "task_4",
            "description": "Estimate detailed project budget",
            "tool": "estimation_tool",
            "dependencies": ["task_2"],
        },
        {
            "id": "task_5",
            "description": "Perform project risk analysis",
            "tool": "risk_tool",
            "dependencies": ["task_2", "task_3"],
        },
        {
            "id": "task_6",
            "description": "Synthesize final project plan",
            "tool": "content_synthesis_tool",
            "dependencies": ["task_2", "task_3", "task_4", "task_5"],
        },
    ]

    if "proposal" in request_lower:
        tasks.insert(
            1,
            {
                "id": "task_0",
                "description": "Frame proposal scope",
                "tool": "reasoning_tool",
                "dependencies": [],
            },
        )

    return tasks


def _fallback_assumptions(prompt: str) -> list[dict]:
    request_text = _extract_request(prompt)
    request_lower = request_text.lower()
    assumptions = []
    if "budget" in request_lower:
        assumptions.append(
            {
                "field": "budget",
                "value": "$100,000",
                "rationale": "No explicit budget was provided.",
            }
        )
    assumptions.append(
        {
            "field": "team_size",
            "value": "6 people",
            "rationale": "Estimated from typical scope and 3-month delivery window.",
        }
    )
    return assumptions


def _fallback_evaluation(prompt: str) -> dict:
    text = prompt.lower()
    issues: List[dict] = []
    if "timeline" in text and "phase" not in text:
        issues.append(
            {
                "section": "timeline",
                "problem": "Timeline lacks clearly defined phases.",
                "severity": "high",
                "suggested_fix": "Add at least 3 phases with duration, activities, and deliverables.",
            }
        )
    if "budget" in text and "rationale" not in text:
        issues.append(
            {
                "section": "budget",
                "problem": "Budget lacks item-level rationale.",
                "severity": "medium",
                "suggested_fix": "Include rationale for each budget category.",
            }
        )
    score = 8.2 if not issues else 6.5
    return {
        "requirement_coverage": 8.1 if not issues else 6.4,
        "content_depth": 8.2 if not issues else 6.2,
        "clarity": 8.3 if not issues else 6.7,
        "consistency": 8.0 if not issues else 6.3,
        "professional_quality": 8.2 if not issues else 6.5,
        "issues": issues,
        "passed": not issues,
        "average_score": score,
    }


def _fallback_corrective_tasks(prompt: str) -> list[dict]:
    issues = re.findall(r"-\s*(.+)", prompt)
    tasks = []
    for index, issue in enumerate(issues, start=1):
        tasks.append(
            {
                "id": f"fix_{index}",
                "description": issue,
                "tool": "reasoning_tool",
                "dependencies": [],
            }
        )
    return tasks or [
        {
            "id": "fix_1",
            "description": "Clarify ambiguous assumptions",
            "tool": "reasoning_tool",
            "dependencies": [],
        }
    ]


def _extract_request(prompt: str) -> str:
    match = re.search(r"Request:\s*(.+)", prompt, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else prompt

