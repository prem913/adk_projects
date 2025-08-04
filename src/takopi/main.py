
import sys
from fastapi import FastAPI
from takopi.agents.agent_runner import AgentRunner
from takopi.agents.agent import root_agent
from takopi.api.chatbot import router as chatbot_router
from common.core.logging import logging
import asyncio
import uvicorn
from dotenv import load_dotenv
_ = load_dotenv()
from takopi.agents.prompt import CODER_KEY,  RESEARCH_KEY

logger = logging.getLogger(__name__)

async def run():
    runner = AgentRunner(root_agent)
    input_str = ""
    session = await runner.get_session("ssesss",initial_state={CODER_KEY:"coder agent has not been called yet",RESEARCH_KEY: "Research agent has not been called yet"})
    while input_str != "1":
        input_str = str(input("Enter 1 to exit or type the prompt ❯ "))
        res = await runner.prompt_agent(input_str, session)
        logger.warning(f"final response: {res}")

app = FastAPI(title="Agent Runner", version="0.1.0")
app.include_router(chatbot_router)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "server":
            uvicorn.run(app, host="0.0.0.0", port=8000)
        elif mode == "cmd":
            asyncio.run(run())
        else:
            print("Usage: python main.py [server|cmd]")
    else:
        print("Usage: python main.py [server|cmd]")

