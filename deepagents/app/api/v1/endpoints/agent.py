"""
Agent API Endpoints

This module defines the FastAPI endpoints for interacting with the Deep Agent.
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import json

from app.schemas.agent import AgentRequest, AgentResponse, AgentStateResponse
from app.agents.graph import graph

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/invoke", response_model=AgentResponse, status_code=status.HTTP_200_OK)
@router.post("/run", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def invoke_agent(request: AgentRequest):
    """
    Invoke the Deep Agent with a query.
    
    Args:
        request: Agent request containing query and optional thread_id
        
    Returns:
        Agent response with results, files, and todos
        
    Raises:
        HTTPException: If agent execution fails
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Invoking agent for thread {thread_id}")
    logger.debug(f"Query: {request.query}")
    
    try:
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        # Run the graph until completion
        final_state = graph.invoke(inputs, config=config)
        
        messages = final_state.get("messages", [])
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent produced no response"
            )
        
        last_message = messages[-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        logger.info(f"Agent completed successfully for thread {thread_id}")
        
        return AgentResponse(
            response=str(response_text),
            thread_id=thread_id,
            files=final_state.get("files", {}),
            todos=final_state.get("todos", [])
        )
        
    except ValueError as e:
        # Configuration errors (e.g., missing API key)
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error invoking agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/{thread_id}/state", response_model=AgentStateResponse)
async def get_agent_state(thread_id: str):
    """
    Retrieve the current state of an agent thread.
    
    Args:
        thread_id: Thread identifier
        
    Returns:
        Current agent state including messages, files, and todos
        
    Raises:
        HTTPException: If thread not found or state retrieval fails
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Retrieving state for thread {thread_id}")
    
    try:
        state_snapshot = graph.get_state(config)
        
        if not state_snapshot.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread {thread_id} not found"
            )
        
        values = state_snapshot.values
        
        # Serialize messages for JSON response
        serialized_messages = []
        for msg in values.get("messages", []):
            if hasattr(msg, 'model_dump'):
                serialized_messages.append(msg.model_dump())
            else:
                # Fallback for messages without model_dump
                serialized_messages.append({
                    "type": msg.__class__.__name__,
                    "content": str(msg.content) if hasattr(msg, 'content') else str(msg)
                })
        
        logger.info(f"State retrieved successfully for thread {thread_id}")
        
        return AgentStateResponse(
            thread_id=thread_id,
            messages=serialized_messages,
            files=values.get("files", {}),
            todos=values.get("todos", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving state: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve state: {str(e)}"
        )


@router.post("/{thread_id}/chat", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def chat_with_agent(thread_id: str, request: AgentRequest):
    """
    Continue conversation with an existing agent thread.
    
    Args:
        thread_id: Thread identifier
        request: Agent request containing query
        
    Returns:
        Agent response with results, files, and todos
        
    Raises:
        HTTPException: If agent execution fails or thread not found
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Continuing chat for thread {thread_id}")
    logger.debug(f"Query: {request.query}")
    
    # Verify thread exists
    try:
        state_snapshot = graph.get_state(config)
        if not state_snapshot.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread {thread_id} not found"
            )
    except Exception as e:
        logger.error(f"Error checking thread existence: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found"
        )
    
    try:
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        # Run the graph until completion
        final_state = graph.invoke(inputs, config=config)
        
        messages = final_state.get("messages", [])
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent produced no response"
            )
        
        last_message = messages[-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        logger.info(f"Chat completed successfully for thread {thread_id}")
        
        return AgentResponse(
            response=str(response_text),
            thread_id=thread_id,
            files=final_state.get("files", {}),
            todos=final_state.get("todos", [])
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.post("/stream")
async def stream_agent(request: AgentRequest):
    """
    Stream agent responses using LangGraph streaming.
    
    Args:
        request: Agent request containing query and optional thread_id
        
    Yields:
        Server-Sent Events with agent state updates
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Streaming agent for thread {thread_id}")
    
    async def generate():
        try:
            # LangGraph with checkpointer automatically loads previous state
            # The add_messages reducer will append the new message to existing messages
            inputs = {"messages": [HumanMessage(content=request.query)]}
            
            # Stream the graph execution
            # LangGraph astream yields events with node names as keys
            async for event in graph.astream(inputs, config=config, stream_mode="values"):
                # Event is a dict with state updates
                if isinstance(event, dict):
                    # Send state updates for files and todos
                    if "files" in event or "todos" in event:
                        state_data = {
                            "type": "state_update",
                            "thread_id": thread_id,
                            "files": event.get("files", {}),
                            "todos": event.get("todos", [])
                        }
                        yield f"data: {json.dumps(state_data)}\n\n"
                    
                    # Send message content updates
                    if "messages" in event:
                        messages = event["messages"]
                        if messages:
                            last_msg = messages[-1]
                            # Check if it's an AIMessage with content
                            if hasattr(last_msg, "content") and last_msg.content:
                                # Only send AI messages (not tool messages or system messages)
                                msg_type = type(last_msg).__name__
                                if msg_type == "AIMessage":
                                    content_data = {
                                        "type": "content",
                                        "content": str(last_msg.content)
                                    }
                                    yield f"data: {json.dumps(content_data)}\n\n"
            
            # Final state
            final_state = graph.get_state(config)
            if final_state.values:
                final_data = {
                    "type": "complete",
                    "thread_id": thread_id,
                    "files": final_state.values.get("files", {}),
                    "todos": final_state.values.get("todos", [])
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in stream: {e}", exc_info=True)
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
