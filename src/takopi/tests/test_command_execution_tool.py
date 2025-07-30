import pytest
import os
import shutil
import tempfile
# Assuming your CommandExecutionTool class is in 'command_execution_tool.py'
from ..agents.tools.command_execution_tool import CommandExecutionTool

@pytest.fixture
def cmd_tool():
    """
    A pytest fixture that sets up a CommandExecutionTool instance in a temporary
    directory before each test and cleans it up afterwards.
    """
    # --- Setup ---
    test_dir = tempfile.mkdtemp(prefix="cmd_tool_pytest_")
    tool = CommandExecutionTool(base_path=test_dir)
    
    # Yield the tool instance to the test function
    yield tool
    
    # --- Teardown ---
    shutil.rmtree(test_dir)

def test_run_command_creates_file(cmd_tool):
    """
    Test running a shell command that creates a file.
    """
    command = "echo 'hello from command' > output.txt"
    result = cmd_tool.run_command(command)

    # Assert that the command ran successfully
    assert "Exit Code: 0" in result
    assert "STDERR" not in result

    # Verify the file was created in the tool's base_path
    output_file_path = os.path.join(cmd_tool.base_path, "output.txt")
    assert os.path.exists(output_file_path)

    with open(output_file_path, 'r') as f:
        content = f.read()
    assert "hello from command" in content

def test_run_command_with_error(cmd_tool):
    """
    Test running a command that produces an error.
    """
    command = "cat non_existent_file.txt"
    result = cmd_tool.run_command(command)

    assert "Exit Code: 1" in result
    assert "STDERR" in result
    # Error message can vary between systems, so we check for common phrases
    assert "No such file or directory" in result or "cannot open" in result

def test_run_command_lists_directory(cmd_tool):
    """
    Test running a command to list the contents of the directory.
    """
    # Create a file to be listed
    with open(os.path.join(cmd_tool.base_path, "file_to_list.txt"), "w") as f:
        f.write("list me")
    
    # Use 'ls -a' to be more platform-agnostic than just 'ls'
    command = "ls -a"
    result = cmd_tool.run_command(command)

    assert "Exit Code: 0" in result
    assert "STDOUT" in result
    assert "file_to_list.txt" in result


