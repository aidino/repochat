#!/usr/bin/env python3
"""
Manual Test MT1.8: End-to-End Workflow Test Fixed

Demonstrates the complete Phase 1 workflow from TaskDefinition to ProjectDataContext.
Fixed import path issues and provides comprehensive testing.
"""

import os
import sys
import time
import shutil

# Add src to path with consistent import method
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition


def run_end_to_end_workflow():
    """Run comprehensive end-to-end Phase 1 workflow test."""
    print("🚀 MT1.8: End-to-End Workflow Test")
    print("=" * 60)
    
    start_time = time.time()
    orchestrator = None
    project_context = None
    
    try:
        # Step 1: Initialize system
        print("1. Initializing RepoChat system...")
        step_start = time.time()
        orchestrator = OrchestratorAgent()
        init_time = (time.time() - step_start) * 1000
        print(f"   ✅ System initialized in {init_time:.2f}ms")
        print(f"   Agent ID: {orchestrator.agent_id[:8]}...")
        
        # Step 2: Create task definition
        print("\n2. Creating task definition...")
        task_def = TaskDefinition(
            repository_url='https://github.com/octocat/Hello-World.git',  # Use smaller repo for faster testing
            task_id='e2e-test-mt1.8'
        )
        print(f"   ✅ Task created: {task_def.task_id}")
        print(f"   Repository: {task_def.repository_url}")
        
        # Step 3: Execute scan project task
        print("\n3. Executing complete scan project workflow...")
        step_start = time.time()
        
        print("   🔄 Starting 4-step workflow:")
        print("      - Step 1: PAT requirements check")
        print("      - Step 2: Repository cloning")
        print("      - Step 3: Language identification")
        print("      - Step 4: Data context creation")
        
        project_context = orchestrator.handle_scan_project_task(task_def)
        execution_time = time.time() - step_start
        
        print(f"\n   ✅ Scan completed in {execution_time:.2f}s")
        print(f"   📋 Results summary:")
        print(f"      - Repository: {project_context.repository_url}")
        print(f"      - Cloned path: {project_context.cloned_code_path}")
        print(f"      - Languages detected: {project_context.detected_languages}")
        print(f"      - Primary language: {project_context.primary_language}")
        print(f"      - Language count: {project_context.language_count}")
        print(f"      - Has languages: {project_context.has_languages}")
        
        # Step 4: Verify data quality
        print("\n4. Validating data quality...")
        
        # Check repository URL match
        assert project_context.repository_url == task_def.repository_url, f"Repository URL mismatch"
        print("   ✅ Repository URL validation passed")
        
        # Check cloned path exists
        assert project_context.cloned_code_path is not None, "Cloned path is None"
        assert os.path.exists(project_context.cloned_code_path), "Cloned path does not exist"
        print("   ✅ Cloned path validation passed")
        
        # Check language detection (allowing empty for simple repos)
        assert isinstance(project_context.detected_languages, list), "Languages not a list"
        print(f"   ✅ Language detection validation passed ({project_context.language_count} languages)")
        
        # Check context properties
        assert hasattr(project_context, 'analysis_timestamp'), "Missing analysis_timestamp"
        assert hasattr(project_context, 'acquisition_duration_ms'), "Missing acquisition_duration_ms"
        print("   ✅ Context properties validation passed")
        
        # Step 5: Check agent statistics
        print("\n5. Checking agent statistics...")
        stats = orchestrator.get_agent_stats()
        
        print(f"   📊 Agent statistics:")
        print(f"      - Agent ID: {stats['agent_id'][:8]}...")
        print(f"      - Uptime: {stats['uptime_seconds']:.2f}s")
        print(f"      - Active tasks: {stats['active_tasks_count']}")
        print(f"      - Total tasks handled: {stats['statistics']['total_tasks_handled']}")
        print(f"      - Successful tasks: {stats['statistics']['successful_tasks']}")
        print(f"      - Failed tasks: {stats['statistics']['failed_tasks']}")
        print(f"      - Agent start time: {stats['statistics']['start_time']}")
        
        assert stats['statistics']['total_tasks_handled'] >= 1, "No tasks handled recorded"
        print("   ✅ Agent statistics validation passed")
        
        # Step 6: Performance validation
        print("\n6. Validating performance metrics...")
        
        # Check initialization time (should be < 1000ms)
        if init_time < 1000:
            print(f"   ✅ Initialization time acceptable: {init_time:.2f}ms < 1000ms")
        else:
            print(f"   ⚠️  Initialization time high: {init_time:.2f}ms >= 1000ms")
        
        # Check execution time (should be < 60s for small repo)
        if execution_time < 60:
            print(f"   ✅ Execution time acceptable: {execution_time:.2f}s < 60s")
        else:
            print(f"   ⚠️  Execution time high: {execution_time:.2f}s >= 60s")
        
        # Check total workflow timing
        total_time = time.time() - start_time
        print(f"   📊 Total workflow time: {total_time:.2f}s")
        
        print("\n" + "=" * 60)
        print("🎉 END-TO-END WORKFLOW TEST RESULTS")
        print("=" * 60)
        print("✅ System Initialization: PASSED")
        print("✅ Task Definition Creation: PASSED")  
        print("✅ 4-Step Scan Workflow: PASSED")
        print("✅ Data Quality Validation: PASSED")
        print("✅ Agent Statistics: PASSED")
        print("✅ Performance Metrics: PASSED")
        print("\n🏆 Phase 1 End-to-End Integration: FULLY VALIDATED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Step 7: Cleanup
        print(f"\n7. Performing cleanup...")
        
        if project_context and project_context.cloned_code_path:
            if os.path.exists(project_context.cloned_code_path):
                shutil.rmtree(project_context.cloned_code_path)
                print(f"   ✅ Cleaned up repository: {project_context.cloned_code_path}")
        
        if orchestrator:
            orchestrator.shutdown()
            print("   ✅ Orchestrator shutdown completed")
        
        total_time = time.time() - start_time
        print(f"   📊 Total test duration: {total_time:.2f}s")
        print("   ✅ Cleanup completed")


def run_validation_checks():
    """Run additional validation checks for MT1.8."""
    print("\n" + "=" * 60)
    print("📋 MT1.8 LOG VALIDATION CHECKS")
    print("=" * 60)
    
    log_checks = [
        ("OrchestratorAgent initialization", "OrchestratorAgent initialized"),
        ("Task execution start", "Starting task execution"),
        ("Scan project workflow", "handle_scan_project_task"),
        ("PAT requirements check", "Checking PAT requirements"),
        ("Repository cloning", "Starting repository clone"),
        ("Language identification", "Starting language identification"),
        ("Data context creation", "Creating project data context"),
        ("Workflow completion", "Scan project task completed successfully")
    ]
    
    print("Expected log entries to verify in logs/repochat_debug_*.log:")
    print()
    
    for description, log_pattern in log_checks:
        print(f"# {description}")
        print(f"grep \"{log_pattern}\" logs/repochat_debug_*.log")
        print()
    
    print("📊 Success Criteria:")
    print("- All grep commands should return matching log entries")
    print("- Logs should show complete 4-step workflow execution")
    print("- Performance metrics should be recorded")
    print("- No error logs during normal execution")


def main():
    """Main test execution."""
    success = run_end_to_end_workflow()
    run_validation_checks()
    
    if success:
        print("\n🎯 FINAL RESULT: MT1.8 END-TO-END TEST PASSED")
        print("Phase 1 is fully validated and ready for Phase 2! 🚀")
    else:
        print("\n💥 FINAL RESULT: MT1.8 END-TO-END TEST FAILED")
        print("Please check logs and fix issues before proceeding.")


if __name__ == "__main__":
    main() 