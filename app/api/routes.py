from fastapi import APIRouter

from app.agent.orchestrator import run_agent
from app.models.request import RequestInput


router = APIRouter()


@router.post("/agent")
def agent_endpoint(payload: RequestInput):
    return run_agent(payload.request)

