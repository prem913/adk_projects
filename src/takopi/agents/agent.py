from google.adk.agents import Agent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import google_search

from takopi.agents.tools.command_execution_tool import CommandExecutionTool
from .prompt import (
    analyser_agent_prompt,
    coder_agent_prompt,
    testing_agent_prompt,
    initial_agent_prompt,
    ERROR_KEY,
    INITIAL_KEY,
    RESEARCH_KEY,
    CODER_KEY,
    ANALYSE_KEY,
)
from .tools.file_system_tool import FileSystemTool
from .tools.internet_tool import InternetTools
from .tools.rag_tool import RAGTool
from ..service.rag_service import RAGService
from time import sleep
from common.core.logging import logging

logger = logging.getLogger(__name__)

project_base_path = "/home/prem/builds/vibe_coding/adk_projects_runner"

file_system_tool = FileSystemTool(base_path=project_base_path)
command_execution_tool = CommandExecutionTool(base_path=project_base_path)
internet_tool = InternetTools()
rag_service = RAGService()
rag_tool = RAGTool(rag_service)

common_tools = [
    file_system_tool.get_file_content,
    file_system_tool.get_file_structure,
    file_system_tool.save_file,
]


def _callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    logger.info(
        f"💤 Sleeping for 5 second. CallbackContext: {callback_context} llm_request: {llm_request}"
    )
    sleep(5)
    logger.info("💤 Sleeping Done")
    return None


MODEL = "gemini-2.5-flash"

initial_agent = Agent(
    name="initial_agent",
    model=MODEL,
    description=("Initial Agent that Outlines a Plan for research agent"),
    instruction=initial_agent_prompt,
    tools=[file_system_tool.get_file_structure, file_system_tool.get_file_content,rag_tool.knowledge_sensei],
    output_key=INITIAL_KEY,
    before_model_callback=_callback,
)
research_agent = Agent(
    name="research_agent",
    model=MODEL,
    description=(
        "Agent that research the internet and gives a very detailed summary of the topics asked"
    ),
    instruction="Use google_search tool to find the answer to the question ,research about topics, if it is about coding try to get as many coding related topics and give a very detailed summary of the topics asked by the analyser agent. Analyser agent output: {initial_agent_output}",
    tools=[google_search],
    output_key=RESEARCH_KEY,
)

analyser_agent = Agent(
    name="analyser_agent",
    model=MODEL,
    description=(
        "Agent That Analyses the Current Code and User Requirements and Outlines a Plan"
    ),
    instruction=analyser_agent_prompt,
    tools=[*common_tools,rag_tool.knowledge_sensei],
    output_key=ANALYSE_KEY,
    before_model_callback=_callback,
)
coder_agent = Agent(
    name="coder_agent",
    model=MODEL,
    description=("Agent that Generates Code"),
    instruction=coder_agent_prompt,
    tools=[*common_tools, file_system_tool.delete_file,rag_tool.knowledge_sensei],
    output_key=CODER_KEY,
    before_model_callback=_callback,
)
test_agent = Agent(
    name="test_agent",
    model=MODEL,
    description=("Agent that tests Code and reports errors"),
    instruction=testing_agent_prompt,
    tools=[command_execution_tool.run_command, *common_tools],
    output_key=ERROR_KEY,
    before_model_callback=_callback,
)


root_agent = LoopAgent(
    name="coding_agent",
    sub_agents=[analyser_agent, coder_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    max_iterations=1,
)
