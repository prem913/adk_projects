from fastapi import WebSocket, WebSocketDisconnect,APIRouter
from takopi.agents.agent_runner import AgentRunnerQueue, LiveRunnerMessageTextModel
from takopi.agents.agent import root_agent
from common.core.logging import logging
import asyncio
import traceback
from takopi.agents.prompt import CODER_KEY, RESEARCH_KEY

logger = logging.getLogger(__name__)


adk_runner = AgentRunnerQueue(agent=root_agent, name="takopi")

router = APIRouter()

@router.get("/", summary="Health Check")
async def read_root():
    """A simple HTTP endpoint to confirm the server is running."""
    return {"status": "ADK Live Runner is active"}


@router.get("/state/{client_id}", summary="Get current session state")
async def get_session_state(client_id: str):
    """Returns the current full state for the given client."""
    session = await adk_runner.get_session(client_id)
    return {"state": session.state,"events": session.events}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Handles the WebSocket connection for a live chat session.
    It manages bidirectional communication between the client and the ADK agent.
    """
    session = await adk_runner.get_session(client_id,initial_state={CODER_KEY:"coder agent has not been called yet",RESEARCH_KEY: "Research agent has not been called yet"})
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for client_id: {client_id}, with session: {session.id}")
    output_queue: asyncio.Queue[LiveRunnerMessageTextModel]= asyncio.Queue()

    async def client_input_handler():
        """Receives messages from the client and sends them to the agent."""
        try:
            while True:
                data = await websocket.receive_text()
                message = LiveRunnerMessageTextModel.model_validate_json(data)
                session = await adk_runner.get_session(client_id)
                await adk_runner.message(message,session,output_queue)
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected.")
        except Exception as e:
            logger.error(f"Error in client input handler for {client_id}: {e}")

    async def agent_output_handler():
        """Receives messages from the agent queue and sends them to the client."""
        try:
            while True:
                message = await output_queue.get()
                await websocket.send_text(message.model_dump_json())
                output_queue.task_done()
        except Exception as e:
            logger.error(f"Error in agent output handler for {client_id}: {e}")

    # Run the ADK session and the two handlers concurrently.
    # `asyncio.gather` will run them all, and if any of them exits
    # (e.g., due to WebSocketDisconnect), it will cancel the others.
    try:
        _ = await asyncio.gather(
            # adk_runner.run_session_live(output_queue,session),
            client_input_handler(),
            agent_output_handler(),
        )
    except Exception as e:
        logger.error(f"Session ended for client {client_id} with error: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info(f"Closing connection for client {client_id}.")

