#!/usr/bin/env python3
"""
Task 3.5 Test Suite: LLMAnalysisSupportModule
 
Test comprehensive functionality của LLMAnalysisSupportModule theo DoD requirements:
1. Định nghĩa LLMServiceRequest và LLMServiceResponse ✅ (Đã có trong llm_services/models.py)
2. LLMAnalysisSupportModule với function tạo LLMServiceRequest
3. Function nhận code string và tạo request với prompt_id="explain_code"
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Add backend to path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teams.code_analysis import (
    LLMAnalysisSupportModule, 
    CodeAnalysisContext,
    create_llm_analysis_support,
    create_explain_code_request
)

from src.teams.llm_services.models import (
    LLMServiceRequest, LLMServiceResponse, LLMConfig,
    LLMProviderType, LLMServiceStatus
)

from src.teams.code_analysis.models import (
    AnalysisFinding, AnalysisFindingType, AnalysisSeverity
)


class TestLLMAnalysisSupportModule(unittest.TestCase):
    """Test LLMAnalysisSupportModule functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.module = LLMAnalysisSupportModule()
        self.sample_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        
        self.custom_config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-4",
            temperature=0.5,
            max_tokens=1500
        )
    
    def test_module_initialization(self):
        """Test module khởi tạo đúng với config mặc định."""
        module = LLMAnalysisSupportModule()
        
        # Check default config
        self.assertIsNotNone(module.default_llm_config)
        self.assertEqual(module.default_llm_config.provider, LLMProviderType.OPENAI)
        self.assertEqual(module.default_llm_config.model, "gpt-3.5-turbo")
        self.assertEqual(module.default_llm_config.temperature, 0.3)
    
    def test_module_initialization_with_custom_config(self):
        """Test module khởi tạo với custom config."""
        module = LLMAnalysisSupportModule(default_llm_config=self.custom_config)
        
        self.assertEqual(module.default_llm_config, self.custom_config)
        self.assertEqual(module.default_llm_config.model, "gpt-4")
    
    def test_create_explain_code_request(self):
        """Test tạo explain_code request - DoD requirement chính."""
        request = self.module.create_explain_code_request(
            code_snippet=self.sample_code,
            language="python"
        )
        
        # Check request structure
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "explain_code")
        self.assertEqual(request.context_data["code_snippet"], self.sample_code)
        self.assertEqual(request.context_data["language"], "python")
        self.assertEqual(request.user_id, "code_analysis_team")
        self.assertIn("explain_code_", request.request_id)
        
        # Check LLM config
        self.assertEqual(request.llm_config.provider, LLMProviderType.OPENAI)
        self.assertEqual(request.llm_config.model, "gpt-3.5-turbo")
    
    def test_create_explain_code_request_with_custom_config(self):
        """Test tạo explain_code request với custom LLM config."""
        request = self.module.create_explain_code_request(
            code_snippet=self.sample_code,
            language="javascript",
            llm_config=self.custom_config,
            additional_context={"framework": "React"}
        )
        
        self.assertEqual(request.llm_config, self.custom_config)
        self.assertEqual(request.context_data["language"], "javascript")
        self.assertEqual(request.context_data["framework"], "React")
    
    def test_create_analyze_function_request(self):
        """Test tạo analyze_function request."""
        request = self.module.create_analyze_function_request(
            function_name="fibonacci",
            function_code=self.sample_code,
            language="python",
            context="Recursive implementation"
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "analyze_function")
        self.assertEqual(request.context_data["function_name"], "fibonacci")
        self.assertEqual(request.context_data["function_code"], self.sample_code)
        self.assertEqual(request.context_data["context"], "Recursive implementation")
    
    def test_create_find_issues_request(self):
        """Test tạo find_issues request."""
        request = self.module.create_find_issues_request(
            code_content=self.sample_code,
            language="python",
            file_path="/path/to/fibonacci.py"
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "find_issues")
        self.assertEqual(request.context_data["code_content"], self.sample_code)
        self.assertEqual(request.context_data["file_path"], "/path/to/fibonacci.py")
        self.assertEqual(request.priority, 3)  # Higher priority for issue detection
    
    def test_create_review_changes_request(self):
        """Test tạo review_changes request."""
        diff_content = "+    # Added comment\n     if n <= 1:"
        
        request = self.module.create_review_changes_request(
            file_path="fibonacci.py",
            diff_content=diff_content,
            pr_context="Optimization PR"
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "review_changes")
        self.assertEqual(request.context_data["file_path"], "fibonacci.py")
        self.assertEqual(request.context_data["diff_content"], diff_content)
        self.assertEqual(request.context_data["pr_context"], "Optimization PR")
        self.assertEqual(request.priority, 1)  # Highest priority for PR reviews
    
    def test_create_suggest_improvements_request(self):
        """Test tạo suggest_improvements request."""
        request = self.module.create_suggest_improvements_request(
            code_content=self.sample_code,
            language="python",
            focus_areas=["performance", "readability"]
        )
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "suggest_improvements")
        self.assertEqual(request.context_data["focus_areas"], "performance, readability")
        self.assertEqual(request.priority, 4)  # Lower priority for improvements
    
    def test_create_context_from_code(self):
        """Test tạo CodeAnalysisContext từ code."""
        context = self.module.create_context_from_code(
            code_snippet=self.sample_code,
            language="python",
            file_path="/path/to/file.py",
            analysis_type="find_issues"
        )
        
        self.assertIsInstance(context, CodeAnalysisContext)
        self.assertEqual(context.code_snippet, self.sample_code)
        self.assertEqual(context.language, "python")
        self.assertEqual(context.file_path, "/path/to/file.py")
        self.assertEqual(context.analysis_type, "find_issues")
        self.assertEqual(context.additional_context, {})
    
    def test_process_llm_response_to_finding_success(self):
        """Test chuyển đổi successful LLM response thành AnalysisFinding."""
        # Create mock successful response
        response = LLMServiceResponse(
            response_text="This function implements a recursive Fibonacci sequence...",
            status=LLMServiceStatus.SUCCESS,
            request_id="test_123",
            model_used="gpt-3.5-turbo",
            response_time_ms=500.0,
            tokens_used=150
        )
        
        context = CodeAnalysisContext(
            code_snippet=self.sample_code,
            language="python",
            file_path="/path/to/fibonacci.py",
            analysis_type="explain_code"
        )
        
        finding = self.module.process_llm_response_to_finding(response, context)
        
        self.assertIsNotNone(finding)
        self.assertIsInstance(finding, AnalysisFinding)
        self.assertEqual(finding.title, "LLM Analysis: explain_code")
        self.assertEqual(finding.description, response.response_text)
        self.assertEqual(finding.file_path, "/path/to/fibonacci.py")
        self.assertEqual(finding.analysis_module, "llm_analysis_support")
        self.assertEqual(finding.confidence_score, 0.8)
        
        # Check metadata
        self.assertEqual(finding.metadata["llm_model"], "gpt-3.5-turbo")
        self.assertEqual(finding.metadata["tokens_used"], 150)
        self.assertEqual(finding.metadata["request_id"], "test_123")
    
    def test_process_llm_response_to_finding_error(self):
        """Test xử lý LLM response có lỗi."""
        response = LLMServiceResponse(
            response_text="",
            status=LLMServiceStatus.ERROR,
            error_message="API key invalid"
        )
        
        context = CodeAnalysisContext(
            code_snippet=self.sample_code,
            analysis_type="explain_code"
        )
        
        finding = self.module.process_llm_response_to_finding(response, context)
        
        self.assertIsNone(finding)
    
    def test_set_default_config(self):
        """Test cập nhật default config."""
        new_config = LLMConfig(
            provider=LLMProviderType.GOOGLE_GENAI,
            model="gemini-pro",
            temperature=0.7
        )
        
        self.module.set_default_config(new_config)
        
        self.assertEqual(self.module.default_llm_config, new_config)
        self.assertEqual(self.module.default_llm_config.provider, LLMProviderType.GOOGLE_GENAI)
    
    def test_get_supported_analysis_types(self):
        """Test lấy danh sách analysis types được hỗ trợ."""
        types = self.module.get_supported_analysis_types()
        
        expected_types = [
            "explain_code",
            "analyze_function", 
            "find_issues",
            "review_changes",
            "suggest_improvements"
        ]
        
        self.assertEqual(types, expected_types)
        self.assertIn("explain_code", types)  # DoD requirement
    
    def test_request_id_uniqueness(self):
        """Test request IDs là unique."""
        request1 = self.module.create_explain_code_request(self.sample_code)
        request2 = self.module.create_explain_code_request(self.sample_code)
        
        self.assertNotEqual(request1.request_id, request2.request_id)
        self.assertIn("explain_code_", request1.request_id)
        self.assertIn("explain_code_", request2.request_id)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_create_llm_analysis_support(self):
        """Test factory function."""
        module = create_llm_analysis_support()
        
        self.assertIsInstance(module, LLMAnalysisSupportModule)
        self.assertIsNotNone(module.default_llm_config)
    
    def test_create_explain_code_request_convenience(self):
        """Test convenience function để tạo explain_code request."""
        code = "print('Hello World')"
        request = create_explain_code_request(code, "python")
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.prompt_id, "explain_code")
        self.assertEqual(request.context_data["code_snippet"], code)
        self.assertEqual(request.context_data["language"], "python")


class TestDoD35Compliance(unittest.TestCase):
    """Test DoD compliance cho Task 3.5."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.module = LLMAnalysisSupportModule()
        self.test_code = """def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)"""
    
    def test_dod_llm_service_request_structure(self):
        """DoD: LLMServiceRequest chứa prompt_id, context_data, llm_config."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Check required fields
        self.assertTrue(hasattr(request, 'prompt_id'))
        self.assertTrue(hasattr(request, 'context_data'))
        self.assertTrue(hasattr(request, 'llm_config'))
        
        # Check values
        self.assertEqual(request.prompt_id, "explain_code")
        self.assertIsInstance(request.context_data, dict)
        self.assertIn("code_snippet", request.context_data)
        self.assertIsInstance(request.llm_config, LLMConfig)
    
    def test_dod_llm_service_response_structure(self):
        """DoD: LLMServiceResponse chứa response_text và status."""
        # Test with mock response
        response = LLMServiceResponse(
            response_text="This function calculates the average...",
            status=LLMServiceStatus.SUCCESS
        )
        
        # Check required fields
        self.assertTrue(hasattr(response, 'response_text'))
        self.assertTrue(hasattr(response, 'status'))
        
        # Check values
        self.assertEqual(response.response_text, "This function calculates the average...")
        self.assertEqual(response.status, LLMServiceStatus.SUCCESS)
        
        # Test helper methods
        self.assertTrue(response.is_success())
        self.assertFalse(response.is_error())
    
    def test_dod_module_accept_code_string(self):
        """DoD: Module có hàm nhận một đoạn code (string)."""
        # Test main DoD requirement method
        request = self.module.create_explain_code_request(self.test_code)
        
        self.assertIsInstance(request, LLMServiceRequest)
        self.assertEqual(request.context_data["code_snippet"], self.test_code)
    
    def test_dod_create_explain_code_request(self):
        """DoD: Hàm tạo LLMServiceRequest với prompt_id="explain_code" và context_data."""
        request = self.module.create_explain_code_request(
            code_snippet=self.test_code,
            language="python"
        )
        
        # Check DoD requirements exactly
        self.assertEqual(request.prompt_id, "explain_code")
        self.assertEqual(request.context_data["code_snippet"], self.test_code)
        self.assertIsInstance(request.llm_config, LLMConfig)
        
        # Check return type
        self.assertIsInstance(request, LLMServiceRequest)
    
    def test_dod_default_llm_config(self):
        """DoD: Sử dụng cấu hình LLM mặc định."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Should use default config when none provided
        self.assertEqual(request.llm_config.provider, LLMProviderType.OPENAI)
        self.assertEqual(request.llm_config.model, "gpt-3.5-turbo")
        self.assertIsNotNone(request.llm_config.temperature)
    
    def test_dod_integration_with_llm_services(self):
        """DoD: Module tạo request compatible với TEAM LLM Services."""
        request = self.module.create_explain_code_request(self.test_code)
        
        # Request should be compatible with LLM Services
        self.assertIsInstance(request, LLMServiceRequest)
        
        # Should have all fields needed by LLM Gateway
        self.assertIsNotNone(request.prompt_id)
        self.assertIsNotNone(request.context_data)
        self.assertIsNotNone(request.llm_config)
        self.assertIsNotNone(request.request_id)
        self.assertIsNotNone(request.user_id)
        
        # Verify the request structure matches what LLM Gateway expects
        expected_fields = ['prompt_text', 'prompt_id', 'context_data', 'llm_config']
        for field in expected_fields:
            self.assertTrue(hasattr(request, field), f"Missing field: {field}")


def run_task_3_5_tests():
    """Run all Task 3.5 tests."""
    print("=" * 70)
    print("  Task 3.5: LLMAnalysisSupportModule Test Suite")
    print("=" * 70)
    print("Testing TEAM Code Analysis LLMAnalysisSupportModule implementation")
    print("DoD Requirements:")
    print("1. ✅ LLMServiceRequest/Response models (pre-existing)")
    print("2. 🧪 LLMAnalysisSupportModule với function nhận code string")
    print("3. 🧪 Function tạo LLMServiceRequest với prompt_id='explain_code'")
    print("4. 🧪 Integration với TEAM LLM Services")
    print()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestLLMAnalysisSupportModule))
    suite.addTest(unittest.makeSuite(TestConvenienceFunctions))
    suite.addTest(unittest.makeSuite(TestDoD35Compliance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("  Task 3.5 Test Results")
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
        print("\n🎉 Task 3.5 DoD FULLY COMPLIANT!")
        print("✅ LLMServiceRequest/Response models available")
        print("✅ LLMAnalysisSupportModule implemented")
        print("✅ create_explain_code_request function working")
        print("✅ Integration với TEAM LLM Services ready")
        print("🚀 Ready for Task 3.6: Orchestrator Agent LLM routing")
    else:
        print(f"\n⚠️  {failures + errors} tests failed. DoD not fully met.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_task_3_5_tests()
    sys.exit(0 if success else 1) 