import pytest
import os
import shutil
import tempfile
from ..agents.tools.file_system_tool import FileSystemTool

# Pytest Fixture for Setup and Teardown
@pytest.fixture
def fs_tool():
    """
    A pytest fixture that sets up a FileSystemTool instance in a temporary
    directory before each test and cleans it up afterwards.
    """
    # Create a unique, temporary directory for the test
    test_dir = tempfile.mkdtemp(prefix="fs_tool_pytest_")
    # Instantiate the tool with this temporary directory as its base
    tool = FileSystemTool(base_path=test_dir)
    
    # Yield the tool instance to the test function
    yield tool
    
    # --- Teardown ---
    # This code runs after the test function completes
    shutil.rmtree(test_dir)

# --- Test Functions ---

def test_initialization_creates_base_path(fs_tool):
    """
    Test that the base directory is created upon initialization.
    """
    assert os.path.isdir(fs_tool.base_path)

def test_get_safe_path_security(fs_tool):
    """
    Test the _get_safe_path method to ensure it prevents directory traversal.
    """
    # Test a valid path
    safe_path = fs_tool._get_safe_path('a/b/c.txt')
    assert safe_path.startswith(fs_tool.base_path)

    # Test for directory traversal attack using pytest.raises
    with pytest.raises(PermissionError, match="Access denied"):
        fs_tool._get_safe_path('../../etc/passwd')
        
    # Test another tricky path that could lead to traversal
    with pytest.raises(PermissionError, match="Access denied"):
        fs_tool._get_safe_path('../somefile')

def test_save_and_get_file_content(fs_tool):
    """
    Test saving a file and then retrieving its content.
    """
    relative_path = 'test_file.txt'
    content = "Hello, this is a pytest test.\nLine 2."
    
    # Test saving the file
    save_msg = fs_tool.save_file(relative_path, content)
    assert "successfully saved" in save_msg
    
    # Verify the file physically exists
    full_path = os.path.join(fs_tool.base_path, relative_path)
    assert os.path.exists(full_path)
    
    # Test reading the content back
    read_content = fs_tool.get_file_content(relative_path)
    assert content == read_content

def test_save_file_in_subdirectory(fs_tool):
    """
    Test that save_file can create necessary subdirectories.
    """
    relative_path = os.path.join('src', 'app', 'main.py')
    content = "if __name__ == '__main__':\n    pass"
    
    fs_tool.save_file(relative_path, content)
    
    full_path = os.path.join(fs_tool.base_path, relative_path)
    assert os.path.exists(full_path)
    
    read_content = fs_tool.get_file_content(relative_path)
    assert content == read_content

def test_get_file_content_non_existent_file(fs_tool):
    """
    Test getting content from a file that does not exist.
    """
    relative_path = 'non_existent_file.py'
    error_msg = fs_tool.get_file_content(relative_path)
    assert "was not found" in error_msg

def test_get_file_structure_empty(fs_tool):
    """
    Test the file structure of an empty directory.
    """

    base_dir_name = os.path.basename(fs_tool.base_path)
    expected_structure = f"📂 {base_dir_name}/"
    assert fs_tool.get_file_structure() == expected_structure

def test_get_file_structure_with_content(fs_tool):
    """
    Test the file structure output for a populated directory.
    """
    # Create some files and directories
    fs_tool.save_file('README.md', '# Test')
    fs_tool.save_file(os.path.join('src', 'main.py'), 'print("hello")')
    fs_tool.save_file(os.path.join('data', 'config.json'), '{}')

    structure = fs_tool.get_file_structure()

    # Assert that key files and directories are mentioned in the structure string
    assert 'README.md' in structure
    assert 'src/' in structure
    assert 'main.py' in structure
    assert 'data/' in structure
    assert 'config.json' in structure
