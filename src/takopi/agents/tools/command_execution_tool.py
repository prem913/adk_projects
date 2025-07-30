import subprocess
import os

class CommandExecutionTool:
    """A tool for securely running shell commands within a specified base directory."""

    def __init__(self, base_path: str):
        """
        Initializes the CommandExecutionTool with a base working directory.

        Args:
            base_path (str): The absolute or relative path to the directory that will serve as the root
                             for all command operations. It will be created if it doesn't exist.
        """
        # Resolve the absolute path to prevent ambiguity and store it.
        self.base_path = os.path.abspath(base_path)
        # Create the base directory if it doesn't exist.
        os.makedirs(self.base_path, exist_ok=True)

    def run_command(self, command: str) -> str:
        """
        Spawns a bash shell and runs the given command in the base_path.

        Args:
            command (str): The command to execute.

        Returns:
            str: A string containing the command's exit code, stdout, and stderr.
        """
        try:
            # Using shell=True can be a security risk if the command is from an untrusted source.
            # For this tool, we assume the user (or agent) is trusted.
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=30  # Add a timeout to prevent hanging processes
            )
            output = f"Exit Code: {result.returncode}\n"
            if result.stdout:
                output += f"--- STDOUT ---\n{result.stdout.strip()}\n"
            if result.stderr:
                output += f"--- STDERR ---\n{result.stderr.strip()}\n"
            return output.strip()
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error running command: {e}"


