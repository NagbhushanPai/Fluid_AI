# Autonomous Document Agent

A small FastAPI-based autonomous document agent that:

- accepts a user request at `POST /agent`
- plans a dependency-aware task graph
- executes tasks with tools for reasoning, estimation, content generation, and document creation
- evaluates the output with a reflection step
- generates a professional `.docx` report

## Features

- Dependency-aware task model
- Planner, executor, evaluator, and recovery flow
- Assumption registry for missing data
- `.docx` generation using `python-docx`
- Groq API support with a local fallback if `GROQ_API_KEY` is not set

## Project Structure

```text
autonomous-doc-agent/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── agent/
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── evaluator.py
│   │   └── orchestrator.py
│   ├── tools/
│   │   ├── registry.py
│   │   ├── reasoning.py
│   │   ├── estimation.py
│   │   └── document.py
│   ├── models/
│   │   ├── request.py
│   │   ├── task.py
│   │   └── response.py
│   ├── llm/
│   │   └── client.py
│   └── core/
│       ├── config.py
│       ├── exceptions.py
│       └── logging.py
├── outputs/
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- `pip`

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in values if needed.

## Environment Variables

- `GROQ_API_KEY`: optional Groq API key
- `GROQ_MODEL`: optional Groq model name, defaults to `llama3-8b-8192`

If `GROQ_API_KEY` is missing, the app uses local fallback logic so the API still works.

## Run Instructions

Start the API with Uvicorn:

```bash
uvicorn app.main:app --reload
```

If you prefer the root shim:

```bash
uvicorn main:app --reload
```

The server will run at:

```text
http://127.0.0.1:8000
```

## API Usage

### Request

`POST /agent`

```json
{
  "request": "Prepare a project plan for launching an AI-based hiring platform in 3 months. Include budget, risks, and timeline. Assume missing data if needed."
}
```

### Response

```json
{
  "status": "completed",
  "request_id": "abc-123",
  "plan": [],
  "assumptions": [],
  "execution": [],
  "quality_score": 8.7,
  "revisions": 1,
  "document_url": "outputs/abc-123.docx",
  "execution_summary": "Generated ..."
}
```

## Example cURL

```bash
curl -Method POST http://127.0.0.1:8000/agent `
  -ContentType "application/json" `
  -Body '{"request":"Create a business proposal for a food delivery startup"}'
```

## Output Files

Generated documents are written to the `outputs/` directory.

## Notes

- The planner expects structured JSON from the LLM and falls back to a local task graph if parsing fails.
- The evaluator supports targeted recovery instead of regenerating everything.
- The document generator uses `python-docx` and includes headings, tables, assumptions, and metadata.
