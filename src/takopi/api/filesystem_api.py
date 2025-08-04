
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Any
from takopi.services.filesystem_service import FileSystemService
import os

router = APIRouter()

# Set your base path here
BASE_PATH = os.path.abspath("/home/prem/builds/vibe_coding/adk_projects_runner")
fs_service = FileSystemService(BASE_PATH)

class SaveFileRequest(BaseModel):
    relative_path: str
    code: str

@router.get("/fs/structure", response_model=list[dict[str, Any]], summary="Get file structure as flat list")
async def get_file_structure():
    """
    Returns the directory structure as a flat list of dicts with parent-child relationships.
    Each item has: id, name, type (file/directory), parent_id.
    Response:
        [
            {"id": 0, "name": "base_dir", "type": "directory", "parent_id": null},
            {"id": 1, "name": "file1.py", "type": "file", "parent_id": 0},
            {"id": 2, "name": "subdir", "type": "directory", "parent_id": 0},
            {"id": 3, "name": "file2.txt", "type": "file", "parent_id": 2}
        ]
    """
    return fs_service.get_file_structure_nested()

@router.get("/fs/content", summary="Get file content")
async def get_file_content(relative_path: str = Query(description="Path to file, relative to base directory")):
    """
    Returns the content of a file.
    Request:
        GET /fs/content?relative_path=src/main.py
    Response:
        str: File content or error message.
    """
    return {"content": fs_service.get_file_content(relative_path)}

@router.post("/fs/save", summary="Save file")
async def save_file(request: SaveFileRequest):
    """
    Saves code to a file at the given relative path.
    Request:
        {
            "relative_path": "src/new_file.py",
            "code": "print('Hello')"
        }
    Response:
        str: Confirmation or error message.
    """
    return {"result": fs_service.save_file(request.relative_path, request.code)}

@router.delete("/fs/delete", summary="Delete file")
async def delete_file(relative_path: str = Query(description="Path to file, relative to base directory")):
    """
    Deletes a file at the given relative path.
    Request:
        DELETE /fs/delete?relative_path=src/old_file.py
    Response:
        str: Confirmation or error message.
    """
    return {"result": fs_service.delete_file(relative_path)}
