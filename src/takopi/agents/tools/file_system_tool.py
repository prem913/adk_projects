import os

class FileSystemTool:
    """A tool for securely interacting with a local filesystem within a specified base directory."""

    def __init__(self, base_path: str):
        """
        Initializes the FileSystemTool with a base working directory.

        Args:
            base_path (str): The absolute or relative path to the directory that will serve as the root
                             for all file operations. It will be created if it doesn't exist.
        """
        # Resolve the absolute path to prevent ambiguity and store it.
        self.base_path = os.path.abspath(base_path)
        # Create the base directory if it doesn't exist.
        os.makedirs(self.base_path, exist_ok=True)

    def _get_safe_path(self, relative_path: str) -> str:
        """
        Constructs a full path and ensures it's safely within the base directory.
        This prevents directory traversal attacks (e.g., accessing '../../etc/passwd').

        Args:
            relative_path (str): The path relative to the base directory.

        Returns:
            str: The full, validated, and safe absolute path.

        Raises:
            PermissionError: If the resolved path is outside the base directory.
        """
        # Join the base path with the user-provided relative path.
        full_path = os.path.abspath(os.path.join(self.base_path, relative_path))

        # Check if the resolved absolute path is still within the base directory.
        if not full_path.startswith(self.base_path):
            raise PermissionError("Access denied: Path is outside the designated base directory.")
        
        return full_path

    def get_file_structure(self) -> str:
        """
        1. get_file_structure tool: Use this to get the directory structure.
        All paths are shown relative to the base path.

        Returns:
            str: A string representing the directory tree structure.
        """
        tree_string = ""
        try:
            for root, dirs, files in os.walk(self.base_path, topdown=True):
                # Exclude hidden/system directories for a cleaner view
                dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
                files = [f for f in files if not f.startswith('.')]

                relative_root = os.path.relpath(root, self.base_path)
                level = relative_root.count(os.sep) if relative_root != '.' else 0
                
                indent = ' ' * 4 * level
                # Display the directory name
                dir_name = os.path.basename(root) if relative_root != '.' else os.path.basename(self.base_path)
                tree_string += f"{indent}📂 {dir_name}/\n"
                
                sub_indent = ' ' * 4 * (level + 1)
                for f in files:
                    tree_string += f"{sub_indent}📄 {f}\n"
            
            return tree_string.strip() if tree_string else "Base directory is empty."
        except Exception as e:
            return f"Error getting file structure: {e}"

    def get_file_content(self, relative_path: str) -> str:
        """
        2. get_file_content tool: Use this to get the content of a file.
        Input the relative file path you get from the get_file_structure tool.

        Args:
            relative_path (str): The path to the file, relative to the base directory.

        Returns:
            str: The content of the file, or an error message.
        """
        try:
            full_path = self._get_safe_path(relative_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"Error: The file at '{relative_path}' was not found."
        except Exception as e:
            return f"Error reading file '{relative_path}': {e}"

    def save_file(self, relative_path: str, code: str) -> str:
        """
        3. save_file tool: Use this to save the code.
        Input the relative file path and the full code to be saved.

        Args:
            relative_path (str): The path, relative to the base directory, where the file will be saved.
            code (str): The entire content to write to the file.

        Returns:
            str: A confirmation message or an error message.
        """
        try:
            full_path = self._get_safe_path(relative_path)
            
            # Ensure the parent directory for the file exists.
            parent_dir = os.path.dirname(full_path)
            os.makedirs(parent_dir, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code)
            return f"✅ File successfully saved to '{relative_path}'"
        except Exception as e:
            return f"Error saving file '{relative_path}': {e}"
