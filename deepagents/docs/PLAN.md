# Deep Agents Implementation Plan

## Overview
This project implements a "Deep Agent" system using FastAPI and LangGraph. Deep Agents are capable of long-horizon tasks through:
1.  **Planning**: Maintaining a TODO list.
2.  **Context Offloading**: Using a virtual filesystem to store information.
3.  **Delegation**: Spawning sub-agents for isolated tasks.

## Architecture

### Tech Stack
-   **Framework**: FastAPI
-   **Agent Framework**: LangGraph, LangChain
-   **LLM**: ChatModel (configurable, e.g., GPT-4o, Claude 3.5 Sonnet)
-   **Runtime**: Python 3.11+

### Project Structure
The project follows a modular FastAPI layout:

```
deepagents/
├── app/
│   ├── main.py              # Application entry point
│   ├── api/                 # API Routes
│   │   └── v1/
│   │       └── endpoints/
│   │           └── agent.py
│   ├── core/                # Core config and utilities
│   │   └── config.py
│   ├── agents/              # Agent Logic
│   │   ├── graph.py         # LangGraph definition
│   │   ├── state.py         # State definition (StateGraph)
│   │   ├── tools/           # Agent Tools
│   │   │   ├── filesystem.py
│   │   │   └── planning.py
│   │   └── subagents.py     # Sub-agent definitions
│   └── schemas/             # Pydantic models
│       └── agent.py
├── requirements.txt
└── .env
```

### Agent Design (LangGraph)

#### State
The agent state will track:
-   `messages`: Chat history.
-   `todos`: List of tasks (pending, in_progress, completed).
-   `files`: Dictionary mapping filenames to content (Virtual Filesystem).

#### Nodes
1.  **Agent**: The main LLM node that decides what to do (call tools, update plan, delegate).
2.  **Tools**: Executes selected tools.

#### Tools
-   **Planning**: `write_todos`, `read_todos`, `update_todo`.
-   **Filesystem**: `write_file`, `read_file`, `ls`, `edit_file`.
-   **Delegation**: `delegate_task` (spawns a sub-agent).

### API Endpoints
-   `POST /agent/run`: Trigger the agent with a user prompt.
-   `GET /agent/{thread_id}/state`: Retrieve the current state (files, plan) of an agent thread.
-   `POST /agent/{thread_id}/chat`: Continue conversation with the agent.

## Implementation Steps
1.  **Setup**: Initialize FastAPI project and dependencies.
2.  **Core**: Implement Configuration and Logging.
3.  **Tools**: Implement Filesystem and Planning tools.
4.  **Agent**: Build the LangGraph agent with state and tools.
5.  **API**: Expose the agent via FastAPI endpoints.
6.  **Testing**: Verify with a complex research task.
