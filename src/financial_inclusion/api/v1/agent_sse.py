import base64
import logging
import json
import asyncio
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai.types import Blob, Content, Part

from financial_inclusion.agents.financial_coach.agent_runner import APP_NAME
from financial_inclusion.core.security import get_current_user
from financial_inclusion.agents.financial_coach.agent import root_agent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_sessions: Dict[str, LiveRequestQueue] = {}


APP_NAME = "Agent"
# --- Agent Session Management ---

async def start_agent_session(user_id: str, is_audio: bool = False):
    """Starts an agent session and returns the event stream and request queue."""
    logger.info(f"Starting agent session for user_id: {user_id}, audio: {is_audio}")
    runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id=user_id)
    
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])
    
    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_sse(live_events):
    """Streams events from the agent to the client via SSE."""
    async for event in live_events:
        if event.turn_complete or event.interrupted:
            message = {"turn_complete": event.turn_complete, "interrupted": event.interrupted}
            yield f"data: {json.dumps(message)}\n\n"
            logger.info(f"[AGENT TO CLIENT]: {message}")
            continue

        part: Part = event.content and event.content.parts and event.content.parts[0]
        if not part:
            continue

        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/")
        if is_audio:
            audio_data = part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": part.inline_data.mime_type,
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                yield f"data: {json.dumps(message)}\n\n"
                logger.info(f"[AGENT TO CLIENT]: {part.inline_data.mime_type}: {len(audio_data)} bytes.")
                continue
        
        if part.text and event.partial:
            message = {"mime_type": "text/plain", "data": part.text}
            yield f"data: {json.dumps(message)}\n\n"
            logger.info(f"[AGENT TO CLIENT]: text/plain: {part.text}")


# --- API Router ---
router = APIRouter(prefix="/api/v1/agent")

@router.get("/events")
async def sse_endpoint(current_user = Depends(get_current_user), is_audio: str = "false"):
    """SSE endpoint for agent-to-client communication."""
    user_id = current_user.id
    live_events, live_request_queue = await start_agent_session(user_id, is_audio.lower() == "true")
    active_sessions[user_id] = live_request_queue
    logger.info(f"Client #{user_id} connected via SSE, audio mode: {is_audio}")

    def cleanup():
        live_request_queue.close()
        if user_id in active_sessions:
            del active_sessions[user_id]
        logger.info(f"Client #{user_id} disconnected from SSE, session cleaned up.")

    async def event_generator():
        try:
            async for data in agent_to_client_sse(live_events):
                yield data
        except asyncio.CancelledError:
             logger.info(f"SSE connection for user {user_id} was cancelled by the client.")
        except Exception as e:
            logger.error(f"Error in SSE stream for user {user_id}: {e}")
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )

@router.post("/send")
async def send_message_endpoint(request: Request,current_user = Depends(get_current_user)):
    """HTTP endpoint for client-to-agent communication."""
    user_id = current_user.id
    live_request_queue = active_sessions.get(user_id)
    if not live_request_queue:
        logger.warning(f"Attempted to send message to non-existent session: {user_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        message = await request.json()
        mime_type = message.get("mime_type")
        data = message.get("data")

        if mime_type == "text/plain":
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            logger.info(f"[CLIENT TO AGENT] User {user_id} sent text: {data}")
        elif mime_type and mime_type.startswith("audio/"):
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
            logger.info(f"[CLIENT TO AGENT] User {user_id} sent audio: {len(decoded_data)} bytes")
        else:
            raise HTTPException(status_code=400, detail=f"MIME type not supported: {mime_type}")
        
        return {"status": "sent"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body.")
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message.")


