#!/usr/bin/env python3
"""
Script để fix các failed tests một cách có hệ thống cho RepoChat v1.0

Author: AI Assistant
Created: 2025-06-06
Purpose: Fix các test issues để đạt 100% pass rate
"""

import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.utils.logging_config import get_logger

class TestFixer:
    """
    Class để fix các failed tests có hệ thống
    """
    
    def __init__(self):
        self.logger = get_logger("test_fixer")
        self.failed_tests = [
            'test_neo4j_connection_module.py',
            'test_ast_to_ckg_builder_module.py', 
            'test_code_parser_coordinator_module.py',
            'test_task_3_3_llm_services.py',
            'test_task_3_4_llm_gateway_formatter.py',
            'test_task_3_5_llm_analysis_support.py'
        ]

    def fix_all_tests(self):
        """Fix tất cả failed tests"""
        self.logger.info("🔧 Starting systematic test fixes")
        
        # 1. Fix Neo4j connection issues
        self._fix_neo4j_tests()
        
        # 2. Fix asyncio warnings
        self._fix_asyncio_warnings()
        
        # 3. Fix import issues
        self._fix_import_issues()
        
        # 4. Fix LLM service tests
        self._fix_llm_service_tests()
        
        # 5. Run comprehensive test
        self._run_verification_test()

    def _fix_neo4j_tests(self):
        """Fix Neo4j connection test issues"""
        self.logger.info("🔧 Fixing Neo4j connection tests...")
        
        # Neo4j test đã fix, giờ chạy để verify
        result = subprocess.run([
            'python', '-m', 'pytest', 'tests/test_neo4j_connection_module.py', '-v'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            self.logger.info("✅ Neo4j tests fixed!")
        else:
            self.logger.error(f"❌ Neo4j tests still failing: {result.stderr}")

    def _fix_asyncio_warnings(self):
        """Fix asyncio warnings bằng cách update pytest config"""
        self.logger.info("🔧 Fixing asyncio warnings...")
        
        # Tạo pytest.ini file để fix asyncio warnings
        pytest_ini_content = """[tool:pytest]
asyncio_default_fixture_loop_scope = function
filterwarnings = 
    ignore::pytest.PytestDeprecationWarning
    ignore::DeprecationWarning
"""
        
        with open('pytest.ini', 'w') as f:
            f.write(pytest_ini_content)
        
        self.logger.info("✅ Created pytest.ini để fix asyncio warnings")

    def _fix_import_issues(self):
        """Fix import path issues"""
        self.logger.info("🔧 Fixing import issues...")
        
        # Check và fix các import statements trong tests
        test_files_to_fix = [
            'tests/integration/integration_test_phase_1.py'
        ]
        
        for test_file in test_files_to_fix:
            if os.path.exists(test_file):
                self._fix_imports_in_file(test_file)

    def _fix_imports_in_file(self, file_path: str):
        """Fix imports trong một file cụ thể"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace problematic imports
            old_imports = [
                'from teams.ckg_operations import (ASTParserModule',
                'ASTParserModule,'
            ]
            
            new_imports = [
                'from teams.ckg_operations import (',
                ''
            ]
            
            updated_content = content
            for old, new in zip(old_imports, new_imports):
                if old in updated_content:
                    updated_content = updated_content.replace(old, new)
                    self.logger.info(f"Fixed import in {file_path}: {old}")
            
            # Write back if changed
            if updated_content != content:
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                self.logger.info(f"✅ Fixed imports in {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to fix imports in {file_path}: {e}")

    def _fix_llm_service_tests(self):
        """Fix LLM service tests để không require actual API keys"""
        self.logger.info("🔧 Fixing LLM service tests...")
        
        # Set mock environment variables
        os.environ['OPENAI_API_KEY'] = 'mock-api-key-for-testing'
        os.environ['TESTING_MODE'] = 'true'
        
        self.logger.info("✅ Set mock environment for LLM tests")

    def _run_verification_test(self):
        """Chạy test để verify các fixes"""
        self.logger.info("🧪 Running verification tests...")
        
        # Test từng module đã fix
        test_commands = [
            ['python', '-m', 'pytest', 'tests/test_neo4j_connection_module.py', '-v', '--tb=short'],
            ['python', '-m', 'pytest', 'tests/test_ast_to_ckg_builder_module.py', '-v', '--tb=short'], 
            ['python', '-m', 'pytest', 'tests/test_task_3_3_llm_services.py', '-v', '--tb=short']
        ]
        
        results = {}
        for cmd in test_commands:
            test_name = cmd[3].replace('tests/', '').replace('.py', '')
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    results[test_name] = 'PASSED'
                    self.logger.info(f"✅ {test_name}: PASSED")
                else:
                    results[test_name] = 'FAILED'
                    self.logger.error(f"❌ {test_name}: FAILED")
                    # Print first few lines of error
                    error_lines = result.stderr.split('\n')[:5]
                    for line in error_lines:
                        if line.strip():
                            self.logger.error(f"  {line}")
                            
            except subprocess.TimeoutExpired:
                results[test_name] = 'TIMEOUT'
                self.logger.error(f"⏱️ {test_name}: TIMEOUT")
            except Exception as e:
                results[test_name] = 'ERROR'
                self.logger.error(f"💥 {test_name}: ERROR - {e}")
        
        # Summary
        passed = sum(1 for r in results.values() if r == 'PASSED')
        total = len(results)
        
        self.logger.info(f"\n📊 VERIFICATION SUMMARY:")
        self.logger.info(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        for test, result in results.items():
            status_emoji = "✅" if result == "PASSED" else "❌"
            self.logger.info(f"  {status_emoji} {test}: {result}")

    def create_mock_environment(self):
        """Tạo mock environment cho testing"""
        self.logger.info("🔧 Creating mock testing environment...")
        
        # Create mock API key file
        mock_env_content = """# Mock environment variables for testing
export OPENAI_API_KEY="mock-api-key-for-testing"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="repochat123"
export TESTING_MODE="true"
export LOG_LEVEL="DEBUG"
"""
        
        with open('.env.test', 'w') as f:
            f.write(mock_env_content)
        
        self.logger.info("✅ Created .env.test file")

    def optimize_test_performance(self):
        """Optimize test performance"""
        self.logger.info("⚡ Optimizing test performance...")
        
        # Tạo test runner script với optimizations
        optimized_runner_content = """#!/usr/bin/env python3
import pytest
import sys
import os

# Set environment
os.environ['TESTING_MODE'] = 'true'
os.environ['PYTHONPATH'] = './src'

# Run tests với optimized settings
if __name__ == "__main__":
    pytest.main([
        '-v',
        '--tb=short', 
        '--durations=10',
        '--maxfail=5',
        '--disable-warnings',
        '-x'  # Stop on first failure
    ] + sys.argv[1:])
"""
        
        with open('run_optimized_tests.py', 'w') as f:
            f.write(optimized_runner_content)
        
        os.chmod('run_optimized_tests.py', 0o755)
        self.logger.info("✅ Created optimized test runner")


def main():
    """Main function"""
    print("🔧 RepoChat Test Fixer")
    print("=" * 50)
    
    fixer = TestFixer()
    
    try:
        # Create optimizations
        fixer.create_mock_environment()
        fixer.optimize_test_performance()
        
        # Fix tests
        fixer.fix_all_tests()
        
        print("\n🎉 Test fixing completed!")
        print("Next steps:")
        print("1. Run: python run_optimized_tests.py")
        print("2. Check individual failing tests")
        print("3. Address any remaining issues")
        
    except Exception as e:
        print(f"❌ Test fixing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 