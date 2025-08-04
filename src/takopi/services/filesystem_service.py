import os
from takopi.agents.tools.file_system_tool import FileSystemTool
from typing import Any 

class FileSystemService:
    """
    Service for interacting with the filesystem using FileSystemTool.
    Provides methods to get file structure (as nested object), get file contents, save file, and delete file.
    """
    def __init__(self, base_path: str):
        self.tool = FileSystemTool(base_path)

    def get_file_structure_nested(self) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """
        Returns the directory structure as a flat list of dicts with parent-child relationships.
        Each item has: id, name, type (file/directory), parent_id.
        This format is easier for frontend tree components.
        """
        result = []
        id_counter = [0]

        def add_node(path: str, parent_id: int | None = None):
            node_id = id_counter[0]
            id_counter[0] += 1
            name = os.path.basename(path)
            if os.path.isdir(path):
                node = {"id": node_id, "name": name, "type": "directory", "parent_id": parent_id}
                result.append(node)
                for entry in os.listdir(path):
                    if entry.startswith('.') or entry.startswith('__'):
                        continue
                    add_node(os.path.join(path, entry), node_id)
            else:
                node = {"id": node_id, "name": name, "type": "file", "parent_id": parent_id}
                result.append(node)

        add_node(self.tool.base_path)
        return result

    def get_file_content(self, relative_path: str) -> str:
        """
        Returns the content of a file.
        Args:
            relative_path (str): Path to the file, relative to base directory.
        Returns:
            str: File content or error message.
        """
        return self.tool.get_file_content(relative_path)

    def save_file(self, relative_path: str, code: str) -> str:
        """
        Saves code to a file at the given relative path.
        Args:
            relative_path (str): Path to save file, relative to base directory.
            code (str): Content to write.
        Returns:
            str: Confirmation or error message.
        """
        return self.tool.save_file(relative_path, code)

    def delete_file(self, relative_path: str) -> str:
        """
        Deletes a file at the given relative path.
        Args:
            relative_path (str): Path to file, relative to base directory.
        Returns:
            str: Confirmation or error message.
        """
        return self.tool.delete_file(relative_path)
