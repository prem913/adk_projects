from google.adk.agents import Agent,LoopAgent
from .prompt import CODER_OUTPUT_KEY, OUTLINE_KEY, analyser_agent_prompt, coder_agent_prompt
from .tools.file_system_tool import FileSystemTool

file_system_tool = FileSystemTool(base_path="coding_agent_test")

common_tools = [
    file_system_tool.get_file_content,
    file_system_tool.get_file_structure,
    file_system_tool.save_file,
]


analyser_agent = Agent(
    name="analyser_agent",
    model="gemini-2.5-flash",
    description=("Agent That Analyses the Current Code and User Requirements and Outlines a Plan"),
    instruction=analyser_agent_prompt,
    tools = [*common_tools],
    output_key=OUTLINE_KEY
)
coder_agent = Agent(
    name="coder_agent",
    model="gemini-2.5-flash",
    description=("Agent that Generates Code"),
    instruction=coder_agent_prompt,
    tools = [*common_tools],
    output_key=CODER_OUTPUT_KEY
)

root_agent = LoopAgent(
    name="coding_agent",
    sub_agents=[analyser_agent,coder_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    max_iterations=1
)
