from typing import List, Dict, Any
from langchain_core.tools import tool

def read_todos(state_todos: List[Dict[str, Any]]) -> str:
    if not state_todos:
        return "No TODOs."
    result = []
    for i, todo in enumerate(state_todos):
        result.append(f"{i}. [{todo['status']}] {todo['task']}")
    return "\n".join(result)

def add_todo(state_todos: List[Dict[str, Any]], task: str) -> str:
    state_todos.append({"task": task, "status": "pending"})
    return f"Added TODO: {task}"

def update_todo(state_todos: List[Dict[str, Any]], index: int, status: str) -> str:
    if 0 <= index < len(state_todos):
        state_todos[index]["status"] = status
        return f"Updated TODO {index} to {status}"
    return "Error: Invalid TODO index."

@tool
def plan_read_todos():
    """Read the current TODO list."""
    pass

@tool
def plan_add_todo(task: str):
    """Add a new task to the TODO list."""
    pass

@tool
def plan_update_todo(index: int, status: str):
    """Update the status of a TODO item. Status can be 'pending', 'in_progress', 'completed'."""
    pass
