#!/usr/bin/env python3
"""
RepoChat Master Test Script - Post-Refactoring Verification

Comprehensive testing script để verify Phase 1, 2, 3 functionality
sau khi refactoring code structure.

Usage:
    python run_all_tests.py [--quick] [--performance] [--phase N]

Author: RepoChat Development Team
Date: 2025-06-06
"""

import sys
import os
import time
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shared.utils.logging_config import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger("master_test_runner")

class TestResult:
    """Test result tracking."""
    def __init__(self, name: str, passed: bool = False, duration: float = 0.0, 
                 output: str = "", error: str = ""):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.output = output
        self.error = error

class MasterTestRunner:
    """
    Master test runner for post-refactoring verification.
    """
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
        # Verify we're in the right directory
        if not Path("src").exists() or not Path("requirements.txt").exists():
            raise RuntimeError("Please run this script from the backend directory")
        
        # Set PYTHONPATH
        current_dir = Path.cwd()
        src_dir = current_dir / "src"
        python_path = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = f"{src_dir}:{python_path}"
        
        logger.info("🚀 Master Test Runner initialized")
        logger.info(f"📂 Working directory: {current_dir}")
        logger.info(f"🐍 PYTHONPATH: {os.environ['PYTHONPATH']}")

    def run_command(self, command: List[str], name: str, timeout: int = 300) -> TestResult:
        """
        Run a command and return test result.
        
        Args:
            command: Command to run as list
            name: Test name for reporting
            timeout: Timeout in seconds
            
        Returns:
            TestResult object
        """
        logger.info(f"🧪 Running: {name}")
        logger.info(f"   Command: {' '.join(command)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"   ✅ {name}: PASSED ({duration:.2f}s)")
                return TestResult(name, True, duration, result.stdout, result.stderr)
            else:
                logger.error(f"   ❌ {name}: FAILED ({duration:.2f}s)")
                logger.error(f"   Error output: {result.stderr[:500]}")
                return TestResult(name, False, duration, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"   ⏱️ {name}: TIMEOUT ({duration:.2f}s)")
            return TestResult(name, False, duration, "", f"Timeout after {timeout}s")
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"   💥 {name}: ERROR ({duration:.2f}s) - {e}")
            return TestResult(name, False, duration, "", str(e))

    def run_phase_1_tests(self) -> List[TestResult]:
        """Run Phase 1 unit tests."""
        logger.info("\n🏗️  PHASE 1: Data Acquisition & Git Integration")
        logger.info("=" * 60)
        
        phase_1_tests = [
            (["python", "-m", "pytest", "tests/test_git_operations_module.py", "-v"], 
             "Git Operations Module"),
            (["python", "-m", "pytest", "tests/test_language_identifier_module.py", "-v"], 
             "Language Identifier Module"),
            (["python", "-m", "pytest", "tests/test_data_preparation_module.py", "-v"], 
             "Data Preparation Module"),
            (["python", "-m", "pytest", "tests/test_pat_handler_module.py", "-v"], 
             "PAT Handler Module"),
            (["python", "-m", "pytest", "tests/test_project_data_context.py", "-v"], 
             "Project Data Context"),
        ]
        
        results = []
        for command, name in phase_1_tests:
            result = self.run_command(command, name)
            results.append(result)
            self.results.append(result)
            
        return results

    def run_phase_2_tests(self) -> List[TestResult]:
        """Run Phase 2 parsing & CKG tests."""
        logger.info("\n🧠 PHASE 2: Code Parsing & CKG Foundation")
        logger.info("=" * 60)
        
        phase_2_tests = [
            (["python", "-m", "pytest", "tests/test_java_parser.py", "-v"], 
             "Java Parser"),
            (["python", "-m", "pytest", "tests/test_python_parser.py", "-v"], 
             "Python Parser"),
            (["python", "-m", "pytest", "tests/test_kotlin_parser.py", "-v"], 
             "Kotlin Parser"),
            (["python", "-m", "pytest", "tests/test_dart_parser.py", "-v"], 
             "Dart Parser"),
            (["python", "-m", "pytest", "tests/test_neo4j_connection_module.py", "-v"], 
             "Neo4j Connection Module"),
            (["python", "-m", "pytest", "tests/test_ast_to_ckg_builder_module.py", "-v"], 
             "AST to CKG Builder"),
            (["python", "-m", "pytest", "tests/test_code_parser_coordinator_module.py", "-v"], 
             "Code Parser Coordinator"),
        ]
        
        results = []
        for command, name in phase_2_tests:
            result = self.run_command(command, name)
            results.append(result)
            self.results.append(result)
            
        return results

    def run_phase_3_tests(self) -> List[TestResult]:
        """Run Phase 3 LLM & analysis tests."""
        logger.info("\n🤖 PHASE 3: Code Analysis & LLM Integration")
        logger.info("=" * 60)
        
        phase_3_tests = [
            (["python", "-m", "pytest", "tests/test_task_3_1_architectural_analyzer_module.py", "-v"], 
             "Task 3.1: Architectural Analyzer"),
            (["python", "-m", "pytest", "tests/test_task_3_3_llm_services.py", "-v"], 
             "Task 3.3: LLM Services"),
            (["python", "-m", "pytest", "tests/test_task_3_4_llm_gateway_formatter.py", "-v"], 
             "Task 3.4: LLM Gateway & Formatter"),
            (["python", "-m", "pytest", "tests/test_task_3_5_llm_analysis_support.py", "-v"], 
             "Task 3.5: LLM Analysis Support"),
            (["python", "tests/phase_3_specific/phase_3_completion_test.py"], 
             "Phase 3 Completion Verification"),
        ]
        
        results = []
        for command, name in phase_3_tests:
            result = self.run_command(command, name)
            results.append(result)
            self.results.append(result)
            
        return results

    def run_integration_tests(self) -> List[TestResult]:
        """Run integration tests."""
        logger.info("\n🔗 INTEGRATION TESTS")
        logger.info("=" * 60)
        
        integration_tests = [
            (["python", "tests/integration/quick_integration_test.py"], 
             "Quick Integration Test"),
            (["python", "tests/integration/integration_test_phase_1.py"], 
             "Phase 1 Integration Test"),
            (["python", "-m", "pytest", "tests/test_orchestrator_agent.py", "-v"], 
             "Orchestrator Agent"),
        ]
        
        results = []
        for command, name in integration_tests:
            result = self.run_command(command, name)
            results.append(result)
            self.results.append(result)
            
        return results

    def run_manual_tests(self) -> List[TestResult]:
        """Run critical manual tests."""
        logger.info("\n🔍 CRITICAL MANUAL TESTS")
        logger.info("=" * 60)
        
        manual_tests = [
            (["python", "tests/manual/manual_test_phase_2_complete_fixed.py"], 
             "Manual Phase 2 Complete Test"),
        ]
        
        results = []
        for command, name in manual_tests:
            result = self.run_command(command, name, timeout=600)  # Longer timeout for manual tests
            results.append(result)
            self.results.append(result)
            
        return results

    def run_performance_tests(self) -> List[TestResult]:
        """Run performance tests (optional)."""
        logger.info("\n⚡ PERFORMANCE TESTS")
        logger.info("=" * 60)
        
        performance_tests = [
            (["python", "scripts/testing/performance_test_real_projects.py"], 
             "Real Projects Performance Test"),
            (["python", "scripts/testing/test_kotlin_dart_performance.py"], 
             "Kotlin/Dart Performance Test"),
        ]
        
        results = []
        for command, name in performance_tests:
            result = self.run_command(command, name, timeout=900)  # Longer timeout
            results.append(result)
            self.results.append(result)
            
        return results

    def generate_report(self) -> None:
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE TEST REPORT")
        logger.info("=" * 80)
        
        logger.info(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        logger.info(f"📈 Total Tests: {len(self.results)}")
        logger.info(f"✅ Passed: {len(passed_tests)}")
        logger.info(f"❌ Failed: {len(failed_tests)}")
        
        if len(self.results) > 0:
            success_rate = (len(passed_tests) / len(self.results)) * 100
            logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed_tests:
            logger.info("\n❌ FAILED TESTS:")
            for test in failed_tests:
                logger.info(f"   • {test.name}")
                if test.error:
                    logger.info(f"     Error: {test.error[:200]}...")
        
        if passed_tests:
            logger.info(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
            for test in passed_tests:
                logger.info(f"   • {test.name} ({test.duration:.2f}s)")
        
        # Overall status
        if len(failed_tests) == 0:
            logger.info("\n🎉 ALL TESTS PASSED!")
            logger.info("✨ RepoChat is fully functional and ready for Phase 4!")
        else:
            logger.info(f"\n⚠️  {len(failed_tests)} tests failed")
            logger.info("🔧 Please review and fix issues before proceeding to Phase 4")

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RepoChat Master Test Runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only quick tests (skip manual/performance)")
    parser.add_argument("--performance", action="store_true", 
                       help="Include performance tests")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], 
                       help="Run only specific phase tests")
    
    args = parser.parse_args()
    
    try:
        runner = MasterTestRunner()
        
        logger.info("🚀 RepoChat Master Test Runner - Post-Refactoring Verification")
        logger.info("=" * 80)
        logger.info("📁 Refactored structure with organized test folders")
        logger.info("🧪 Comprehensive testing of Phase 1, 2, 3 functionality")
        logger.info("=" * 80)
        
        if args.phase:
            # Run specific phase only
            if args.phase == 1:
                runner.run_phase_1_tests()
            elif args.phase == 2:
                runner.run_phase_2_tests()
            elif args.phase == 3:
                runner.run_phase_3_tests()
        else:
            # Run all phases
            runner.run_phase_1_tests()
            runner.run_phase_2_tests()
            runner.run_phase_3_tests()
            runner.run_integration_tests()
            
            if not args.quick:
                runner.run_manual_tests()
                
            if args.performance:
                runner.run_performance_tests()
        
        runner.generate_report()
        
        # Exit with appropriate code
        failed_count = len([r for r in runner.results if not r.passed])
        sys.exit(0 if failed_count == 0 else 1)
        
    except Exception as e:
        logger.error(f"💥 Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 