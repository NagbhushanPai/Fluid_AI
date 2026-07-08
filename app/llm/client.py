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
            "description": "Identify business requirements",
            "tool": "reasoning_tool",
            "dependencies": [],
        },
        {
            "id": "task_2",
            "description": "Create project timeline",
            "tool": "planning_tool",
            "dependencies": ["task_1"],
        },
        {
            "id": "task_3",
            "description": "Estimate project budget",
            "tool": "estimation_tool",
            "dependencies": ["task_1"],
        },
        {
            "id": "task_4",
            "description": "Generate final document sections",
            "tool": "content_tool",
            "dependencies": ["task_2", "task_3"],
        },
        {
            "id": "task_5",
            "description": "Assemble DOCX report",
            "tool": "document_tool",
            "dependencies": ["task_4"],
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
                "reason": "No explicit budget was provided.",
            }
        )
    assumptions.append(
        {
            "field": "team_size",
            "value": "6 people",
            "reason": "Estimated from typical scope and 3-month delivery window.",
        }
    )
    return assumptions


def _fallback_evaluation(prompt: str) -> dict:
    text = prompt.lower()
    issues = []
    if "unclear" in text or "missing" in text:
        issues.append("Some sections may need more detail.")
    if "budget" in text and "assumption" not in text:
        issues.append("Budget assumptions are unclear.")
    score = 8.7 if not issues else 6.8
    return {
        "completeness": 8 if not issues else 6,
        "clarity": 9 if not issues else 7,
        "consistency": 8 if not issues else 6,
        "requirement_coverage": 8 if not issues else 6,
        "issues": issues or ["No major issues detected."],
        "passed": not issues,
        "score": score,
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

