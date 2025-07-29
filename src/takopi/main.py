from takopi.agents.agent_runner import AgentRunner
from takopi.agents.agent import root_agent
from common.core.logging import logging
import asyncio 
from dotenv import load_dotenv
load_dotenv()

from takopi.agents.prompt import CODER_OUTPUT_KEY

logger = logging.getLogger(__name__)

runner = AgentRunner(root_agent)

async def run():
    session = await runner.get_session("ssesss",initial_state={CODER_OUTPUT_KEY:"coder agent has not been called yet"})
    res = await runner.prompt_agent("Use rich library to use different colors in console also use table to list the todos. Also create a requirement.txt file for the libraries you used",session)


if __name__ == "__main__":
    asyncio.run(run())

