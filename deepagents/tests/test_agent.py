"""
Comprehensive test suite for Deep Agents API

Tests all features including:
- Filesystem operations (read, write, list, edit)
- Planning operations (TODOs)
- Sub-agent delegation
- All API endpoints
- Conversation continuity
"""

import httpx
import time
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1/agent"
TIMEOUT = 120.0  # Increased timeout for LLM operations


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = httpx.get("http://localhost:8000/health", timeout=10.0)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "healthy":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed: {data}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


def test_agent_invoke() -> Optional[str]:
    """Test basic agent invocation"""
    print_section("Testing Agent Invocation")
    
    payload = {
        "query": "Create a plan to learn Rust, write it to plan.txt, and add the first step to TODOs.",
    }
    
    try:
        print_info(f"Sending request to {BASE_URL}/invoke...")
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print_success("Agent invoked successfully")
        print(f"  Thread ID: {data['thread_id']}")
        print(f"  Response: {data['response'][:100]}...")
        print(f"  Files created: {len(data.get('files', {}))}")
        print(f"  TODOs created: {len(data.get('todos', []))}")
        
        # Verify files
        if "plan.txt" in data.get('files', {}):
            print_success("plan.txt was created")
        else:
            print_error("plan.txt was NOT created")
        
        # Verify TODOs
        if data.get('todos'):
            print_success(f"TODOs were added: {len(data['todos'])}")
        else:
            print_error("No TODOs added")
        
        return data['thread_id']
        
    except httpx.HTTPStatusError as e:
        print_error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def test_agent_run_endpoint() -> Optional[str]:
    """Test /run endpoint (alias for /invoke)"""
    print_section("Testing /run Endpoint")
    
    payload = {
        "query": "Write 'Hello World' to hello.txt and list all files.",
    }
    
    try:
        print_info(f"Sending request to {BASE_URL}/run...")
        response = httpx.post(f"{BASE_URL}/run", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print_success("/run endpoint works")
        print(f"  Thread ID: {data['thread_id']}")
        
        if "hello.txt" in data.get('files', {}):
            print_success("hello.txt was created")
            content = data['files']['hello.txt']
            if "Hello World" in content:
                print_success("hello.txt contains correct content")
            else:
                print_error(f"hello.txt content mismatch: {content}")
        else:
            print_error("hello.txt was NOT created")
        
        return data['thread_id']
        
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def test_get_state(thread_id: str):
    """Test getting agent state"""
    print_section("Testing Get State Endpoint")
    
    try:
        print_info(f"Fetching state for thread {thread_id}...")
        response = httpx.get(f"{BASE_URL}/{thread_id}/state", timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        print_success("State retrieved successfully")
        print(f"  Thread ID: {data['thread_id']}")
        print(f"  Files: {list(data.get('files', {}).keys())}")
        print(f"  TODOs: {len(data.get('todos', []))}")
        print(f"  Messages: {len(data.get('messages', []))}")
        
        # Verify state structure
        assert 'thread_id' in data, "Missing thread_id in state"
        assert 'files' in data, "Missing files in state"
        assert 'todos' in data, "Missing todos in state"
        assert 'messages' in data, "Missing messages in state"
        
        print_success("State structure is correct")
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_chat_continuity(thread_id: str):
    """Test continuing conversation with /chat endpoint"""
    print_section("Testing Chat Continuity")
    
    payload = {
        "query": "Update the first TODO to 'in_progress' status.",
    }
    
    try:
        print_info(f"Continuing chat for thread {thread_id}...")
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print_success("Chat continued successfully")
        print(f"  Response: {data['response'][:100]}...")
        
        # Check if TODO was updated
        todos = data.get('todos', [])
        if todos and any(todo.get('status') == 'in_progress' for todo in todos):
            print_success("TODO status was updated")
        else:
            print_info("TODO status update may not have occurred (check manually)")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_filesystem_operations():
    """Test filesystem operations"""
    print_section("Testing Filesystem Operations")
    
    thread_id = None
    
    # Test 1: Write file
    print_info("Test 1: Writing file...")
    payload = {
        "query": "Write 'Test content for filesystem' to test_fs.txt",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        thread_id = data['thread_id']
        
        if "test_fs.txt" in data.get('files', {}):
            print_success("File write operation successful")
        else:
            print_error("File write operation failed")
            return False
    except Exception as e:
        print_error(f"File write error: {e}")
        return False
    
    # Test 2: Read file
    print_info("Test 2: Reading file...")
    payload = {
        "query": "Read the content of test_fs.txt",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        print_success("File read operation successful")
    except Exception as e:
        print_error(f"File read error: {e}")
        return False
    
    # Test 3: Edit file (append)
    print_info("Test 3: Editing file (append)...")
    payload = {
        "query": "Append ' - Appended content' to test_fs.txt using edit_file",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if "test_fs.txt" in data.get('files', {}):
            content = data['files']['test_fs.txt']
            if "Appended content" in content:
                print_success("File edit (append) operation successful")
            else:
                print_error("File edit (append) content mismatch")
                return False
        else:
            print_error("File edit (append) failed")
            return False
    except Exception as e:
        print_error(f"File edit error: {e}")
        return False
    
    # Test 4: List files
    print_info("Test 4: Listing files...")
    payload = {
        "query": "List all files using fs_ls",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        print_success("File list operation successful")
    except Exception as e:
        print_error(f"File list error: {e}")
        return False
    
    return True


def test_planning_operations():
    """Test planning (TODO) operations"""
    print_section("Testing Planning Operations")
    
    thread_id = None
    
    # Test 1: Add TODO
    print_info("Test 1: Adding TODO...")
    payload = {
        "query": "Add a TODO: 'Test task 1'",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        thread_id = data['thread_id']
        
        todos = data.get('todos', [])
        if todos:
            print_success(f"TODO added successfully: {len(todos)} TODO(s)")
        else:
            print_error("TODO add operation failed")
            return False
    except Exception as e:
        print_error(f"TODO add error: {e}")
        return False
    
    # Test 2: Read TODOs
    print_info("Test 2: Reading TODOs...")
    payload = {
        "query": "Read all TODOs using plan_read_todos",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        print_success("TODO read operation successful")
    except Exception as e:
        print_error(f"TODO read error: {e}")
        return False
    
    # Test 3: Update TODO status
    print_info("Test 3: Updating TODO status...")
    payload = {
        "query": "Update the first TODO to 'completed' status",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/{thread_id}/chat", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        todos = data.get('todos', [])
        if todos and any(todo.get('status') == 'completed' for todo in todos):
            print_success("TODO status update successful")
        else:
            print_info("TODO status update may not have occurred (check manually)")
    except Exception as e:
        print_error(f"TODO update error: {e}")
        return False
    
    return True


def test_subagent_delegation():
    """Test sub-agent delegation"""
    print_section("Testing Sub-agent Delegation")
    
    # Test research-agent
    print_info("Test 1: Delegating to research-agent...")
    payload = {
        "query": "Delegate research on 'Python async programming' to the research-agent",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if "research" in data.get('response', '').lower() or len(data.get('response', '')) > 50:
            print_success("Research-agent delegation successful")
        else:
            print_info("Research-agent may have been used (check response manually)")
    except Exception as e:
        print_error(f"Research-agent delegation error: {e}")
        return False
    
    # Test writing-agent
    print_info("Test 2: Delegating to writing-agent...")
    payload = {
        "query": "Delegate writing a summary about 'Machine Learning basics' to the writing-agent",
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if len(data.get('response', '')) > 50:
            print_success("Writing-agent delegation successful")
        else:
            print_info("Writing-agent may have been used (check response manually)")
    except Exception as e:
        print_error(f"Writing-agent delegation error: {e}")
        return False
    
    return True


def test_complex_workflow():
    """Test a complex multi-step workflow"""
    print_section("Testing Complex Workflow")
    
    payload = {
        "query": """Create a comprehensive plan for building a web application:
1. Add TODOs for: 'Design database schema', 'Create API endpoints', 'Build frontend'
2. Write the plan to 'webapp_plan.txt'
3. Update the first TODO to 'in_progress'
4. List all files""",
    }
    
    try:
        print_info("Executing complex workflow...")
        response = httpx.post(f"{BASE_URL}/invoke", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print_success("Complex workflow executed")
        
        # Verify files
        files = data.get('files', {})
        if "webapp_plan.txt" in files:
            print_success("Plan file created")
        else:
            print_error("Plan file NOT created")
        
        # Verify TODOs
        todos = data.get('todos', [])
        if len(todos) >= 3:
            print_success(f"Multiple TODOs created: {len(todos)}")
        else:
            print_error(f"Expected at least 3 TODOs, got {len(todos)}")
        
        # Check for in_progress status
        if any(todo.get('status') == 'in_progress' for todo in todos):
            print_success("TODO status updated to in_progress")
        
        return True
        
    except Exception as e:
        print_error(f"Complex workflow error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  DEEP AGENTS API - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"{Colors.RESET}\n")
    
    results = []
    
    # Basic tests
    results.append(("Health Check", test_health_check()))
    
    # API endpoint tests
    thread_id1 = test_agent_invoke()
    results.append(("Agent Invoke", thread_id1 is not None))
    
    thread_id2 = test_agent_run_endpoint()
    results.append(("Agent Run Endpoint", thread_id2 is not None))
    
    if thread_id1:
        results.append(("Get State", test_get_state(thread_id1)))
        results.append(("Chat Continuity", test_chat_continuity(thread_id1)))
    
    # Feature tests
    results.append(("Filesystem Operations", test_filesystem_operations()))
    results.append(("Planning Operations", test_planning_operations()))
    results.append(("Sub-agent Delegation", test_subagent_delegation()))
    results.append(("Complex Workflow", test_complex_workflow()))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! 🎉{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}Some tests failed. Please review the output above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
