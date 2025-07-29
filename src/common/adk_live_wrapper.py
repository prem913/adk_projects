import asyncio
import json
import base64
from typing import Literal

from google.adk.agents import Agent, LiveRequestQueue,BaseAgent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from common.web_socket import BaseWebSocketServer
from common.core.logging import logging

logger = logging.getLogger(__name__)

class LiveRunnerMessageModel(BaseModel):
    type: Literal["audio", "end", "text","interrupted","turn_complete"]
    data: str

# class ADKLiveRunner():
#     """WebSocket server implementation using Google ADK."""
#
#     def __init__(self,system_instruction: str,model: str,tools: list[type(types.ToolUnion)],name: str = "generic_agent",voice_name: str = "Puck",send_sample_rate = 16000): # pyright: ignore
#
#
#         self.name = name
#         self.send_sample_rate = send_sample_rate
#
#         # Initialize ADK components
#         self.agent = Agent(
#             name=name,
#             model=model,
#             instruction=system_instruction,
#             tools=tools,
#         )
#
#         # Create session service
#         self.session_service = InMemorySessionService()
#
#         # Create runner
#         self.runner = Runner(
#             app_name=self.name,
#             agent=self.agent,
#             session_service=self.session_service,
#         )
#
#
#         # Create run config with audio settings
#         self.run_config = RunConfig(
#             streaming_mode=StreamingMode.BIDI,
#             speech_config=types.SpeechConfig(
#                 voice_config=types.VoiceConfig(
#                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
#                         voice_name=voice_name
#                     )
#                 )
#             ),
#             response_modalities=["AUDIO"],
#             output_audio_transcription=types.AudioTranscriptionConfig(),
#             input_audio_transcription=types.AudioTranscriptionConfig(),
#         )
#
#         self.audio_queue_map: dict[str,asyncio.Queue] = dict()
#
#     async def message(self,message: LiveRunnerMessageModel,client_id: str):
#         logger.info(f"Received message: {message.type}")
#         audio_queue = self.audio_queue_map.get(client_id)
#         try:
#             if message.type is "audio":
#                 # Decode base64 audio data
#                 audio_bytes = base64.b64decode(message.data)
#                 logger.info("Received audio signal from client")
#                 # Put audio in queue for processing
#                 await audio_queue.put(audio_bytes)
#             elif message.type == "end":
#                 # Client is done sending audio for this turn
#                 logger.info("Received end signal from client")
#             elif message.type == "text":
#                 # Handle text messages (not implemented in this simple version)
#                 logger.info(f"Received text: {message.data}")
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON message received")
#         except Exception as e:
#             logger.error(f"Error processing message: {e}")
#
#     async def run_session_live(self,client_id: str,output_queue: asyncio.Queue[LiveRunnerMessageModel]):
#
#         # Create session for this client
#         session = await self.session_service.create_session(
#             app_name=self.name,
#             user_id=f"user_{client_id}",
#             session_id=f"session_{client_id}",
#         )
#         # Queue for audio data from the client
#         audio_queue = None
#         if client_id in self.audio_queue_map:
#             audio_queue = self.audio_queue_map[client_id]
#         else:
#             audio_queue = asyncio.Queue()
#             self.audio_queue_map[client_id] = audio_queue
#
#         # Create live request queue
#         live_request_queue = LiveRequestQueue()
#
#         async with asyncio.TaskGroup() as tg:
#
#             # Task to process and send audio to Gemini
#             async def process_and_send_audio():
#                 while True:
#                     data = await audio_queue.get()
#
#                     # Send the audio data to Gemini through ADK's LiveRequestQueue
#                     logger.info("sending audio to live_request_queue")
#                     live_request_queue.send_realtime(
#                         types.Blob(
#                             data=data,
#                             mime_type=f"audio/pcm;rate={self.send_sample_rate}",
#                         )
#                     )
#
#                     audio_queue.task_done()
#
#             # Task to receive and process responses
#             async def receive_and_process_responses():
#                 # Track user and model outputs between turn completion events
#                 input_texts = []
#                 output_texts = []
#
#                 # Flag to track if we've seen an interruption in the current turn
#                 interrupted = False
#
#                 # Process responses from the agent
#                 async for event in self.runner.run_live(
#                     session=session,
#                     live_request_queue=live_request_queue,
#                     run_config=self.run_config,
#                 ):
#
#                     # Check for turn completion or interruption using string matching
#                     # This is a fallback approach until a proper API exists
#                     event_str = str(event)
#                     logger.info("Event to live_request_queue received")
#                     #print()
#
#                     # Handle audio content
#                     if event.content and event.content.parts:
#                         for part in event.content.parts:
#                             # Process audio content
#                             if hasattr(part, "inline_data") and part.inline_data:
#                                 b64_audio = base64.b64encode(part.inline_data.data).decode("utf-8") # pyright: ignore
#                                 await output_queue.put(LiveRunnerMessageModel(type="audio",data=b64_audio))
#
#                             # Process text content
#                             if hasattr(part, "text") and part.text:
#                                 # Check if this is user or model text based on content role
#                                 if hasattr(event.content, "role") and event.content.role == "user":
#                                     # User text shouldn't be sent to the client
#                                     input_texts.append(part.text)
#                                 else:
#                                     # From the logs, we can see the duplicated text issue happens because
#                                     # we get streaming chunks with "partial=True" followed by a final consolidated
#                                     # response with "partial=None" containing the complete text
#
#                                     # Check in the event string for the partial flag
#                                     # Only process messages with "partial=True"
#                                     if "partial=True" in event_str:
#                                         await output_queue.put(LiveRunnerMessageModel(type="text",data=part.text))
#                                         output_texts.append(part.text)
#                                     # Skip messages with "partial=None" to avoid duplication
#
#
#
#                     # Check for interruption
#                     if event.interrupted  and not interrupted:
#                         logger.info("🤐 INTERRUPTION DETECTED")
#                         await output_queue.put(LiveRunnerMessageModel(type="interrupted",data="Response interrupted by user input"))
#                         interrupted = True
#
#                     # Check for turn completion
#                     if event.turn_complete:
#                         # Only send turn_complete if there was no interruption
#                         if not interrupted:
#                             logger.info("✅ Gemini done talking")
#                             await output_queue.put(LiveRunnerMessageModel(type="turn_complete",data=""))
#
#                         # Log collected transcriptions for debugging
#                         if input_texts:
#                             # Get unique texts to prevent duplication
#                             unique_texts = list(dict.fromkeys(input_texts))
#                             logger.info(f"Input transcription: {' '.join(unique_texts)}")
#
#                         if output_texts:
#                             # Get unique texts to prevent duplication
#                             unique_texts = list(dict.fromkeys(output_texts))
#                             logger.info(f"Output transcription: {' '.join(unique_texts)}")
#
#                         # Reset for next turn
#                         input_texts = []
#                         output_texts = []
#                         interrupted = False
#
#             # Start all tasks
#             tg.create_task(process_and_send_audio())
#             tg.create_task(receive_and_process_responses())


class ADKLiveRunner():
    """WebSocket server implementation using Google ADK."""
    def __init__(self,agent: BaseAgent, name: str = "generic_agent",voice_name: str = "Puck", send_sample_rate=16000):
        self.name = name
        self.send_sample_rate = send_sample_rate
        self.agent = agent
        self.session_service = InMemorySessionService()
        self.runner = Runner(app_name=self.name, agent=self.agent, session_service=self.session_service)
        self.run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name))),
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
        )
        self.audio_queue_map: dict[str, asyncio.Queue] = {}
        # This map will hold the live request queue for each active session
        self.live_request_queue_map: dict[str, LiveRequestQueue] = {}

    async def message(self, message: LiveRunnerMessageModel, client_id: str):
        """Receives a message from the app and forwards it to the correct queue."""
        logger.info(f"Received message: {message.type}")
        
        # --- FIX 1: Make queue creation robust to prevent race condition ---
        # Get the queue for the client, or create it if it doesn't exist yet.
        if client_id not in self.audio_queue_map:
            logger.warning(f"Audio queue for client {client_id} not found. Creating a new one.")
            self.audio_queue_map[client_id] = asyncio.Queue()
        audio_queue = self.audio_queue_map[client_id]
        
        live_request_queue = self.live_request_queue_map.get(client_id)
        
        try:
            # --- FIX 2: Use '==' for correct string comparison ---
            if message.type == "audio":
                audio_bytes = base64.b64decode(message.data)
                logger.info("Received audio signal from client, putting on queue.")
                await audio_queue.put(audio_bytes)
            
            elif message.type == "text":
                if live_request_queue:
                    logger.info(f"Sending text to agent: {message.data}")
                    live_request_queue.send_content(types.Content(parts=[types.Part(text=message.data)]))
                else:
                    logger.error(f"Cannot send text. Live request queue for client {client_id} not available.")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    async def run_session_live(self, client_id: str, output_queue: asyncio.Queue[LiveRunnerMessageModel]):
        session = await self.session_service.create_session(app_name=self.name, user_id=f"user_{client_id}", session_id=f"session_{client_id}")
        
        # Ensure the queues for this session are initialized
        if client_id not in self.audio_queue_map:
            self.audio_queue_map[client_id] = asyncio.Queue()
        audio_queue = self.audio_queue_map[client_id]
        
        live_request_queue = LiveRequestQueue()
        self.live_request_queue_map[client_id] = live_request_queue

        async with asyncio.TaskGroup() as tg:
            async def process_and_send_audio():
                while True:
                    data = await audio_queue.get()
                    logger.info("Sending audio from queue to Google.")
                    live_request_queue.send_realtime(types.Blob(data=data, mime_type=f"audio/pcm;rate={self.send_sample_rate}"))
                    audio_queue.task_done()

            async def receive_and_process_responses():
                logger.info("Starting to listen for responses from Google.")
                async for event in self.runner.run_live(session=session, live_request_queue=live_request_queue, run_config=self.run_config):
                    logger.debug(f"Received event from runner: {event}")
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                                b64_audio = base64.b64encode(part.inline_data.data).decode("utf-8") 
                                await output_queue.put(LiveRunnerMessageModel(type="audio", data=b64_audio))
                            if hasattr(part, "text") and part.text and "partial=True" in str(event):
                                await output_queue.put(LiveRunnerMessageModel(type="text", data=part.text))
                    if event.turn_complete:
                        logger.info("Turn complete event received.")
                        await output_queue.put(LiveRunnerMessageModel(type="turn_complete", data=""))
            
            tg.create_task(process_and_send_audio())
            tg.create_task(receive_and_process_responses())
