"""
Sub-agent Delegation Tools

This module provides tools for the main agent to delegate tasks to specialized sub-agents.
Sub-agents operate in isolated contexts to handle specific tasks.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import logging

logger = logging.getLogger(__name__)


class SubAgent:
    """Represents a specialized sub-agent."""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: Optional[List] = None
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools or []
    
    def execute(self, task: str, model, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a task using this sub-agent.
        
        Args:
            task: The task description
            model: The LLM model to use (should be a base model without tools for sub-agents)
            context: Optional context to pass to the sub-agent
            
        Returns:
            The sub-agent's response
        """
        try:
            from langchain_core.messages import SystemMessage
            
            # Build the prompt
            prompt_parts = [self.system_prompt, f"\n\nTask: {task}"]
            
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt_parts.append(f"\n\nContext:\n{context_str}")
            
            # Use base model without tools for sub-agent execution
            # Get the underlying model if it's bound with tools
            base_model = model
            if hasattr(model, 'model') and hasattr(model, 'bound'):
                # If model is bound with tools, we need to use the base model
                # For now, we'll use the model as-is and hope it doesn't call tools
                base_model = model
            
            messages = [
                SystemMessage(content="\n".join(prompt_parts))
            ]
            
            response = base_model.invoke(messages)
            result = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"Sub-agent {self.name} completed task")
            return result
        except Exception as e:
            logger.error(f"Error in sub-agent {self.name}: {e}", exc_info=True)
            return f"Error: Sub-agent {self.name} failed: {str(e)}"


# Predefined sub-agents
RESEARCH_AGENT = SubAgent(
    name="research-agent",
    description="Specialized in researching topics and gathering information",
    system_prompt="You are a research specialist. Your role is to conduct thorough research on topics, gather relevant information, and provide comprehensive summaries."
)

WRITING_AGENT = SubAgent(
    name="writing-agent",
    description="Specialized in writing and content creation",
    system_prompt="You are a writing specialist. Your role is to create well-structured, clear, and engaging written content based on provided information."
)

ANALYSIS_AGENT = SubAgent(
    name="analysis-agent",
    description="Specialized in analyzing data and information",
    system_prompt="You are an analysis specialist. Your role is to analyze information, identify patterns, and provide insights."
)

# Registry of available sub-agents
SUB_AGENT_REGISTRY: Dict[str, SubAgent] = {
    "research-agent": RESEARCH_AGENT,
    "writing-agent": WRITING_AGENT,
    "analysis-agent": ANALYSIS_AGENT,
}


def delegate_task(
    sub_agent_name: str,
    task: str,
    model,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Delegate a task to a sub-agent.
    
    Args:
        sub_agent_name: Name of the sub-agent to use
        task: Task description
        model: The LLM model instance
        context: Optional context dictionary
        
    Returns:
        Sub-agent's response
    """
    if sub_agent_name not in SUB_AGENT_REGISTRY:
        return f"Error: Unknown sub-agent '{sub_agent_name}'. Available: {', '.join(SUB_AGENT_REGISTRY.keys())}"
    
    sub_agent = SUB_AGENT_REGISTRY[sub_agent_name]
    logger.info(f"Delegating task to {sub_agent_name}: {task[:50]}...")
    return sub_agent.execute(task, model, context)


@tool
def delegate_to_subagent(sub_agent_name: str, task: str):
    """
    Delegate a specific task to a specialized sub-agent.
    
    Args:
        sub_agent_name: The name of the sub-agent to use. Options:
            - research-agent: For research tasks
            - writing-agent: For writing tasks
            - analysis-agent: For analysis tasks
        task: The task description to delegate
        
    Returns:
        The sub-agent's response
    """
    # This is a placeholder. Actual execution happens in the graph node.
    pass


def list_available_subagents() -> str:
    """List all available sub-agents."""
    agents = []
    for name, agent in SUB_AGENT_REGISTRY.items():
        agents.append(f"- {name}: {agent.description}")
    return "\n".join(agents) if agents else "No sub-agents available."
