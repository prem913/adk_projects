from google.adk.agents import Agent
from google.adk.tools import google_search
from financial_inclusion.agents.financial_coach.prompts.system_prompt import SYSTEM_PROMPT
from financial_inclusion.core.logging import logging

logger = logging.getLogger(__name__)


root_agent = Agent(
    name="financial_coach",
    model="gemini-2.5-flash",
    description=("A financial coach that generates reading material about financial advice"),
    instruction=(SYSTEM_PROMPT),
    tools = [google_search],
    # generate_content_config=types.GenerateContentConfig(response_mime_type="application/json")
)

