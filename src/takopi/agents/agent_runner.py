from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types
from common.core.logging import logging

logger = logging.getLogger(__name__)

class AgentRunner:
    def __init__(self,agent: BaseAgent,app_name: str = "generic_app"):
        self.session_service = InMemorySessionService()
        self.agent = agent
        self.app_name = app_name
        self.runner = Runner(session_service=self.session_service, app_name=app_name,agent=agent)

    async def get_session(self,id: str,initial_state: dict | None = None):
        session_id = f"session_{id}"
        user_id = f"user_{id}"
        current_session = await self.session_service.get_session(session_id=session_id, app_name=self.app_name, user_id=user_id)

        if not current_session:
            logger.info("current session does't exist")
            current_session = await self.session_service.create_session(app_name=self.app_name, user_id=user_id, state=initial_state)
            if not current_session:
                logger.error("Failed to get/create session")
                raise Exception("Failed to get/create session")
        return current_session


    async def prompt_agent(self,prompt: str,session: Session):
        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        events = self.runner.run_async(user_id=session.user_id, new_message=content, session_id=session.id)

        final_response = None
        async for event in events:
            if not event.is_final_response():
                continue
            part = event.content.parts[0] if event.content and event.content.parts else None
            if not part:
                continue
            if part.text:
                logger.info("Final Response: " + part.text)
                final_response = part.text

        return final_response




