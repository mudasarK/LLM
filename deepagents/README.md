# Deep Agents API

A production-ready FastAPI implementation of Deep Agents using LangGraph and LangChain. Deep Agents are capable of handling long-horizon tasks through planning, context offloading, and sub-agent delegation.

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd deepagents

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY

# 4. Run the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5. Open your browser
# Navigate to: http://localhost:8000
```

That's it! The web UI will load automatically at **http://localhost:8000** and you can start chatting with the agent.

> 💡 **Tip**: The UI is served directly from the FastAPI server - no separate frontend server needed!

## Features

- **Task Planning**: Maintains TODO lists for complex multi-step workflows
- **Virtual Filesystem**: Stores information in a virtual filesystem for context management
- **Tool Execution**: Executes filesystem and planning tools with state management
- **Persistent Memory**: Thread-based conversation memory using LangGraph checkpointing
- **Web UI**: Modern, responsive web interface for interacting with the agent
- **Production-Ready**: Comprehensive error handling, logging, and API best practices

## Architecture

```
deepagents/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   └── v1/
│   │       └── endpoints/
│   │           └── agent.py # Agent endpoints
│   ├── core/                # Core configuration
│   │   └── config.py
│   ├── agents/              # Agent logic
│   │   ├── graph.py         # LangGraph definition
│   │   ├── state.py         # State definition
│   │   └── tools/           # Agent tools
│   │       ├── filesystem.py
│   │       └── planning.py
│   └── schemas/             # Pydantic models
│       └── agent.py
├── ui/                      # Web UI
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── requirements.txt
├── .env.example
└── README.md
```

### What's Included

```
deepagents/
├── app/                    # Backend (FastAPI + LangGraph)
│   ├── main.py            # Application entry (serves UI + API)
│   ├── core/              # Configuration management
│   ├── agents/            # Agent logic + tools
│   ├── api/               # REST API endpoints
│   └── schemas/           # Pydantic models
├── ui/                     # Frontend (HTML/CSS/JS)
│   ├── templates/         # HTML templates
│   └── static/            # CSS + JavaScript
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
└── README.md             # This file
```

## Installation

1. **Clone or navigate to the project**:
   ```bash
   cd deepagents
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# You only need ONE API key (OpenAI OR Anthropic, not both required)
# Priority: OpenAI is checked first, then Anthropic
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server configuration (optional)
HOST=0.0.0.0
PORT=8000

# Model configuration (optional)
DEFAULT_MODEL=gpt-4o  # Used with OpenAI
DEFAULT_ANTHROPIC_MODEL=claude-3-5-sonnet-20240620  # Used with Anthropic
```

> 💡 **Why both?** The system supports both providers for flexibility, but you only need **one** API key. Choose based on your preference:
> - **OpenAI (GPT-4o)**: Fast, cost-effective, great for general tasks
> - **Anthropic (Claude 3.5 Sonnet)**: Excellent reasoning, better for complex analysis

## Usage

### Starting the Server

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or using the main module:

```bash
python3 app/main.py
```

The server will start on http://localhost:8000

### Using the Web UI

Once the server is running, simply open your browser and navigate to:

**http://localhost:8000**

> 🎨 The UI loads automatically - no additional setup needed!

The web UI provides:
- 💬 **Chat Interface**: Interact with the agent through a modern chat interface
- 📁 **File Viewer**: View and browse files created by the agent
- ✓ **TODO Tracker**: Monitor task progress with status indicators
- ⚙️ **Settings**: Configure the API URL

**Features**:
- Real-time updates of files and TODOs
- Markdown-style message formatting
- Persistent conversation threads
- Responsive design for mobile and desktop

### API Endpoints

You can also interact directly with the API:

#### 1. Invoke Agent

**POST** `/api/v1/agent/invoke`

Invoke the Deep Agent with a query.

**Request Body**:
```json
{
  "query": "Create a plan to learn Rust, write it to plan.txt, and add the first step to TODOs.",
  "thread_id": "optional-thread-id"
}
```

**Response**:
```json
{
  "response": "I have created the plan and added the first task.",
  "thread_id": "abc-123",
  "files": {
    "plan.txt": "1. Learn Rust basics\n2. Build a project"
  },
  "todos": [
    {"task": "Learn Rust basics", "status": "pending"}
  ]
}
```

#### 2. Get Agent State

**GET** `/api/v1/agent/{thread_id}/state`

Retrieve the current state of an agent thread.

**Response**:
```json
{
  "thread_id": "abc-123",
  "messages": [...],
  "files": {...},
  "todos": [...]
}
```

#### 3. Health Check

**GET** `/health`

Check if the API is running.

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Agent Capabilities

### Planning Tools

- `plan_read_todos()`: Read the current TODO list
- `plan_add_todo(task: str)`: Add a new task to the TODO list
- `plan_update_todo(index: int, status: str)`: Update task status (pending/in_progress/completed)

### Filesystem Tools

- `fs_read_file(path: str)`: Read file content
- `fs_write_file(path: str, content: str)`: Write content to a file
- `fs_ls(path: str)`: List files in the virtual filesystem

## Example Usage

### Python Client

```python
import httpx

# Invoke the agent
response = httpx.post(
    "http://localhost:8000/api/v1/agent/invoke",
    json={
        "query": "Research LangGraph and write a summary to summary.md"
    },
    timeout=60.0
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Files: {data['files']}")
print(f"TODOs: {data['todos']}")

# Get state
thread_id = data['thread_id']
state = httpx.get(f"http://localhost:8000/api/v1/agent/{thread_id}/state")
print(state.json())
```

### cURL

```bash
# Invoke agent
curl -X POST "http://localhost:8000/api/v1/agent/invoke" \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a TODO list for building a web app"}'

# Get state
curl "http://localhost:8000/api/v1/agent/{thread_id}/state"
```

## Development

### Running Tests

```bash
python3 test_agent.py
```

### Project Structure

- **app/main.py**: FastAPI application with CORS, logging, and lifespan management
- **app/agents/graph.py**: LangGraph agent implementation with tool execution
- **app/agents/state.py**: TypedDict state definition for the agent
- **app/agents/tools/**: Tool implementations (filesystem, planning)
- **app/api/v1/endpoints/**: API endpoint definitions
- **app/core/config.py**: Configuration management using Pydantic Settings
- **app/schemas/**: Pydantic models for request/response validation

## Best Practices Implemented

1. **Modular Architecture**: Clear separation of concerns (API, agents, tools, config)
2. **Type Safety**: Full type hints and Pydantic models
3. **Error Handling**: Comprehensive try-catch blocks with proper HTTP status codes
4. **Logging**: Structured logging throughout the application
5. **Configuration**: Environment-based configuration with sensible defaults
6. **Documentation**: Docstrings, type hints, and API documentation
7. **State Management**: Thread-based conversation memory with LangGraph checkpointing

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **LangChain**: Framework for developing applications powered by language models
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI applications

## License

This project is part of the LLM development workspace.

## Additional Documentation

- **[UI Guide](UI_GUIDE.md)**: Detailed guide on accessing the UI and understanding API key configuration
- **[UI Comparison](UI_COMPARISON.md)**: Comparison between our UI and the official deep-agents-ui
- **[Enhancements](docs/ENHANCEMENTS.md)**: List of all enhancements made to the project
- **[Test Documentation](tests/README.md)**: How to run the comprehensive test suite

## ⚠️ UI Note: Official vs Our Implementation

**Important:** Our UI at `http://localhost:8000` is **different** from the official [deep-agents-ui](https://github.com/langchain-ai/deep-agents-ui):

- **Official UI**: Next.js/React app that connects to LangGraph deployments (requires separate LangGraph server)
- **Our UI**: Simple HTML/JS integrated with our FastAPI backend (single server, no build step)

See [UI_COMPARISON.md](UI_COMPARISON.md) for detailed differences and when to use each.

## References

- [LangChain Deep Agents](https://github.com/langchain-ai/deepagents)
- [Deep Agents from Scratch](https://github.com/langchain-ai/deep-agents-from-scratch)
- [Deep Agents UI](https://github.com/langchain-ai/deep-agents-ui)
