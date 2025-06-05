#!/usr/bin/env python3
"""
Demo Script for Orchestrator Agent - Task 1.1

This script demonstrates the basic functionality of the Orchestrator Agent
and shows the logging output as required by the Task 1.1 DoD.

This is an integration demo, not a unit test. Unit tests are located in the tests/ directory.
"""

import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition


def main():
    """Main test function to demonstrate Orchestrator Agent functionality."""
    
    print("=== RepoChat v1.0 - Orchestrator Agent Test ===")
    print()
    
    try:
        # Test 1: Initialize Orchestrator Agent
        print("1. Initializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent()
        print(f"   Created: {orchestrator}")
        print()
        
        # Test 2: Create TaskDefinition
        print("2. Creating TaskDefinition...")
        task_def = TaskDefinition(
            repository_url="https://github.com/aidino/repochat.git"
        )
        print(f"   TaskDefinition: {task_def}")
        print()
        
        # Test 3: Handle a task
        print("3. Handling task with Orchestrator...")
        execution_id = orchestrator.handle_task(task_def)
        print(f"   Execution ID: {execution_id}")
        print()
        
        # Test 4: Check task status
        print("4. Checking task status...")
        status = orchestrator.get_task_status(execution_id)
        print(f"   Status: {status['status'] if status else 'Not found'}")
        print()
        
        # Test 5: Test error logging
        print("5. Testing error logging with invalid repository...")
        try:
            invalid_task = TaskDefinition(repository_url="")
            orchestrator.handle_task(invalid_task)
        except Exception as e:
            print(f"   Expected error handled: {type(e).__name__}")
        print()
        
        # Test 6: Shutdown
        print("6. Shutting down Orchestrator Agent...")
        orchestrator.shutdown()
        print()
        
        print("=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 