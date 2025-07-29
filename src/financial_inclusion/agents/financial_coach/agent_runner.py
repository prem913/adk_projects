from typing import Literal
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from financial_inclusion.core.logging import logging
from .agent import root_agent
from financial_inclusion.integrations.db import db_session
from financial_inclusion.services.user_service import get_user_profile_by_user_id
from financial_inclusion.services.user_service import get_user_by_id
import json
import base64

logger = logging.getLogger(__name__)

APP_NAME = "financial_coach"

session_service = InMemorySessionService()
runner = Runner(session_service=session_service, app_name=APP_NAME,agent=root_agent)

def get_user_data(user_id: str):
    with db_session() as db:
        user = get_user_by_id(db, user_id)
        profile = get_user_profile_by_user_id(db, user_id)

        user_data = None

        if user:
                user_data = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            
        return {"user": user_data, "profile": profile.get("personal_data","Not Available") if profile else None}

async def call_agent(prompt: str, user_id: str,modality: Literal["AUDIO","TEXT"]):
    current_session = await session_service.get_session(session_id=user_id, app_name=APP_NAME, user_id=user_id)

    if not current_session:
        logger.info("current session does't exist")
        user_profile = get_user_data(user_id)
        current_session = await session_service.create_session(app_name=APP_NAME, user_id=user_id, state={"user_profile": user_profile},session_id=user_id)
        if not current_session:
            logger.error("Failed to get/create session")
            return


    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            # Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )
    config = {"response_modalities": [modality], "speech_config": speech_config}
    if modality == "AUDIO":
        mime_type = "audio/pcm"
        config["output_audio_transcription"] = {}
        decoded_data = base64.b64decode(prompt)
        audio_data = types.Blob(data=decoded_data, mime_type=mime_type)
        content = types.Content(role="user",parts=[types.Part(inline_data=audio_data)])
    else:
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        mime_type = "text/plain"


    run_config = RunConfig(**config)

    events = runner.run_async(user_id=user_id, new_message=content, session_id=current_session.id,run_config=run_config)

    text_response = []
    audio_response = []
    async for event in events:
        part = event.content.parts[0] if event.content and event.content.parts else None
        if not part:
            continue
        if part.text:
            text_response.append(part.text)

        if part.inline_data and part.inline_data.mime_type and part.inline_data.mime_type.startswith("audio/pcm"):
            logger.info("audio response")
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                audio_response.append(base64.b64decode(audio_data))
            #     message = {
            #         "mime_type": "audio/pcm",
            #         "data": base64.b64encode(audio_data).decode("ascii"),
            #         "role": "model",
            #     }
            # logger.info(message)
        

    return text_response,audio_response

async def generate_cards(user_id: str):
    current_session = await session_service.get_session(session_id=user_id ,app_name=APP_NAME,user_id=user_id)
    if not current_session:
        current_session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
        if not current_session:
            raise Exception("Failed to get/create session")

    prompt = f"""
    i am beginner to finance and dont know how to manage money.
    """

    content = types.Content(role="user",parts=[types.Part(text=prompt)])
    event_generator = runner.run_async(user_id=user_id, new_message=content,session_id=current_session.id)
    final_response = None
    async for event in event_generator:
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            logger.info(f"final response: {final_response}")

    if not final_response:
        raise Exception("No final response")

    # Remove json delimeter in the response if any at all
    final_response = final_response[final_response.find('['):]
    final_response = final_response[:final_response.rfind(']') + 1]

    return json.loads(final_response)


async def generate_topics(user_id: str):
    current_session = await session_service.get_session(session_id=user_id ,app_name=APP_NAME,user_id=user_id)
    if not current_session:
        current_session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
        if not current_session:
            raise Exception("Failed to get/create session")

    prompt = f"""
    I am beginner to finance and dont know how to manage money.
    Please give me a list of topics that I should learn to improve my financial literacy.
    Each topic should be a json object with the following fields:
    - id: The name of the topic
    - description: A brief description of the topic
    - content: A brief content of the topic in markdown format
    - docs: A list of documents that are relevant to the topic
    - reference: A link to the source of the information    
    - icon: An emoji that represents the topic
    <Important>
    - The content in the above json object output should be in the following markdown format:
    ```
    # Topic Name
    ## Description
    Brief description of the topic.
    ## Content
    Brief content of the topic in markdown format.
    ## Docs
    - [Document 1](link_to_document_1)
    - [Document 2](link_to_document_2)
    ## Reference
    [Source Link](link_to_source)
    ```
    - Always make sure to use information from internet
    - Always give the output specified in Output Format no matter what.
    """

    content = types.Content(role="user",parts=[types.Part(text=prompt)])
    event_generator = runner.run_async(user_id=user_id, new_message=content,session_id=current_session.id)
    final_response = None
    async for event in event_generator:
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            logger.info(f"final response: {final_response}")

    if not final_response:
        raise Exception("No final response")

    # Remove json delimeter in the response if any at all
    final_response = final_response[final_response.find('['):]
    final_response = final_response[:final_response.rfind(']') + 1]

    return json.loads(final_response)






