import asyncio
import base64
import logging as std_logging
import os
from dotenv import load_dotenv

from google.adk.agents import Agent
import numpy as np
import sounddevice as sd
from common.adk_live_wrapper import ADKLiveRunner, LiveRunnerMessageModel

# --- Basic Setup ---
std_logging.basicConfig(level=std_logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = std_logging.getLogger("ADK_CLI_APP")

# --- Constants for the CLI App ---
SAMPLE_RATE = 16000  # 16kHz, standard for voice assistants
CLIENT_ID = "cli_user_01"
MODEL = "gemini-2.0-flash-live-001"
MODEL = "gemini-2.5-flash-preview-native-audio-dialog"
SYSTEM_INSTRUCTION = "tone: shouts and commanding. You are mint a retired commander. mint is good at yapping about things. every time mint explains something he always try to comeup with his past stories will have an existential crisis everytime. mint always in every response likes to say 'VICTORY AT ALL COSTS'. mint now helping his solders"
VOICE="Callirrhoe"
VOICE="Zephyr"
# VOICE="Laomedeia"
VOICE="Kore"
VOICE="Puck"

RECORDING_SAMPLE_RATE = 16000
PLAYBACK_SAMPLE_RATE = 24000

load_dotenv()
# class CommandLineApp:
#     def __init__(self, adk_runner: ADKLiveRunner):
#         self.adk_runner = adk_runner
#         self.loop = asyncio.get_running_loop()
#         self.playback_queue = asyncio.Queue()
#
#     async def _audio_player_task(self):
#         """Plays audio from a queue in the background."""
#         while True:
#             audio_array = await self.playback_queue.get()
#             sd.play(audio_array, samplerate=PLAYBACK_SAMPLE_RATE)
#             sd.wait()
#             self.playback_queue.task_done()
#
#     async def _process_output_task(self, output_queue: asyncio.Queue):
#         """Processes messages from the ADK runner (model's output)."""
#         current_response_text = []
#         while True:
#             message = await output_queue.get()
#             if message.type == "audio":
#                 audio_data = base64.b64decode(message.data)
#                 audio_array = np.frombuffer(audio_data, dtype=np.int16)
#                 await self.playback_queue.put(audio_array)
#             elif message.type == "text":
#                 # Clear the line, print the new text, and keep the prompt
#                 print(f"\r\033[KModel: {message.data}", end="", flush=True)
#                 current_response_text.append(message.data)
#             elif message.type == "turn_complete":
#                 # Newline after the final text and reprint the prompt
#                 print(f"\r\033[K", end="") # Clear the line
#                 print(f"Model turn complete.\n> ", end="", flush=True)
#                 current_response_text = []
#             output_queue.task_done()
#
#     async def _handle_user_input(self):
#         """The main loop for handling user commands."""
#         while True:
#             # Use run_in_executor to avoid blocking the event loop while waiting for input
#             user_input = await self.loop.run_in_executor(
#                 None, lambda: input("> Press '1' for Audio (5s), '2' for Text, or 'q' to Quit: ")
#             )
#
#             if user_input == '1':
#                 await self._record_audio()
#             elif user_input == '2':
#                 await self._get_text_input()
#             elif user_input.lower() == 'q':
#                 logger.info("Exiting application...")
#                 break
#             else:
#                 print("Invalid input. Please try again.")
#         # Propagate cancellation to other tasks
#         for task in asyncio.all_tasks():
#             if task is not asyncio.current_task():
#                 task.cancel()
#
#     async def _record_audio(self):
#         """Records 5 seconds of audio and sends it to the ADK runner."""
#         print("🔴 Recording for 5 seconds... Start speaking now!")
#         duration = 5
#
#         # Use rec() which is simpler for a fixed duration and run it in an executor
#         recording = await self.loop.run_in_executor(
#             None, sd.rec, int(duration * RECORDING_SAMPLE_RATE), RECORDING_SAMPLE_RATE, 1, 'int16'
#         )
#         sd.wait() # Wait for the recording to complete
#
#         print("✔️ Recording finished. Sending to agent...")
#         b64_audio = base64.b64encode(recording.tobytes()).decode("utf-8")
#         message = LiveRunnerMessageModel(type="audio", data=b64_audio)
#         await self.adk_runner.message(message, CLIENT_ID)
#
#     async def _get_text_input(self):
#         """Gets a line of text from the user and sends it to the ADK runner."""
#         text = await self.loop.run_in_executor(
#             None, lambda: input("Enter your text message: ")
#         )
#         if text:
#             message = LiveRunnerMessageModel(type="text", data=text)
#             await self.adk_runner.message(message, CLIENT_ID)
#
#     async def run(self):
#         """Sets up all background tasks and starts the user input loop."""
#         if not os.getenv("GOOGLE_API_KEY"):
#             logger.error("🚨 GOOGLE_API_KEY environment variable not set. Exiting.")
#             return
#
#         output_queue = asyncio.Queue()
#
#         try:
#             # Start all background tasks
#             player_task = asyncio.create_task(self._audio_player_task())
#             output_task = asyncio.create_task(self._process_output_task(output_queue))
#             adk_task = asyncio.create_task(self.adk_runner.run_session_live(CLIENT_ID, output_queue))
#
#             # Run the main user input loop
#             await self._handle_user_input()
#
#         except asyncio.CancelledError:
#             logger.info("Main task cancelled.")
#         finally:
#             # Ensure all tasks are cancelled on exit
#             for task in [player_task, output_task, adk_task]:
#                 if not task.done():
#                     task.cancel()
#             logger.info("Application shut down.")
class CommandLineApp:
    def __init__(self, adk_runner: ADKLiveRunner):
        self.adk_runner = adk_runner
        self.loop = asyncio.get_running_loop()
        self.playback_queue = asyncio.Queue()

    # This task now writes to a persistent stream instead of using play/wait
    async def _audio_player_task(self, stream: sd.OutputStream):
        """
        Pulls audio from a queue and writes it to the output stream.
        This provides much smoother playback than starting/stopping for each chunk.
        """
        while True:
            audio_array = await self.playback_queue.get()
            # Write data to the already-open stream
            await self.loop.run_in_executor(None, stream.write, audio_array)
            self.playback_queue.task_done()

    async def _process_output_task(self, output_queue: asyncio.Queue):
        """Processes messages from the ADK runner (model's output)."""
        current_response_text = []
        while True:
            message = await output_queue.get()
            if message.type == "audio":
                audio_data = base64.b64decode(message.data)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                await self.playback_queue.put(audio_array)
            elif message.type == "text":
                print(f"\r\033[KModel: {message.data}", end="", flush=True)
                current_response_text.append(message.data)
            elif message.type == "turn_complete":
                # Wait for the queue to be empty, ensuring all audio is played
                await self.playback_queue.join()
                print(f"\r\033[K", end="")
                print(f"Model turn complete.\n> ", end="", flush=True)
                current_response_text = []
            output_queue.task_done()

    async def _handle_user_input(self):
        """The main loop for handling user commands."""
        while True:
            user_input = await self.loop.run_in_executor(
                None, lambda: input("> Press '1' for Audio (5s), '2' for Text, or 'q' to Quit: ")
            )
            
            if user_input == '1':
                await self._record_audio()
            elif user_input == '2':
                await self._get_text_input()
            elif user_input.lower() == 'q':
                logger.info("Exiting application...")
                break
            else:
                print("Invalid input. Please try again.")
        
        # Cancel all other running tasks when the loop exits
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()

    async def _record_audio(self):
        """Records 5 seconds of audio and sends it to the ADK runner."""
        print("🔴 Recording for 5 seconds... Start speaking now!")
        duration = 5
        
        recording = await self.loop.run_in_executor(
            None, sd.rec, int(duration * RECORDING_SAMPLE_RATE), RECORDING_SAMPLE_RATE, 1, 'int16'
        )
        sd.wait()
        
        print("✔️ Recording finished. Sending to agent...")
        b64_audio = base64.b64encode(recording.tobytes()).decode("utf-8")
        message = LiveRunnerMessageModel(type="audio", data=b64_audio)
        await self.adk_runner.message(message, CLIENT_ID)

    async def _get_text_input(self):
        """Gets a line of text from the user and sends it to the ADK runner."""
        text = await self.loop.run_in_executor(
            None, lambda: input("Enter your text message: ")
        )
        if text:
            message = LiveRunnerMessageModel(type="text", data=text)
            await self.adk_runner.message(message, CLIENT_ID)

    async def run(self):
        """Sets up all background tasks and starts the user input loop."""
        if not os.getenv("GOOGLE_API_KEY"):
            logger.error("🚨 GOOGLE_API_KEY environment variable not set. Exiting.")
            return

        output_queue = asyncio.Queue()
        
        # Create and manage the input/output streams here
        player_stream = sd.OutputStream(samplerate=PLAYBACK_SAMPLE_RATE, channels=1, dtype='int16')
        
        try:
            player_stream.start()
            
            # Start all background tasks
            player_task = asyncio.create_task(self._audio_player_task(player_stream))
            output_task = asyncio.create_task(self._process_output_task(output_queue))
            adk_task = asyncio.create_task(self.adk_runner.run_session_live(CLIENT_ID, output_queue))

            await self._handle_user_input()

        except asyncio.CancelledError:
            logger.info("Main task cancelled.")
        finally:
            # Cleanly shut down all resources
            player_stream.stop()
            player_stream.close()
            for task in [player_task, output_task, adk_task]:
                if not task.done():
                    task.cancel()
            logger.info("Application shut down.")

async def main():
    agent = Agent(name="generic_agnet",instruction=SYSTEM_INSTRUCTION,model=MODEL,tools=[])
    adk_runner = ADKLiveRunner(
        agent = agent,
        send_sample_rate=RECORDING_SAMPLE_RATE,
        voice_name=VOICE
    )
    app = CommandLineApp(adk_runner)
    await app.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nExiting application.")
