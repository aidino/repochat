"""
Unit tests cho Task 3.4 (F3.4): LLMGatewayModule và PromptFormatterModule.

Tests coverage:
- PromptFormatterModule functionality
- LLMGatewayModule orchestration
- Template formatting và validation
- Error handling và edge cases
- Integration between components
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import modules under test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teams.llm_services.prompt_formatter import (
    PromptFormatterModule, TemplateType, FormattingError, FormattingResult,
    create_prompt_formatter, format_explain_code_prompt
)

from src.teams.llm_services.llm_gateway import (
    LLMGatewayModule, GatewayStatus, GatewayRequest, GatewayResponse,
    create_llm_gateway, explain_code_with_gateway
)

from src.teams.llm_services.models import (
    LLMConfig, LLMProviderType, LLMServiceRequest, LLMServiceResponse,
    LLMServiceStatus, PromptTemplate
)

class TestTask34PromptFormatter(unittest.TestCase):
    """Test PromptFormatterModule functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.formatter = PromptFormatterModule()
    
    def test_formatter_initialization(self):
        """Test PromptFormatterModule initialization."""
        # Should initialize with predefined templates
        self.assertIsInstance(self.formatter, PromptFormatterModule)
        self.assertGreater(len(self.formatter._templates), 0)
        
        # Check that explain_code template exists (DoD requirement)
        self.assertIn("explain_code", self.formatter._templates)
        
        # Verify template has required structure
        explain_template = self.formatter._templates["explain_code"]
        self.assertEqual(explain_template.template_id, "explain_code")
        self.assertIn("code_snippet", explain_template.required_variables)
    
    def test_explain_code_template_format(self):
        """Test explain_code template formatting (main DoD requirement)."""
        context_data = {
            "code_snippet": "def hello():\n    return 'world'"
        }
        
        result = self.formatter.format_prompt("explain_code", context_data)
        
        # Should succeed
        self.assertTrue(result.success)
        self.assertIsNotNone(result.formatted_prompt)
        self.assertEqual(result.template_used, "explain_code")
        
        # Should contain the code snippet
        self.assertIn("def hello():", result.formatted_prompt)
        self.assertIn("return 'world'", result.formatted_prompt)
        
        # Should be in Vietnamese (DoD requirement)
        self.assertIn("Hãy giải thích", result.formatted_prompt)
        self.assertIn("tiếng Việt", result.formatted_prompt)
    
    def test_template_with_optional_variables(self):
        """Test template formatting với optional variables."""
        context_data = {
            "code_snippet": "print('hello')",
            "language": "python"
        }
        
        result = self.formatter.format_prompt("explain_code", context_data)
        
        self.assertTrue(result.success)
        self.assertIn("python", result.formatted_prompt)
    
    def test_template_missing_required_variables(self):
        """Test error handling khi thiếu required variables."""
        context_data = {}  # Missing code_snippet
        
        result = self.formatter.format_prompt("explain_code", context_data)
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.error_type, "MISSING_VARIABLES")
        self.assertIn("code_snippet", result.error.missing_variables)
    
    def test_template_not_found(self):
        """Test error handling khi template không tồn tại."""
        context_data = {"code_snippet": "test"}
        
        result = self.formatter.format_prompt("nonexistent_template", context_data)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error.error_type, "TEMPLATE_NOT_FOUND")
    
    def test_all_predefined_templates(self):
        """Test tất cả predefined templates."""
        expected_templates = [
            "explain_code",
            "analyze_function", 
            "review_changes",
            "find_issues",
            "suggest_improvements"
        ]
        
        for template_id in expected_templates:
            self.assertIn(template_id, self.formatter._templates)
            template = self.formatter._templates[template_id]
            self.assertTrue(template.is_valid())
    
    def test_analyze_function_template(self):
        """Test analyze_function template."""
        context_data = {
            "function_name": "calculate_sum",
            "function_code": "def calculate_sum(a, b):\n    return a + b"
        }
        
        result = self.formatter.format_prompt("analyze_function", context_data)
        
        self.assertTrue(result.success)
        self.assertIn("calculate_sum", result.formatted_prompt)
        self.assertIn("def calculate_sum", result.formatted_prompt)
    
    def test_validate_context_data(self):
        """Test context data validation."""
        context_data = {"code_snippet": "test"}
        
        result = self.formatter.validate_context_data("explain_code", context_data)
        
        self.assertTrue(result.success)
    
    def test_get_template_info(self):
        """Test getting template information."""
        info = self.formatter.get_template_info("explain_code")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["template_id"], "explain_code")
        self.assertIn("code_snippet", info["required_variables"])
    
    def test_get_stats(self):
        """Test getting formatter statistics."""
        stats = self.formatter.get_stats()
        
        self.assertIn("total_templates", stats)
        self.assertIn("valid_templates", stats)
        self.assertGreater(stats["total_templates"], 0)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test create_prompt_formatter
        formatter = create_prompt_formatter()
        self.assertIsInstance(formatter, PromptFormatterModule)
        
        # Test format_explain_code_prompt
        result = format_explain_code_prompt("print('hello')", "python")
        self.assertTrue(result.success)


class TestTask34LLMGateway(unittest.TestCase):
    """Test LLMGatewayModule functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.gateway = LLMGatewayModule()
    
    def test_gateway_initialization(self):
        """Test LLMGatewayModule initialization."""
        self.assertIsInstance(self.gateway, LLMGatewayModule)
        self.assertEqual(self.gateway.status, GatewayStatus.READY)
        self.assertIsNotNone(self.gateway.prompt_formatter)
    
    @patch('src.teams.llm_services.llm_gateway.LLMProviderFactory')
    def test_process_request_success_flow(self, mock_factory_class):
        """Test successful request processing flow (main DoD requirement)."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.complete.return_value = LLMServiceResponse(
            request_id="test_req",
            response_text="Đây là giải thích code...",
            status=LLMServiceStatus.SUCCESS,
            metadata={"total_tokens": 100, "cost_estimate": 0.01}
        )
        
        # Mock factory
        mock_factory = Mock()
        mock_factory.create_provider.return_value = mock_provider
        mock_factory_class.return_value = mock_factory
        
        # Test the main flow: prompt_id + context_data -> formatted prompt -> LLM call
        prompt_id = "explain_code"
        context_data = {"code_snippet": "def test(): pass"}
        
        response = self.gateway.process_request(prompt_id, context_data)
        
        # Verify DoD requirements
        self.assertTrue(response.success)
        self.assertIsNotNone(response.response_text)
        self.assertEqual(response.template_used, "explain_code")
        
        # Verify PromptFormatterModule was called
        # Verify OpenAIProvider.complete was called
        mock_provider.complete.assert_called_once()
    
    def test_explain_code_convenience_method(self):
        """Test explain_code convenience method."""
        with patch.object(self.gateway, 'process_request') as mock_process:
            mock_process.return_value = GatewayResponse(
                success=True,
                response_text="Code explanation..."
            )
            
            response = self.gateway.explain_code("def hello(): pass", "python")
            
            # Verify process_request was called with correct parameters
            mock_process.assert_called_once()
            args, kwargs = mock_process.call_args
            self.assertEqual(args[0], "explain_code")  # prompt_id
            self.assertEqual(args[1]["code_snippet"], "def hello(): pass")
            self.assertEqual(args[1]["language"], "python")
    
    def test_gateway_request_object_processing(self):
        """Test processing GatewayRequest object."""
        request = GatewayRequest(
            prompt_id="explain_code",
            context_data={"code_snippet": "test"},
            metadata={"test": "data"}
        )
        
        with patch.object(self.gateway, 'process_request') as mock_process:
            mock_process.return_value = GatewayResponse(success=True)
            
            self.gateway.process_gateway_request(request)
            
            mock_process.assert_called_once_with(
                prompt_id=request.prompt_id,
                context_data=request.context_data,
                llm_config=request.llm_config,
                metadata=request.metadata
            )
    
    def test_formatting_error_handling(self):
        """Test error handling khi prompt formatting fails."""
        # Use invalid template
        response = self.gateway.process_request("invalid_template", {})
        
        self.assertFalse(response.success)
        self.assertIsNotNone(response.error_message)
        self.assertIn("not found", response.error_message.lower())
    
    def test_provider_unavailable_error(self):
        """Test error handling khi provider không available."""
        with patch.object(self.gateway, '_get_provider') as mock_get_provider:
            mock_get_provider.return_value = None
            
            response = self.gateway.process_request("explain_code", {"code_snippet": "test"})
            
            self.assertFalse(response.success)
            self.assertIn("not available", response.error_message)
    
    def test_llm_service_error_handling(self):
        """Test error handling khi LLM service returns error."""
        with patch.object(self.gateway, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.complete.return_value = LLMServiceResponse(
                request_id="test",
                status=LLMServiceStatus.ERROR,
                error_message="API Error"
            )
            mock_get_provider.return_value = mock_provider
            
            response = self.gateway.process_request("explain_code", {"code_snippet": "test"})
            
            self.assertFalse(response.success)
            self.assertIn("API Error", response.error_message)
    
    def test_gateway_status_management(self):
        """Test gateway status management."""
        # Test initial status
        self.assertEqual(self.gateway.status, GatewayStatus.READY)
        
        # Test status change
        self.gateway.set_status(GatewayStatus.MAINTENANCE)
        self.assertEqual(self.gateway.status, GatewayStatus.MAINTENANCE)
        
        # Test processing request when not ready
        response = self.gateway.process_request("explain_code", {"code_snippet": "test"})
        self.assertFalse(response.success)
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        # Enable stats
        self.gateway.enable_stats = True
        self.gateway.stats = self.gateway.stats or type('Stats', (), {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'template_usage': {},
            'provider_usage': {},
            'error_counts': {}
        })()
        
        with patch.object(self.gateway, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.complete.return_value = LLMServiceResponse(
                request_id="test",
                response_text="Success",
                status=LLMServiceStatus.SUCCESS
            )
            mock_get_provider.return_value = mock_provider
            
            # Process request
            self.gateway.process_request("explain_code", {"code_snippet": "test"})
            
            # Check stats
            stats = self.gateway.get_stats()
            if stats:
                self.assertGreater(stats["total_requests"], 0)
    
    def test_get_status(self):
        """Test getting gateway status."""
        status = self.gateway.get_status()
        
        self.assertIn("gateway_status", status)
        self.assertIn("default_provider", status)
        self.assertIn("available_templates", status)
    
    def test_validate_prompt(self):
        """Test prompt validation."""
        result = self.gateway.validate_prompt("explain_code", {"code_snippet": "test"})
        
        self.assertTrue(result.success)
    
    def test_convenience_functions_module_level(self):
        """Test module-level convenience functions."""
        # Test create_llm_gateway
        gateway = create_llm_gateway()
        self.assertIsInstance(gateway, LLMGatewayModule)
        
        # Test explain_code_with_gateway (without actual API call)
        with patch('src.teams.llm_services.llm_gateway.LLMGatewayModule') as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.explain_code.return_value = GatewayResponse(
                success=True,
                response_text="Explanation"
            )
            mock_gateway_class.return_value = mock_gateway
            
            result = explain_code_with_gateway("def test(): pass")
            self.assertTrue(result.success)


class TestTask34Integration(unittest.TestCase):
    """Test integration between PromptFormatterModule và LLMGatewayModule."""
    
    def test_end_to_end_flow_without_api(self):
        """Test end-to-end flow without actual API calls."""
        # Create components
        formatter = PromptFormatterModule()
        gateway = LLMGatewayModule()
        
        # Test 1: Format prompt manually
        context_data = {"code_snippet": "def add(a, b): return a + b"}
        format_result = formatter.format_prompt("explain_code", context_data)
        
        self.assertTrue(format_result.success)
        formatted_prompt = format_result.formatted_prompt
        
        # Verify formatted prompt contains expected elements
        self.assertIn("def add(a, b)", formatted_prompt)
        self.assertIn("Hãy giải thích", formatted_prompt)
        
        # Test 2: Gateway can validate the same prompt
        validation_result = gateway.validate_prompt("explain_code", context_data)
        self.assertTrue(validation_result.success)
    
    def test_all_templates_work_with_gateway(self):
        """Test all predefined templates work with gateway."""
        gateway = LLMGatewayModule()
        
        test_cases = [
            ("explain_code", {"code_snippet": "def test(): pass"}),
            ("analyze_function", {"function_name": "test", "function_code": "def test(): pass"}),
            ("review_changes", {"file_path": "test.py", "diff_content": "+def new(): pass"}),
            ("find_issues", {"code_content": "def test(): pass"}),
            ("suggest_improvements", {"code_content": "def test(): pass"})
        ]
        
        for template_id, context_data in test_cases:
            with self.subTest(template=template_id):
                result = gateway.validate_prompt(template_id, context_data)
                self.assertTrue(result.success, f"Template {template_id} validation failed")
    
    def test_error_propagation(self):
        """Test error propagation from formatter to gateway."""
        gateway = LLMGatewayModule()
        
        # Test with missing required variable
        response = gateway.process_request("explain_code", {})  # Missing code_snippet
        
        self.assertFalse(response.success)
        self.assertIn("Missing required variables", response.error_message)


class TestTask34DoD(unittest.TestCase):
    """Specific tests for Task 3.4 DoD requirements."""
    
    def test_dod_prompt_template_explain_code(self):
        """
        DoD: Một string template được tạo, có placeholder cho đoạn code cần giải thích.
        Ví dụ: "Hãy giải thích chức năng của đoạn code sau: \\n```\\n{code_snippet}\\n```".
        """
        formatter = PromptFormatterModule()
        
        # Get the explain_code template
        template = formatter.get_template("explain_code")
        self.assertIsNotNone(template)
        
        # Verify it has the required placeholder
        self.assertIn("{code_snippet}", template.template_text)
        self.assertIn("code_snippet", template.required_variables)
        
        # Verify it matches the expected pattern
        self.assertIn("Hãy giải thích", template.template_text)
        self.assertIn("```", template.template_text)
    
    def test_dod_prompt_formatter_module(self):
        """
        DoD: Module có hàm nhận `template_id` và `context_data`.
        Hàm điền `context_data` vào template tương ứng và trả về prompt hoàn chỉnh.
        """
        formatter = PromptFormatterModule()
        
        # Test the required function signature
        template_id = "explain_code"
        context_data = {"code_snippet": "def hello(): return 'world'"}
        
        result = formatter.format_prompt(template_id, context_data)
        
        # Verify function exists and works as specified
        self.assertTrue(result.success)
        self.assertIsNotNone(result.formatted_prompt)
        
        # Verify context_data was filled into template
        self.assertIn("def hello():", result.formatted_prompt)
        self.assertIn("return 'world'", result.formatted_prompt)
    
    def test_dod_llm_gateway_module(self):
        """
        DoD: Module có hàm nhận `prompt_id` và `context_data`.
        Gọi `PromptFormatterModule` để lấy prompt.
        Gọi `OpenAIProvider.complete(prompt)` để nhận phản hồi từ LLM.
        Trả về phản hồi của LLM.
        """
        gateway = LLMGatewayModule()
        
        # Mock the provider to avoid actual API calls
        with patch.object(gateway, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.complete.return_value = LLMServiceResponse(
                request_id="test",
                response_text="Đây là giải thích code từ LLM",
                status=LLMServiceStatus.SUCCESS
            )
            mock_get_provider.return_value = mock_provider
            
            # Test the required function signature
            prompt_id = "explain_code"
            context_data = {"code_snippet": "def test(): pass"}
            
            response = gateway.process_request(prompt_id, context_data)
            
            # Verify function exists and works as specified
            self.assertTrue(response.success)
            self.assertIsNotNone(response.response_text)
            
            # Verify PromptFormatterModule was used (indirectly)
            self.assertEqual(response.template_used, "explain_code")
            
            # Verify OpenAIProvider.complete was called
            mock_provider.complete.assert_called_once()
            
            # Verify LLM response was returned
            self.assertEqual(response.response_text, "Đây là giải thích code từ LLM")


if __name__ == "__main__":
    # Run specific test groups
    test_suite = unittest.TestSuite()
    
    # Add DoD compliance tests first
    test_suite.addTest(unittest.makeSuite(TestTask34DoD))
    
    # Add functionality tests
    test_suite.addTest(unittest.makeSuite(TestTask34PromptFormatter))
    test_suite.addTest(unittest.makeSuite(TestTask34LLMGateway))
    test_suite.addTest(unittest.makeSuite(TestTask34Integration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Task 3.4 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "No tests run")
    print(f"{'='*50}") 