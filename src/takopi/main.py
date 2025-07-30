from takopi.agents.agent_runner import AgentRunner
from takopi.agents.agent import root_agent
from common.core.logging import logging
import asyncio 
from dotenv import load_dotenv
load_dotenv()

from takopi.agents.prompt import CODER_OUTPUT_KEY, ERROR_KEY

logger = logging.getLogger(__name__)

runner = AgentRunner(root_agent)
prompt = """
Use the shadcn componets present in the project as much as possible.Add A floating button in all pages when clicked on it a chatbot window will open and sending prompt.use mock responses for now.The window should take full heigh and half of the page width.
"""
async def run():
    input_str = ""
    session = await runner.get_session("ssesss",initial_state={CODER_OUTPUT_KEY:"coder agent has not been called yet",ERROR_KEY: "Error agent has not been called yet"})
    while input_str != "1":
        input_str = str(input("Enter 1 to exit or type the prompt ❯ "))
        res = await runner.prompt_agent(input_str,session)
        logger.warning(f"final response: {res}")



if __name__ == "__main__":
    asyncio.run(run())

