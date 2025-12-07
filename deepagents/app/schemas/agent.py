from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AgentRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None
    model_name: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    thread_id: str
    files: Dict[str, str] = {}
    todos: List[Dict[str, Any]] = []

class AgentStateResponse(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]
    files: Dict[str, str]
    todos: List[Dict[str, Any]]
