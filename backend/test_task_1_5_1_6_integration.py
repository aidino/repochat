#!/usr/bin/env python3
"""
Integration Test for Task 1.5 and Task 1.6
Test handle_scan_project_task with PAT handling functionality

This script demonstrates the complete Phase 1 functionality:
- Task 1.5: OrchestratorAgent.handle_scan_project_task()
- Task 1.6: PATHandlerModule integration
- End-to-end workflow from TaskDefinition to ProjectDataContext
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition
from teams.data_acquisition.pat_handler_module import PATHandlerModule
import tempfile
import shutil
from teams.data_acquisition.git_operations_module import GitOperationsModule


def test_public_repository_scan():
    """Test scanning a public repository (no PAT needed)."""
    print("=" * 60)
    print("🧪 TEST 1: Public Repository Scan (Task 1.5)")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        print(f"✅ OrchestratorAgent initialized: {orchestrator.agent_id[:8]}")
        
        # Create task definition for public repository
        task_def = TaskDefinition(repository_url="https://github.com/octocat/Hello-World.git")
        print(f"📋 Task created: {task_def.repository_url}")
        
        # Execute scan project task
        print("🚀 Starting scan project task...")
        project_context = orchestrator.handle_scan_project_task(task_def)
        
        # Verify results
        print("✅ Scan completed successfully!")
        print(f"📁 Repository path: {project_context.cloned_code_path}")
        print(f"🔤 Detected languages: {project_context.detected_languages}")
        print(f"📊 Language count: {project_context.language_count}")
        print(f"🎯 Primary language: {project_context.primary_language}")
        print(f"🌐 Repository URL: {project_context.repository_url}")
        
        # Clean up
        if os.path.exists(project_context.cloned_code_path):
            shutil.rmtree(project_context.cloned_code_path)
            print(f"🧹 Cleaned up: {project_context.cloned_code_path}")
        
        orchestrator.shutdown()
        print("✅ Test 1 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False


def test_pat_handler_module():
    """Test PATHandlerModule functionality (Task 1.6)."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: PAT Handler Module (Task 1.6)")
    print("=" * 60)
    
    try:
        pat_handler = PATHandlerModule()
        print("✅ PATHandlerModule initialized")
        
        # Test 1: Public repository (no PAT needed)
        public_url = "https://github.com/octocat/Hello-World.git"
        pat = pat_handler.request_pat_if_needed(public_url)
        assert pat is None, "Public repository should not require PAT"
        print(f"✅ Public repo test passed: {public_url}")
        
        # Test 2: Private repository detection
        private_urls = [
            "https://github.private.company.com/team/repo.git",
            "https://git.corp.company.com/project/repo.git",
            "git@gitlab.internal.company.com:team/repo.git",
            "https://enterprise.github.com/user/repo.git"
        ]
        
        for private_url in private_urls:
            is_private = pat_handler._is_private_repository(private_url)
            assert is_private, f"URL should be detected as private: {private_url}"
            print(f"✅ Private detection test passed: {private_url}")
        
        # Test 3: Host extraction
        test_cases = [
            ("https://github.com/user/repo.git", "github.com"),
            ("git@gitlab.com:user/repo.git", "gitlab.com"),
            ("https://bitbucket.org/user/repo.git", "bitbucket.org")
        ]
        
        for url, expected_host in test_cases:
            extracted_host = pat_handler._extract_host(url)
            assert extracted_host == expected_host, f"Host extraction failed for {url}"
            print(f"✅ Host extraction test passed: {url} -> {expected_host}")
        
        # Test 4: Authenticated URL building (from GitOperationsModule)
        git_ops = GitOperationsModule()
        test_url = "https://github.com/user/repo.git"
        test_pat = "ghp_test_token_123"
        auth_url = git_ops._build_authenticated_url(test_url, test_pat)
        expected = "https://ghp_test_token_123@github.com/user/repo.git"
        assert auth_url == expected, f"Authenticated URL building failed"
        print(f"✅ Authenticated URL building test passed (GitOperationsModule)")
        
        # Test 5: PAT cache management
        pat_handler._pat_cache['test.com'] = 'test_pat'
        assert len(pat_handler._pat_cache) == 1
        pat_handler.clear_pat_cache()
        assert len(pat_handler._pat_cache) == 0
        print(f"✅ PAT cache management test passed")
        
        # Test 6: Statistics
        stats = pat_handler.get_stats()
        assert 'cached_hosts' in stats
        assert 'cached_host_list' in stats
        print(f"✅ Statistics test passed: {stats}")
        
        print("✅ Test 2 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False


def test_private_repository_simulation():
    """Test private repository handling simulation."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Private Repository Simulation")
    print("=" * 60)
    
    try:
        orchestrator = OrchestratorAgent()
        print(f"✅ OrchestratorAgent initialized: {orchestrator.agent_id[:8]}")
        
        # Test private repository URL (will not actually clone due to lack of real PAT)
        private_url = "https://github.private.company.com/team/secret-repo.git"
        task_def = TaskDefinition(repository_url=private_url)
        print(f"📋 Task created for private repo: {private_url}")
        
        # Check if PAT would be requested
        is_private = orchestrator.pat_handler._is_private_repository(private_url)
        print(f"🔐 Private repository detection: {is_private}")
        assert is_private, "URL should be detected as private"
        
        # Simulate PAT handling without actual user input
        host = orchestrator.pat_handler._extract_host(private_url)
        print(f"🌐 Extracted host: {host}")
        
        # Test authenticated URL building
        test_pat = "ghp_simulated_token_12345"
        auth_url = orchestrator.git_operations._build_authenticated_url(private_url, test_pat)
        expected = f"https://{test_pat}@{host}/team/secret-repo.git"
        assert auth_url == expected
        print(f"🔗 Authenticated URL: {auth_url[:50]}...")
        
        orchestrator.shutdown()
        print("✅ Test 3 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False


def test_error_handling():
    """Test error handling in scan project task."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Error Handling")
    print("=" * 60)
    
    try:
        orchestrator = OrchestratorAgent()
        print(f"✅ OrchestratorAgent initialized: {orchestrator.agent_id[:8]}")
        
        # Test with invalid repository URL
        invalid_url = "https://github.com/nonexistent/repository-that-does-not-exist.git"
        task_def = TaskDefinition(repository_url=invalid_url)
        print(f"📋 Task created with invalid repo: {invalid_url}")
        
        try:
            project_context = orchestrator.handle_scan_project_task(task_def)
            print("❌ Expected error did not occur")
            return False
        except Exception as e:
            print(f"✅ Expected error caught: {type(e).__name__}: {str(e)[:100]}...")
        
        # Test with uninitialized orchestrator
        orchestrator._is_initialized = False
        try:
            project_context = orchestrator.handle_scan_project_task(task_def)
            print("❌ Expected initialization error did not occur")
            return False
        except RuntimeError as e:
            print(f"✅ Expected initialization error caught: {e}")
        
        print("✅ Test 4 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False


def test_component_integration():
    """Test integration between all TEAM Data Acquisition components."""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: Component Integration")
    print("=" * 60)
    
    try:
        orchestrator = OrchestratorAgent()
        print(f"✅ OrchestratorAgent initialized: {orchestrator.agent_id[:8]}")
        
        # Verify all components are properly initialized
        components = [
            ('git_operations', 'GitOperationsModule'),
            ('language_identifier', 'LanguageIdentifierModule'),
            ('data_preparation', 'DataPreparationModule'),
            ('pat_handler', 'PATHandlerModule')
        ]
        
        for attr_name, class_name in components:
            component = getattr(orchestrator, attr_name)
            assert component is not None, f"{class_name} not initialized"
            print(f"✅ {class_name} properly initialized")
        
        # Test agent statistics
        stats = orchestrator.get_agent_stats()
        required_stats = [
            'agent_id', 'created_at', 'uptime_seconds',
            'is_initialized', 'active_tasks_count', 'statistics', 'active_tasks'
        ]
        
        for stat in required_stats:
            assert stat in stats, f"Missing stat: {stat}"
        
        print(f"✅ Agent statistics complete: {len(stats)} fields")
        print(f"📊 Current stats: initialized={stats['is_initialized']}, "
              f"active_tasks={stats['active_tasks_count']}, "
              f"uptime={stats['uptime_seconds']:.2f}s")
        
        orchestrator.shutdown()
        print("✅ Test 5 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 STARTING TASK 1.5 & 1.6 INTEGRATION TESTS")
    print("Testing Phase 1 completion: handle_scan_project_task + PAT handling")
    
    tests = [
        test_public_repository_scan,
        test_pat_handler_module,
        test_private_repository_simulation,
        test_error_handling,
        test_component_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 1 Tasks 1.5 & 1.6 are complete!")
        print("✅ Task 1.5: handle_scan_project_task() - WORKING")
        print("✅ Task 1.6: PATHandlerModule integration - WORKING")
        print("🚀 Ready to proceed to Phase 2!")
        return True
    else:
        print(f"\n💥 {failed} tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 