from typing import Dict, List, Optional
from langchain_core.tools import tool

# We will define the logic here, but the actual state update will happen in the graph node
# because tools in LangChain typically just return a string.

def read_file(state_files: Dict[str, str], path: str) -> str:
    if path not in state_files:
        return f"Error: File {path} not found."
    return state_files[path]

def write_file(state_files: Dict[str, str], path: str, content: str) -> str:
    state_files[path] = content
    return f"Successfully wrote to {path}"

def list_files(state_files: Dict[str, str], path: str = "/") -> str:
    # Simple mock LS
    files = list(state_files.keys())
    return f"Files: {', '.join(files)}"

def edit_file(state_files: Dict[str, str], path: str, content: str, mode: str = "replace") -> str:
    """
    Edit a file. Mode can be 'replace' (default), 'append', or 'prepend'.
    
    Args:
        state_files: The files dictionary
        path: File path
        content: Content to add
        mode: 'replace', 'append', or 'prepend'
        
    Returns:
        Success message
    """
    if path not in state_files and mode != "replace":
        return f"Error: File {path} not found. Use 'replace' mode to create a new file."
    
    if mode == "replace":
        state_files[path] = content
        return f"Successfully replaced content in {path}"
    elif mode == "append":
        state_files[path] = state_files.get(path, "") + "\n" + content
        return f"Successfully appended to {path}"
    elif mode == "prepend":
        state_files[path] = content + "\n" + state_files.get(path, "")
        return f"Successfully prepended to {path}"
    else:
        return f"Error: Invalid mode '{mode}'. Use 'replace', 'append', or 'prepend'."

# Tool definitions for the LLM
@tool
def fs_read_file(path: str):
    """Read the content of a file."""
    # This is a placeholder. The actual execution needs state access.
    pass

@tool
def fs_write_file(path: str, content: str):
    """Write content to a file."""
    pass

@tool
def fs_ls(path: str = "/"):
    """List files in the directory."""
    pass

@tool
def fs_edit_file(path: str, content: str, mode: str = "replace"):
    """
    Edit a file. Mode can be 'replace' (default), 'append', or 'prepend'.
    
    Args:
        path: File path
        content: Content to add
        mode: 'replace' (default), 'append', or 'prepend'
    """
    pass
