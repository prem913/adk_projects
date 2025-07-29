from typing import Literal
from fastapi import APIRouter,Query
from fastapi.responses import JSONResponse
from sqlalchemy.sql import text
from financial_inclusion.agents.financial_coach.agent_runner import generate_cards
from financial_inclusion.agents.financial_coach.agent_runner import call_agent
from financial_inclusion.core.logging import logging
from financial_inclusion.models.db.user_model import User
from financial_inclusion.core.security import get_current_user
from fastapi import Depends
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException,UploadFile,File,HTTPException
from financial_inclusion.core.logging import logging
import google.generativeai as genai
import os
import base64

class Request(BaseModel):
    text: str | None
    audio: str | None
class Response(BaseModel):
    text: str | None
    audio: str | None


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent")

@router.get("/generate_cards")
async def get_generate_cards(user_id: str = Query()):
    return await generate_cards(user_id)

@router.post("/fincoach")
async def get_response(body: Request, current_user: User = Depends(get_current_user)):
    modality : Literal["AUDIO","TEXT"] | None = None
    prompt = None
    if body.text:
        modality = "TEXT"
        prompt = body.text
    elif body.audio:
        modality = "AUDIO"
        prompt = body.audio
        missing_padding = len(prompt) % 4
        if missing_padding:
            prompt += '=' * (4 - missing_padding)
    elif modality is None:
        return "error"
    logger.info(f"Generating response for user {current_user.id} with prompt: {prompt}")
    try:
        res = await call_agent(prompt, str(current_user.id),modality=modality) 
        if res:
            (text_response,audio_response) = res
            return {"status": "success", "response": Response(text="\n".join(text_response),audio = "".join(audio_response)) }
    except Exception as exception:
        logger.error(exception)
        return {"status": "error", "message": str(exception)}



async def audio_to_base64(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()

        base64_encoded_bytes = base64.b64encode(audio_bytes)

        base64_encoded_string = base64_encoded_bytes.decode('utf-8')

        return {
            "base64": base64_encoded_string,
            "mimeType": file.content_type
        }
    except Exception as e:
        logger.error(e)
