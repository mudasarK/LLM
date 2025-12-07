# Deep Agents Test Suite

## Overview

Comprehensive test suite for the Deep Agents API that tests all features including:
- ✅ Health check endpoint
- ✅ Agent invocation (`/invoke` and `/run`)
- ✅ State retrieval (`/state`)
- ✅ Chat continuity (`/chat`)
- ✅ Filesystem operations (read, write, list, edit)
- ✅ Planning operations (TODOs: read, add, update)
- ✅ Sub-agent delegation (research, writing, analysis agents)
- ✅ Complex multi-step workflows

## Prerequisites

1. **Install dependencies:**
   ```bash
   cd /path/to/deepagents
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)
   ```

3. **Start the server:**
   ```bash
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Running Tests

### Option 1: Using the test runner script (Recommended)

```bash
cd /path/to/deepagents
./tests/run_tests.sh
```

The script will:
- Check if dependencies are installed
- Check if the server is running
- Offer to start the server if needed
- Run all tests
- Clean up background processes

### Option 2: Manual execution

1. **Start the server** (in one terminal):
   ```bash
   cd /path/to/deepagents
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Run tests** (in another terminal):
   ```bash
   cd /path/to/deepagents
   python3 tests/test_agent.py
   ```

## Test Coverage

### API Endpoints
- `GET /health` - Health check
- `POST /api/v1/agent/invoke` - Invoke agent
- `POST /api/v1/agent/run` - Invoke agent (alias)
- `GET /api/v1/agent/{thread_id}/state` - Get state
- `POST /api/v1/agent/{thread_id}/chat` - Continue conversation

### Features
- **Filesystem**: Create, read, edit, list files
- **Planning**: Add, read, update TODOs with status tracking
- **Sub-agents**: Delegate tasks to specialized agents
- **Workflows**: Multi-step complex task execution

## Test Output

Tests provide color-coded output:
- ✅ Green: Test passed
- ❌ Red: Test failed
- ℹ️ Blue: Information
- ⚠️ Yellow: Warning

## Expected Results

All tests should pass if:
- Server is running correctly
- API keys are configured
- Dependencies are installed
- Network connectivity is available

## Troubleshooting

### "No module named uvicorn"
```bash
pip install -r requirements.txt
```

### "Connection refused"
- Make sure the server is running on port 8000
- Check if another process is using port 8000

### "No API key configured"
- Create a `.env` file with your API keys
- See `.env.example` for format

### Tests timeout
- LLM API calls can be slow
- Increase `TIMEOUT` in `test_agent.py` if needed
- Check your API key limits

## Notes

- Tests make real API calls to LLM services (OpenAI/Anthropic)
- Some tests may take 30-120 seconds due to LLM processing
- Tests create actual files and TODOs in agent state
- Each test run creates new thread IDs
