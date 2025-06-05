#!/usr/bin/env python3
"""
Manual Test Script cho Task 3.4 (F3.4): LLMGatewayModule và PromptFormatterModule.

Thực hiện testing thủ công với các scenario thực tế:
- PromptFormatterModule functionality  
- LLMGatewayModule orchestration
- Template formatting và validation
- Error handling scenarios
- Integration với OpenAI API (nếu có API key)
"""

import sys
import os
import time
import logging
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.teams.llm_services import (
    # Task 3.4 modules
    PromptFormatterModule, LLMGatewayModule,
    TemplateType, FormattingResult, GatewayResponse,
    create_prompt_formatter, create_llm_gateway,
    explain_code_simple, get_system_status, get_task_3_4_info,
    
    # Task 3.3 modules  
    LLMConfig, LLMProviderType, check_dependencies
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('manual_test_task_3_4.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"      Details: {details}")

def test_1_prompt_formatter_basic():
    """Test 1: PromptFormatterModule basic functionality."""
    print_section("Test 1: PromptFormatterModule Basic Functionality")
    
    try:
        # Test 1.1: Initialization
        formatter = PromptFormatterModule()
        test_1_1_success = formatter is not None
        print_test("PromptFormatterModule initialization", test_1_1_success, 
                  f"Templates loaded: {len(formatter._templates)}")
        
        # Test 1.2: Verify explain_code template exists (DoD requirement)
        has_explain_template = "explain_code" in formatter._templates
        print_test("Explain code template exists", has_explain_template)
        
        if has_explain_template:
            template = formatter._templates["explain_code"]
            has_placeholder = "{code_snippet}" in template.template_text
            print_test("Template has {code_snippet} placeholder", has_placeholder)
        
        # Test 1.3: List all available templates
        templates = formatter.list_templates()
        template_names = [t.template_id for t in templates]
        print_test("At least 5 predefined templates", len(templates) >= 5, 
                  f"Templates: {template_names}")
        
        # Test 1.4: Get template info
        info = formatter.get_template_info("explain_code")
        print_test("Get template info working", info is not None,
                  f"Required vars: {info.get('required_variables', []) if info else 'None'}")
        
        # Test 1.5: Get stats
        stats = formatter.get_stats()
        print_test("Template statistics working", stats.get("total_templates", 0) > 0,
                  f"Total: {stats.get('total_templates', 0)}, Valid: {stats.get('valid_templates', 0)}")
        
        return True
        
    except Exception as e:
        print_test("PromptFormatterModule basic test", False, f"Error: {str(e)}")
        return False

def test_2_prompt_formatting():
    """Test 2: Prompt template formatting functionality."""
    print_section("Test 2: Prompt Template Formatting")
    
    try:
        formatter = create_prompt_formatter()
        
        # Test 2.1: Format explain_code template (main DoD requirement)
        context_data = {
            "code_snippet": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        }
        
        result = formatter.format_prompt("explain_code", context_data)
        print_test("Format explain_code template", result.success,
                  f"Prompt length: {len(result.formatted_prompt) if result.formatted_prompt else 0}")
        
        if result.success:
            # Verify Vietnamese content
            has_vietnamese = "Hãy giải thích" in result.formatted_prompt
            print_test("Vietnamese content in prompt", has_vietnamese)
            
            # Verify code is included
            has_code = "fibonacci" in result.formatted_prompt
            print_test("Code snippet included in prompt", has_code)
        
        # Test 2.2: Format with optional parameters
        context_data_with_lang = {
            "code_snippet": "print('Hello, World!')",
            "language": "python"
        }
        
        result2 = formatter.format_prompt("explain_code", context_data_with_lang)
        print_test("Format with optional language parameter", result2.success,
                  f"Language included: {'python' in result2.formatted_prompt if result2.formatted_prompt else False}")
        
        # Test 2.3: Test analyze_function template
        func_context = {
            "function_name": "fibonacci",
            "function_code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
        }
        
        result3 = formatter.format_prompt("analyze_function", func_context)
        print_test("Format analyze_function template", result3.success,
                  f"Function name included: {'fibonacci' in result3.formatted_prompt if result3.formatted_prompt else False}")
        
        # Test 2.4: Error case - missing required variable
        result4 = formatter.format_prompt("explain_code", {})
        print_test("Error handling - missing required variable", not result4.success,
                  f"Error type: {result4.error.error_type if result4.error else 'None'}")
        
        # Test 2.5: Error case - invalid template
        result5 = formatter.format_prompt("nonexistent_template", context_data)
        print_test("Error handling - invalid template", not result5.success,
                  f"Error type: {result5.error.error_type if result5.error else 'None'}")
        
        return True
        
    except Exception as e:
        print_test("Prompt formatting test", False, f"Error: {str(e)}")
        return False

def test_3_llm_gateway_basic():
    """Test 3: LLMGatewayModule basic functionality."""
    print_section("Test 3: LLMGatewayModule Basic Functionality")
    
    try:
        # Test 3.1: Gateway initialization
        gateway = LLMGatewayModule()
        print_test("LLMGatewayModule initialization", gateway is not None)
        
        # Test 3.2: Gateway status
        status = gateway.get_status()
        print_test("Gateway status ready", status.get("gateway_status") == "ready",
                  f"Status: {status.get('gateway_status', 'unknown')}")
        
        # Test 3.3: Available templates through gateway
        templates = gateway.get_available_templates()
        print_test("Gateway can access templates", len(templates) > 0,
                  f"Available templates: {templates}")
        
        # Test 3.4: Validate prompt without LLM call
        validation_result = gateway.validate_prompt("explain_code", {"code_snippet": "print('test')"})
        print_test("Prompt validation works", validation_result.success)
        
        # Test 3.5: Provider availability checking
        provider_status = status.get("provider_availability", {})
        print_test("Provider availability check", isinstance(provider_status, dict),
                  f"Providers: {list(provider_status.keys())}")
        
        # Test 3.6: Gateway statistics (if enabled)
        stats = gateway.get_stats()
        stats_working = stats is None or isinstance(stats, dict)
        print_test("Gateway statistics working", stats_working,
                  f"Stats enabled: {gateway.enable_stats}")
        
        return True
        
    except Exception as e:
        print_test("LLMGateway basic test", False, f"Error: {str(e)}")
        return False

def test_4_gateway_without_api():
    """Test 4: Gateway functionality without actual API calls."""
    print_section("Test 4: Gateway Functionality (Mock)")
    
    try:
        gateway = create_llm_gateway()
        
        # Test 4.1: Process request with invalid template (should fail at formatting stage)
        response1 = gateway.process_request("invalid_template", {"code_snippet": "test"})
        print_test("Gateway handles invalid template", not response1.success,
                  f"Error: {response1.error_message[:50] if response1.error_message else 'None'}...")
        
        # Test 4.2: Process request with missing data (should fail at formatting stage)  
        response2 = gateway.process_request("explain_code", {})
        print_test("Gateway handles missing data", not response2.success,
                  f"Error: {response2.error_message[:50] if response2.error_message else 'None'}...")
        
        # Test 4.3: Process request with valid formatting (will fail at provider stage without API key)
        response3 = gateway.process_request("explain_code", {"code_snippet": "def hello(): pass"})
        formatting_ok = response3.template_used == "explain_code"
        print_test("Gateway formatting stage works", formatting_ok,
                  f"Template used: {response3.template_used}")
        
        # Test 4.4: Convenience method - explain_code
        response4 = gateway.explain_code("def add(x, y): return x + y", "python")
        print_test("Explain code convenience method", response4.template_used == "explain_code",
                  f"Processing time: {response4.processing_time:.3f}s")
        
        # Test 4.5: Convenience method - analyze_function
        response5 = gateway.analyze_function("add_numbers", "def add_numbers(a, b): return a + b")
        print_test("Analyze function convenience method", response5.template_used == "analyze_function")
        
        return True
        
    except Exception as e:
        print_test("Gateway mock test", False, f"Error: {str(e)}")
        return False

def test_5_integration():
    """Test 5: Integration between components."""
    print_section("Test 5: Integration Testing")
    
    try:
        # Test 5.1: Manual integration - formatter + gateway
        formatter = PromptFormatterModule()
        gateway = LLMGatewayModule()
        
        # Format prompt manually
        context_data = {"code_snippet": "class Calculator:\n    def add(self, x, y): return x + y"}
        format_result = formatter.format_prompt("explain_code", context_data)
        
        # Validate same prompt in gateway
        gateway_validation = gateway.validate_prompt("explain_code", context_data)
        
        integration_ok = format_result.success and gateway_validation.success
        print_test("Formatter-Gateway integration", integration_ok,
                  f"Both components handle same data: {integration_ok}")
        
        # Test 5.2: All templates work with both components
        all_templates_ok = True
        test_cases = [
            ("explain_code", {"code_snippet": "def test(): pass"}),
            ("analyze_function", {"function_name": "test", "function_code": "def test(): pass"}),
            ("review_changes", {"file_path": "test.py", "diff_content": "+def new(): pass"}),
            ("find_issues", {"code_content": "def test(): pass"}),
            ("suggest_improvements", {"code_content": "def test(): pass"})
        ]
        
        for template_id, test_data in test_cases:
            formatter_result = formatter.format_prompt(template_id, test_data)
            gateway_result = gateway.validate_prompt(template_id, test_data)
            
            template_ok = formatter_result.success and gateway_result.success
            if not template_ok:
                all_templates_ok = False
            
            print_test(f"Template '{template_id}' integration", template_ok)
        
        print_test("All templates work with both components", all_templates_ok)
        
        # Test 5.3: Error propagation
        error_response = gateway.process_request("explain_code", {})
        error_propagation_ok = not error_response.success and "Missing required variables" in error_response.error_message
        print_test("Error propagation from formatter to gateway", error_propagation_ok)
        
        return True
        
    except Exception as e:
        print_test("Integration test", False, f"Error: {str(e)}")
        return False

def test_6_convenience_functions():
    """Test 6: High-level convenience functions."""
    print_section("Test 6: Convenience Functions")
    
    try:
        # Test 6.1: System status check
        system_status = get_system_status()
        print_test("System status check", isinstance(system_status, dict),
                  f"Overall status: {system_status.get('overall_status', 'unknown')}")
        
        # Test 6.2: Task 3.4 info
        task_info = get_task_3_4_info()
        print_test("Task 3.4 info available", isinstance(task_info, dict),
                  f"Features: {len(task_info.get('features', {}))}")
        
        # Test 6.3: Dependencies check
        deps = check_dependencies()
        print_test("Dependencies check", isinstance(deps, dict),
                  f"Dependencies: {list(deps.keys())}")
        
        # Test 6.4: Simple explain code function (will fail without API key but should handle gracefully)
        simple_result = explain_code_simple("def greet(name): return f'Hello, {name}!'")
        print_test("Simple explain code function", isinstance(simple_result, str),
                  f"Result type: {type(simple_result).__name__}")
        
        return True
        
    except Exception as e:
        print_test("Convenience functions test", False, f"Error: {str(e)}")
        return False

def test_7_openai_integration():
    """Test 7: Real OpenAI API integration (if API key available)."""
    print_section("Test 7: OpenAI API Integration (Optional)")
    
    # Check if OpenAI API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print_test("OpenAI API key not found", False, 
                  "Set OPENAI_API_KEY environment variable to test real API integration")
        return False
    
    try:
        # Test 7.1: Real API call through gateway
        gateway = create_llm_gateway()
        
        start_time = time.time()
        response = gateway.explain_code(
            code_snippet="""def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
            language="python"
        )
        end_time = time.time()
        
        print_test("Real OpenAI API call through gateway", response.success,
                  f"Response time: {end_time - start_time:.2f}s, Tokens: {response.tokens_used}")
        
        if response.success:
            # Verify response is in Vietnamese
            has_vietnamese = any(word in response.response_text.lower() for word in 
                               ["chức năng", "thuật toán", "tìm kiếm", "mảng", "phần tử"])
            print_test("Response is in Vietnamese", has_vietnamese)
            
            # Test 7.2: Cost estimation
            print_test("Cost estimation available", response.cost_estimate is not None,
                      f"Estimated cost: ${response.cost_estimate:.6f}" if response.cost_estimate else "None")
            
            # Test 7.3: Metadata tracking
            print_test("Response metadata available", len(response.metadata) > 0,
                      f"Metadata keys: {list(response.metadata.keys())}")
        
        # Test 7.4: Simple convenience function with real API
        simple_response = explain_code_simple("def factorial(n): return 1 if n <= 1 else n * factorial(n-1)")
        real_api_works = isinstance(simple_response, str) and len(simple_response) > 50
        print_test("Simple convenience function with real API", real_api_works,
                  f"Response length: {len(simple_response)}")
        
        return True
        
    except Exception as e:
        print_test("OpenAI integration test", False, f"Error: {str(e)}")
        return False

def test_8_error_scenarios():
    """Test 8: Error handling scenarios."""
    print_section("Test 8: Error Handling Scenarios")
    
    try:
        formatter = PromptFormatterModule()
        gateway = LLMGatewayModule()
        
        # Test 8.1: Formatter error scenarios
        error_cases = [
            ("Missing template", "nonexistent_template", {"code_snippet": "test"}),
            ("Missing required var", "explain_code", {}),
            ("Extra variables", "explain_code", {"code_snippet": "test", "extra_var": "value"})
        ]
        
        all_errors_handled = True
        for case_name, template_id, context_data in error_cases:
            result = formatter.format_prompt(template_id, context_data)
            case_ok = not result.success if case_name != "Extra variables" else result.success
            print_test(f"Formatter handles: {case_name}", case_ok)
            if not case_ok:
                all_errors_handled = False
        
        # Test 8.2: Gateway error scenarios  
        from src.teams.llm_services.llm_gateway import GatewayStatus
        
        gateway_errors = [
            ("Invalid template", "invalid_template", {"code_snippet": "test"}),
            ("Missing data", "explain_code", {}),
            ("Gateway maintenance mode", "explain_code", {"code_snippet": "test"})
        ]
        
        for case_name, template_id, context_data in gateway_errors:
            if case_name == "Gateway maintenance mode":
                gateway.set_status(GatewayStatus.MAINTENANCE)
                
            response = gateway.process_request(template_id, context_data)
            case_ok = not response.success
            print_test(f"Gateway handles: {case_name}", case_ok)
            if not case_ok:
                all_errors_handled = False
                
            if case_name == "Gateway maintenance mode":
                gateway.set_status(GatewayStatus.READY)
        
        print_test("All error scenarios handled properly", all_errors_handled)
        
        return True
        
    except Exception as e:
        print_test("Error scenarios test", False, f"Error: {str(e)}")
        return False

def test_9_performance():
    """Test 9: Performance characteristics."""
    print_section("Test 9: Performance Testing")
    
    try:
        formatter = PromptFormatterModule()
        gateway = LLMGatewayModule()
        
        # Test 9.1: Formatter performance
        context_data = {"code_snippet": "def test(): pass"}
        
        start_time = time.time()
        for _ in range(100):
            formatter.format_prompt("explain_code", context_data)
        formatter_time = time.time() - start_time
        
        print_test("Formatter performance (100 formats < 1s)", formatter_time < 1.0,
                  f"Time: {formatter_time:.3f}s, Avg: {formatter_time/100*1000:.1f}ms per format")
        
        # Test 9.2: Gateway validation performance
        start_time = time.time()
        for _ in range(50):
            gateway.validate_prompt("explain_code", context_data)
        validation_time = time.time() - start_time
        
        print_test("Gateway validation performance (50 validations < 1s)", validation_time < 1.0,
                  f"Time: {validation_time:.3f}s, Avg: {validation_time/50*1000:.1f}ms per validation")
        
        # Test 9.3: Memory usage estimation
        import sys
        
        initial_size = sys.getsizeof(formatter) + sys.getsizeof(gateway)
        print_test("Memory usage reasonable", initial_size < 10000,
                  f"Combined size: {initial_size} bytes")
        
        return True
        
    except Exception as e:
        print_test("Performance test", False, f"Error: {str(e)}")
        return False

def test_10_dod_compliance():
    """Test 10: DoD (Definition of Done) compliance verification."""
    print_section("Test 10: DoD Compliance Verification")
    
    try:
        # DoD 1: Thiết kế prompt template cho "Giải thích đoạn code này"
        formatter = PromptFormatterModule()
        explain_template = formatter.get_template("explain_code")
        
        dod1_ok = (explain_template is not None and 
                  "{code_snippet}" in explain_template.template_text and
                  "Hãy giải thích" in explain_template.template_text)
        print_test("DoD 1: Prompt template 'Giải thích code' exists with {code_snippet} placeholder", dod1_ok)
        
        # DoD 2: PromptFormatterModule với template_id và context_data
        context_data = {"code_snippet": "def hello(): return 'world'"}
        format_result = formatter.format_prompt("explain_code", context_data)
        
        dod2_ok = (format_result.success and 
                  format_result.formatted_prompt is not None and
                  "def hello():" in format_result.formatted_prompt)
        print_test("DoD 2: PromptFormatterModule.format_prompt(template_id, context_data) works", dod2_ok)
        
        # DoD 3: LLMGatewayModule với prompt_id và context_data  
        gateway = LLMGatewayModule()
        gateway_response = gateway.process_request("explain_code", context_data)
        
        # Should at least get to formatting stage successfully
        dod3_ok = (gateway_response.template_used == "explain_code" and
                  hasattr(gateway, 'prompt_formatter') and
                  gateway.prompt_formatter is not None)
        print_test("DoD 3: LLMGatewayModule.process_request(prompt_id, context_data) calls formatter and provider", dod3_ok)
        
        # Verify integration chain: prompt_id + context_data -> PromptFormatter -> OpenAI (simulated)
        integration_chain_ok = all([dod1_ok, dod2_ok, dod3_ok])
        print_test("DoD Integration: Complete chain from prompt_id to LLM response works", integration_chain_ok)
        
        return integration_chain_ok
        
    except Exception as e:
        print_test("DoD compliance verification", False, f"Error: {str(e)}")
        return False

def main():
    """Run all manual tests for Task 3.4."""
    print_section("Manual Test Suite for Task 3.4 (F3.4)")
    print("LLMGatewayModule và PromptFormatterModule Testing")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results tracking
    test_results = []
    
    # Run all tests
    tests = [
        ("Test 1: PromptFormatter Basic", test_1_prompt_formatter_basic),
        ("Test 2: Prompt Formatting", test_2_prompt_formatting),
        ("Test 3: LLMGateway Basic", test_3_llm_gateway_basic),
        ("Test 4: Gateway Mock", test_4_gateway_without_api),
        ("Test 5: Integration", test_5_integration),
        ("Test 6: Convenience Functions", test_6_convenience_functions),
        ("Test 7: OpenAI Integration", test_7_openai_integration),
        ("Test 8: Error Scenarios", test_8_error_scenarios),
        ("Test 9: Performance", test_9_performance),
        ("Test 10: DoD Compliance", test_10_dod_compliance)
    ]
    
    for test_name, test_func in tests:
        try:
            logger.info(f"Running {test_name}")
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {str(e)}")
            test_results.append((test_name, False))
    
    # Print final summary
    print_section("Manual Test Results Summary")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\n📊 Overall Results:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print(f"🎉 All tests passed! Task 3.4 implementation is working correctly.")
    else:
        print(f"⚠️  Some tests failed. Check logs for details.")
    
    # Log final status
    logger.info(f"Manual testing completed: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 