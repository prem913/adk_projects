
from fastapi import APIRouter
from financial_inclusion.agents.financial_coach.agent_runner import generate_topics

router = APIRouter(prefix="/api/v1/topic")

@router.get("/")
async def get_topics():
    return await generate_topics("gates")
