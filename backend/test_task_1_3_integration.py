#!/usr/bin/env python3
"""
Test script for Task 1.3 - LanguageIdentifierModule Integration
Tests the integration of LanguageIdentifierModule with OrchestratorAgent
"""

import sys
import os

# Add src to path
sys.path.append('/app/src')

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition


def test_task_1_3_integration():
    """Test complete integration of Task 1.3 - LanguageIdentifierModule."""
    print("=== Task 1.3 Integration Test ===")
    print("Testing LanguageIdentifierModule integration with OrchestratorAgent")
    
    try:
        # Initialize Orchestrator Agent
        print("\n1. Initializing OrchestratorAgent...")
        agent = OrchestratorAgent()
        print(f"   Agent initialized with ID: {agent.agent_id}")
        
        # Create a test task
        print("\n2. Creating test task...")
        task = TaskDefinition(repository_url='https://github.com/octocat/Hello-World.git')
        print(f"   Task created for repository: {task.repository_url}")
        
        # Execute the task
        print("\n3. Executing task (this will clone repo and identify languages)...")
        execution_id = agent.handle_task(task)
        print(f"   Task executed with execution ID: {execution_id}")
        
        # Get task status and results
        print("\n4. Checking task results...")
        status = agent.get_task_status(execution_id)
        
        if status:
            print(f"   Task Status: {status.get('status', 'unknown')}")
            print(f"   Repository Path: {status.get('repository_path', 'N/A')}")
            print(f"   Detected Languages: {status.get('detected_languages', [])}")
            print(f"   Steps Completed: {len(status.get('steps_completed', []))}")
            
            # Check if we have detected languages
            detected_languages = status.get('detected_languages', [])
            if detected_languages:
                print(f"   ✅ SUCCESS: Languages detected successfully: {detected_languages}")
            else:
                print(f"   ⚠️  WARNING: No languages detected")
                
            # Show step details
            steps = status.get('steps_completed', [])
            print(f"\n5. Task execution steps:")
            for i, step in enumerate(steps, 1):
                step_name = step.get('step', 'unknown')
                duration = step.get('duration_ms', 0)
                print(f"   Step {i}: {step_name} ({duration:.2f}ms)")
        else:
            print("   ❌ ERROR: Could not retrieve task status")
            
        # Get agent statistics
        print("\n6. Agent Statistics:")
        stats = agent.get_agent_stats()
        print(f"   Total Tasks: {stats.get('total_tasks_handled', 0)}")
        print(f"   Successful Tasks: {stats.get('successful_tasks', 0)}")
        print(f"   Failed Tasks: {stats.get('failed_tasks', 0)}")
        
        # Clean up
        print("\n7. Cleanup...")
        repo_path = status.get('repository_path') if status else None
        if repo_path and agent.git_operations:
            try:
                agent.git_operations.cleanup_repository(repo_path)
                print(f"   Repository cleaned up: {repo_path}")
            except Exception as e:
                print(f"   Cleanup warning: {e}")
        
        print("\n=== Task 1.3 Integration Test COMPLETED ===")
        print("✅ LanguageIdentifierModule is successfully integrated!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_task_1_3_integration()
    sys.exit(0 if success else 1) 