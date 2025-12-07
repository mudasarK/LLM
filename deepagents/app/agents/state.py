from typing import TypedDict, Annotated, List, Dict, Any, Union
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class Todo(TypedDict):
    task: str
    status: str # "pending", "in_progress", "completed"

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    todos: List[Todo]
    files: Dict[str, str]
