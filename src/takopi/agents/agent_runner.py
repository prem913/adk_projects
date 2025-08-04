from typing import Literal
from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel
from common.core.logging import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self, agent: BaseAgent, app_name: str = "generic_app"):
        self.session_service: InMemorySessionService = InMemorySessionService()
        self.agent: BaseAgent = agent
        self.app_name: str = app_name
        self.runner: Runner = Runner(
            session_service=self.session_service, app_name=app_name, agent=agent
        )

    async def get_session(self, id: str, initial_state: dict[str, str] | None = None):
        session_id = f"session_{id}"
        user_id = f"user_{id}"
        current_session = await self.session_service.get_session(
            session_id=session_id, app_name=self.app_name, user_id=user_id
        )

        if not current_session:
            logger.info("current session does't exist")
            current_session = await self.session_service.create_session(
                app_name=self.app_name, user_id=user_id, state=initial_state
            )
            if not current_session:
                logger.error("Failed to get/create session")
                raise Exception("Failed to get/create session")
        return current_session

    async def prompt_agent(self, prompt: str, session: Session):
        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        events = self.runner.run_async(
            user_id=session.user_id, new_message=content, session_id=session.id
        )

        final_response = None
        async for event in events:
            if not event.is_final_response():
                continue
            part = (
                event.content.parts[0]
                if event.content and event.content.parts
                else None
            )
            if not part:
                continue
            if part.text:
                logger.info("Final Response: " + part.text)
                final_response = part.text

        return final_response


class LiveRunnerMessageTextModel(BaseModel):
    type: Literal[
        "end",
        "text",
        "interrupted",
        "turn_complete",
        "function_call",
        "function_response",
    ]
    data: str


class AgentRunnerQueue:
    def __init__(self, agent: BaseAgent, name: str = "generic_agent"):
        self.name: str = name
        self.agent: BaseAgent = agent
        self.session_service: DatabaseSessionService = DatabaseSessionService(db_url="sqlite:///sessions.db")
        self.runner: Runner = Runner(
            app_name=self.name, agent=self.agent, session_service=self.session_service
        )
        self.live_request_queue_map: dict[
            str, asyncio.Queue[LiveRunnerMessageTextModel]
        ] = {}

    async def get_session(self, id: str, initial_state: dict[str, str] | None = None):
        session_id = f"session_{id}"
        user_id = f"user_{id}"
        current_session = await self.session_service.get_session(
            session_id=session_id, app_name=self.name, user_id=user_id
        )

        if not current_session:
            logger.warning(f"session with id{id} does't exist.Creating one")
            current_session = await self.session_service.create_session(
                app_name=self.name,
                user_id=user_id,
                state=initial_state,
                session_id=session_id,
            )
            if not current_session:
                logger.error("Failed to get/create session")
                raise Exception("Failed to get/create session")
        return current_session

    async def message(
        self,
        message: LiveRunnerMessageTextModel,
        session: Session,
        output_queue: asyncio.Queue[LiveRunnerMessageTextModel],
    ):
        """Receives a message from the app and forwards it to the correct queue."""
        logger.info(f"Received message: {message.type}")
        await output_queue.put(LiveRunnerMessageTextModel(type="text", data="Thinking"))

        try:
            content = types.Content(role="user", parts=[types.Part(text=message.data)])
            events = self.runner.run_async(
                user_id=session.user_id, new_message=content, session_id=session.id
            )
            async for event in events:
                logger.info(f"Received event from runner {event}")
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            await output_queue.put(
                                LiveRunnerMessageTextModel(
                                    type="function_call",
                                    data=json.dumps(
                                        {
                                            "name": part.function_call.name,
                                            "args": part.function_call.args,
                                        }
                                    ),
                                )
                            )
                        if (
                            hasattr(part, "function_response")
                            and part.function_response
                        ):
                            await output_queue.put(
                                LiveRunnerMessageTextModel(
                                    type="function_response",
                                    data=json.dumps(
                                        {
                                            "name": part.function_response.name,
                                            "response": part.function_response.response,
                                        }
                                    ),
                                )
                            )
                        if hasattr(part, "text") and part.text:
                            logger.info("Putting into output queue: " + part.text)
                            await output_queue.put(
                                LiveRunnerMessageTextModel(type="text", data=part.text)
                            )
                if event.is_final_response():
                    logger.info("Turn complete event received.")
                    await output_queue.put(
                        LiveRunnerMessageTextModel(type="turn_complete", data="")
                    )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
