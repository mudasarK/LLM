"""
Deep Agent Graph Implementation

This module defines the LangGraph-based agent that handles:
- Task planning with TODO lists
- Virtual filesystem operations
- Tool execution and state management
"""

from typing import Literal, Optional
import logging

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import get_settings
from app.agents.state import AgentState
from app.agents.tools.filesystem import (
    fs_read_file, fs_write_file, fs_ls, fs_edit_file,
    read_file, write_file, list_files, edit_file
)
from app.agents.tools.planning import (
    plan_read_todos, plan_add_todo, plan_update_todo,
    read_todos, add_todo, update_todo
)
from app.agents.tools.subagents import (
    delegate_to_subagent,
    delegate_task,
    list_available_subagents
)

logger = logging.getLogger(__name__)
settings = get_settings()

# System prompt for the agent
SYSTEM_PROMPT = """You are a Deep Agent capable of planning and executing complex tasks.

You have access to:
1. A virtual filesystem (fs_read_file, fs_write_file, fs_ls, fs_edit_file)
2. A TODO list for task planning (plan_read_todos, plan_add_todo, plan_update_todo)
3. Sub-agent delegation (delegate_to_subagent) for specialized tasks

Available Sub-agents:
- research-agent: For research tasks and information gathering
- writing-agent: For writing and content creation
- analysis-agent: For data analysis and insights

Best Practices:
- Start by breaking down complex tasks into a plan using `plan_add_todo`
- Use the filesystem to store your work and intermediate results
- Delegate specialized tasks to sub-agents when appropriate
- Mark tasks as completed using `plan_update_todo` with status 'completed'
- Keep your responses concise and focused on task execution
"""

# Define available tools
TOOLS = [
    fs_read_file, fs_write_file, fs_ls, fs_edit_file,
    plan_read_todos, plan_add_todo, plan_update_todo,
    delegate_to_subagent
]


def create_model() -> BaseChatModel:
    """
    Create and configure the LLM model.
    
    Returns:
        Configured chat model instance
    """
    if settings.OPENAI_API_KEY:
        logger.info(f"Initializing OpenAI model: {settings.DEFAULT_MODEL}")
        return ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0
        )
    elif settings.ANTHROPIC_API_KEY:
        logger.info(f"Initializing Anthropic model: {settings.DEFAULT_ANTHROPIC_MODEL}")
        return ChatAnthropic(
            model=settings.DEFAULT_ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0
        )
    else:
        logger.warning("No API key provided. Agent will not function properly.")
        raise ValueError(
            "No LLM API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY "
            "in your environment or .env file."
        )


# Lazy model initialization
_model_instance: Optional[BaseChatModel] = None


def get_model() -> BaseChatModel:
    """Get or create the model instance with tools bound."""
    global _model_instance
    if _model_instance is None:
        _model_instance = create_model().bind_tools(TOOLS)
    return _model_instance


def agent_node(state: AgentState) -> dict:
    """
    Main agent node that invokes the LLM.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with new messages
    """
    messages = state["messages"]
    
    # Filter out system messages and add fresh one
    filtered_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
    
    # Add system prompt at the beginning
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + filtered_messages
    
    try:
        model = get_model()
        response = model.invoke(messages_with_system)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"Error in agent_node: {e}", exc_info=True)
        error_msg = AIMessage(content=f"Error: {str(e)}")
        return {"messages": [error_msg]}


def tools_node(state: AgentState) -> dict:
    """
    Execute tool calls from the agent.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with tool results and modified files/todos
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": []}
    
    tool_calls = last_message.tool_calls
    results = []
    
    # Copy state to modify safely
    files = state.get("files", {}).copy()
    todos = [{**todo} for todo in state.get("todos", [])]  # Deep copy of list and dicts
    
    for tool_call in tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        try:
            # Execute tool based on name
            if name == "fs_read_file":
                result_text = read_file(files, args["path"])
            elif name == "fs_write_file":
                result_text = write_file(files, args["path"], args["content"])
            elif name == "fs_ls":
                result_text = list_files(files, args.get("path", "/"))
            elif name == "fs_edit_file":
                result_text = edit_file(files, args["path"], args["content"], args.get("mode", "replace"))
            elif name == "plan_read_todos":
                result_text = read_todos(todos)
            elif name == "plan_add_todo":
                result_text = add_todo(todos, args["task"])
            elif name == "plan_update_todo":
                result_text = update_todo(todos, args["index"], args["status"])
            elif name == "delegate_to_subagent":
                # Get the base model (without tools) for sub-agent execution
                # Sub-agents should use the base model to avoid tool recursion
                base_model = create_model()  # Get base model without tools
                sub_agent_name = args.get("sub_agent_name", "")
                task = args.get("task", "")
                # Extract context from files if needed
                context = {"files": list(files.keys())} if files else None
                result_text = delegate_task(sub_agent_name, task, base_model, context)
            else:
                result_text = f"Error: Unknown tool '{name}'"
                logger.warning(f"Unknown tool called: {name}")
                
        except Exception as e:
            result_text = f"Error executing {name}: {str(e)}"
            logger.error(f"Tool execution error: {e}")
            
        results.append(ToolMessage(tool_call_id=tool_call_id, content=result_text))
    
    return {
        "messages": results,
        "files": files,
        "todos": todos
    }


def should_continue(state: AgentState) -> Literal["tools", END]:
    """
    Determine if the agent should continue or end.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END


# Build the graph
def create_graph():
    """Create and compile the agent graph."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    # Compile with checkpointer for memory
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Create the graph instance
graph = create_graph()
