from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from financial_inclusion.core.logging import logging
from .agent import root_agent

logger = logging.getLogger(__name__)

APP_NAME = "financial_coach"

session_service = InMemorySessionService()
runner = Runner(session_service=session_service, app_name=APP_NAME,agent=root_agent)


