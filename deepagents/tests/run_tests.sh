#!/bin/bash

# Test runner script for Deep Agents
# This script checks prerequisites and runs tests

set -e

echo "=========================================="
echo "Deep Agents Test Runner"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "❌ Error: Dependencies not installed"
    echo ""
    echo "Please install dependencies first:"
    echo "  cd $(dirname $(dirname $0))"
    echo "  pip install -r requirements.txt"
    exit 1
}

echo "✓ Dependencies installed"

# Check if server is running
echo ""
echo "Checking if server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Server is running"
else
    echo "⚠ Server is not running"
    echo ""
    echo "Please start the server in another terminal:"
    echo "  cd $(dirname $(dirname $0))"
    echo "  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo ""
    read -p "Would you like to start the server now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting server in background..."
        cd "$(dirname $(dirname $0))"
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/deepagents_server.log 2>&1 &
        SERVER_PID=$!
        echo "Server started with PID: $SERVER_PID"
        echo "Waiting for server to be ready..."
        sleep 5
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ Server is ready"
        else
            echo "❌ Server failed to start. Check /tmp/deepagents_server.log"
            exit 1
        fi
    else
        echo "Please start the server manually and run tests again"
        exit 1
    fi
fi

# Run tests
echo ""
echo "=========================================="
echo "Running tests..."
echo "=========================================="
echo ""

cd "$(dirname $(dirname $0))"
python3 tests/test_agent.py

EXIT_CODE=$?

# Cleanup if we started the server
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    echo "Stopping background server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null || true
fi

exit $EXIT_CODE
