#!/usr/bin/env python3
"""
Task 3.5 Standalone Test: LLMAnalysisSupportModule Only

Test chỉ LLMAnalysisSupportModule để tránh dependency issues với các modules khác.
"""

import sys
import os
import unittest
from datetime import datetime

# Add backend to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import only what we need for Task 3.5
from src.teams.llm_services.models import (
    LLMServiceRequest, LLMServiceResponse, LLMConfig,
    LLMProviderType, LLMServiceStatus
)

# Import directly from modules to avoid __init__.py dependencies
from src.teams.code_analysis.models import (
    AnalysisFinding, AnalysisFindingType, AnalysisSeverity
)

from src.teams.code_analysis.llm_analysis_support_module import (
    LLMAnalysisSupportModule, 
    CodeAnalysisContext,
    create_llm_analysis_support,
    create_explain_code_request
)


class TestTask35DoD(unittest.TestCase):
    """Test Task 3.5 DoD compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.module = LLMAnalysisSupportModule()
        self.test_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
    
    def test_dod_1_llm_service_request_exists(self):
        """DoD 1: LLMServiceRequest structure exists với required fields."""
        # Create a request to test structure
        request = self.module.create_explain_code_request(self.test_code)
        
        # Check that LLMServiceRequest exists and has required fields
        self.assertIsInstance(request, LLMServiceRequest)
        
        # Check required fields per DoD
        self.assertTrue(hasattr(request, 'prompt_id'))
        self.assertTrue(hasattr(request, 'context_data'))
        self.assertTrue(hasattr(request, 'llm_config'))
        
        # Check prompt_text field (or equivalent)
        self.assertTrue(hasattr(request, 'prompt_text'))
        
        print("✅ DoD 1: LLMServiceRequest structure valid")
    
    def test_dod_2_llm_service_response_exists(self):
        """DoD 2: LLMServiceResponse structure exists với required fields."""
        # Create a mock response to test structure
        response = LLMServiceResponse(
            response_text="This is a test response",
            status=LLMServiceStatus.SUCCESS
        )
        
        # Check that LLMServiceResponse exists and has required fields
        self.assertIsInstance(response, LLMServiceResponse)
        
        # Check required fields per DoD
        self.assertTrue(hasattr(response, 'response_text'))
        self.assertTrue(hasattr(response, 'status'))
        
        # Verify field values
        self.assertEqual(response.response_text, "This is a test response")
        self.assertEqual(response.status, LLMServiceStatus.SUCCESS)
        
        print("✅ DoD 2: LLMServiceResponse structure valid")
    
    def test_dod_3_module_exists_and_accepts_code_string(self):
        """DoD 3: LLMAnalysisSupportModule exists và có function nhận code string."""
        # Check module exists
        self.assertIsInstance(self.module, LLMAnalysisSupportModule)
        
        # Check module có method nhận code string
        self.assertTrue(hasattr(self.module, 'create_explain_code_request'))
        
        # Test method với code string
        result = self.module.create_explain_code_request(self.test_code)
        self.assertIsNotNone(result)
        
        print("✅ DoD 3: LLMAnalysisSupportModule accepts code string")
    
    def test_dod_4_creates_llm_service_request_with_explain_code(self):
        """DoD 4: Function tạo LLMServiceRequest với prompt_id='explain_code'."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Check return type
        self.assertIsInstance(request, LLMServiceRequest)
        
        # Check prompt_id = "explain_code"
        self.assertEqual(request.prompt_id, "explain_code")
        
        # Check context_data chứa code_snippet
        self.assertIsInstance(request.context_data, dict)
        self.assertIn("code_snippet", request.context_data)
        self.assertEqual(request.context_data["code_snippet"], self.test_code)
        
        print("✅ DoD 4: Creates LLMServiceRequest with prompt_id='explain_code'")
    
    def test_dod_5_default_llm_config(self):
        """DoD 5: Function sử dụng cấu hình LLM mặc định."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Check có llm_config
        self.assertIsInstance(request.llm_config, LLMConfig)
        
        # Check config có provider và model (cấu hình mặc định)
        self.assertIsNotNone(request.llm_config.provider)
        self.assertIsNotNone(request.llm_config.model)
        
        # Check default values
        self.assertEqual(request.llm_config.provider, LLMProviderType.OPENAI)
        self.assertEqual(request.llm_config.model, "gpt-3.5-turbo")
        
        print("✅ DoD 5: Uses default LLM config")
    
    def test_dod_6_returns_llm_service_request(self):
        """DoD 6: Function trả về LLMServiceRequest."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Check return type chính xác
        self.assertIsInstance(request, LLMServiceRequest)
        
        # Check không phải None hay type khác
        self.assertIsNotNone(request)
        
        print("✅ DoD 6: Returns LLMServiceRequest object")


class TestLLMAnalysisSupportBasicFunctions(unittest.TestCase):
    """Test basic functionality của LLMAnalysisSupportModule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.module = LLMAnalysisSupportModule()
        self.sample_code = """def add(a, b):
    return a + b"""
    
    def test_module_initialization(self):
        """Test module initialization."""
        module = LLMAnalysisSupportModule()
        
        self.assertIsNotNone(module.default_llm_config)
        self.assertEqual(module.default_llm_config.provider, LLMProviderType.OPENAI)
        self.assertEqual(module.default_llm_config.model, "gpt-3.5-turbo")
    
    def test_create_explain_code_request_basic(self):
        """Test basic explain_code request creation."""
        request = self.module.create_explain_code_request(
            code_snippet=self.sample_code,
            language="python"
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "explain_code")
        self.assertEqual(request.context_data["code_snippet"], self.sample_code)
        self.assertEqual(request.context_data["language"], "python")
    
    def test_create_analyze_function_request(self):
        """Test analyze_function request creation."""
        request = self.module.create_analyze_function_request(
            function_name="add",
            function_code=self.sample_code,
            language="python"
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "analyze_function")
        self.assertEqual(request.context_data["function_name"], "add")
        self.assertEqual(request.context_data["function_code"], self.sample_code)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test factory function
        module = create_llm_analysis_support()
        self.assertIsInstance(module, LLMAnalysisSupportModule)
        
        # Test convenience request function
        request = create_explain_code_request(self.sample_code, "python")
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "explain_code")


def run_task_3_5_standalone_tests():
    """Run Task 3.5 standalone tests."""
    print("=" * 70)
    print("  Task 3.5 Standalone Test: LLMAnalysisSupportModule")
    print("=" * 70)
    print("Testing TEAM Code Analysis LLMAnalysisSupportModule DoD compliance")
    print("(Standalone test to avoid dependency issues)")
    print()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add DoD compliance tests
    suite.addTest(unittest.makeSuite(TestTask35DoD))
    suite.addTest(unittest.makeSuite(TestLLMAnalysisSupportBasicFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("  Task 3.5 DoD Compliance Results")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
    
    if failures == 0 and errors == 0:
        print("\n🎉 TASK 3.5 DoD FULLY COMPLIANT!")
        print("\n✅ DoD Requirements All Met:")
        print("  1. ✅ LLMServiceRequest structure với prompt_id, context_data, llm_config")
        print("  2. ✅ LLMServiceResponse structure với response_text, status")
        print("  3. ✅ LLMAnalysisSupportModule với function nhận code string")
        print("  4. ✅ Function tạo LLMServiceRequest với prompt_id='explain_code'")
        print("  5. ✅ Function sử dụng cấu hình LLM mặc định")
        print("  6. ✅ Function trả về LLMServiceRequest")
        print("\n🚀 Ready for Task 3.6: Orchestrator Agent LLM routing")
        
        # Additional achievements beyond DoD
        print("\n🌟 Additional Features Implemented:")
        print("  ✨ Multiple analysis types: explain_code, analyze_function, find_issues, etc.")
        print("  ✨ CodeAnalysisContext for structured data")
        print("  ✨ Response to Finding conversion")
        print("  ✨ Convenience functions")
        print("  ✨ Vietnamese documentation")
        
    else:
        print(f"\n⚠️  {failures + errors} tests failed. DoD not fully met.")
        if result.failures:
            print("Failures:")
            for failure in result.failures:
                print(f"  - {failure[0]}")
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error[0]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_task_3_5_standalone_tests()
    sys.exit(0 if success else 1) 