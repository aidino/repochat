#!/usr/bin/env python3
"""
DoD Compliance Test cho Task 3.4

Test các DoD requirements mà không cần OpenAI API key thật:
1. Prompt Template Design với placeholder {code_snippet}
2. PromptFormatterModule.format_prompt(template_id, context_data)
3. LLMGatewayModule.process_request(prompt_id, context_data) architecture
"""

import sys
import os
import time
import logging

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.teams.llm_services import (
    # Task 3.4 refactored modules
    TemplateLoader, PromptFormatterModule, LLMGatewayModule,
    create_template_loader, create_prompt_formatter, create_llm_gateway,
    
    # Task 3.3 LLM infrastructure
    LLMConfig, LLMProviderType, get_default_openai_config
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_test(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    └─ {details}")

def test_dod_1_template_design():
    """
    DoD 1: Prompt Template Design
    - Template "Giải thích code" có placeholder {code_snippet}
    """
    print_section("DoD 1: Prompt Template Design")
    
    try:
        # Test template loading
        loader = create_template_loader()
        result = loader.load_all_templates()
        
        if not result.success:
            print_test("Template loading failed", False, f"Could not load templates: {result.errors}")
            return False
        
        # Find explain_code template
        explain_template = None
        for template in result.templates_loaded:
            if template.template_id == "explain_code":
                explain_template = template
                break
        
        if not explain_template:
            print_test("Template 'explain_code' not found", False)
            return False
        
        print_test("Template 'explain_code' found", True, f"Name: {explain_template.name}")
        
        # Check for {code_snippet} placeholder
        has_placeholder = "{code_snippet}" in explain_template.template_text
        print_test("Template contains {code_snippet} placeholder", has_placeholder)
        
        # Check required variables
        has_required_var = "code_snippet" in explain_template.required_variables
        print_test("Template has 'code_snippet' in required_variables", has_required_var)
        
        # Check Vietnamese content
        has_vietnamese = "Hãy giải thích" in explain_template.template_text
        print_test("Template has Vietnamese content", has_vietnamese)
        
        return has_placeholder and has_required_var and has_vietnamese
        
    except Exception as e:
        print_test("DoD 1 test failed", False, f"Error: {str(e)}")
        return False

def test_dod_2_prompt_formatter():
    """
    DoD 2: PromptFormatterModule
    - Có function format_prompt(template_id, context_data)
    - Function hoạt động đúng với template "explain_code"
    """
    print_section("DoD 2: PromptFormatterModule.format_prompt()")
    
    try:
        # Create formatter
        formatter = create_prompt_formatter()
        print_test("PromptFormatterModule created", True)
        
        # Check if format_prompt method exists
        has_format_method = hasattr(formatter, 'format_prompt')
        print_test("Has format_prompt method", has_format_method)
        
        if not has_format_method:
            return False
        
        # Test format_prompt with explain_code
        context_data = {
            "code_snippet": """def calculate_factorial(n):
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)""",
            "language": "python"
        }
        
        result = formatter.format_prompt("explain_code", context_data)
        print_test("format_prompt call successful", result.success)
        
        if result.success:
            # Check formatted prompt contains input code
            contains_code = "calculate_factorial" in result.formatted_prompt
            print_test("Formatted prompt contains input code", contains_code)
            
            # Check formatted prompt is in Vietnamese
            contains_vietnamese = "Hãy giải thích" in result.formatted_prompt
            print_test("Formatted prompt in Vietnamese", contains_vietnamese)
            
            # Show preview
            print("📝 Formatted prompt preview:")
            preview = result.formatted_prompt[:200] + "..." if len(result.formatted_prompt) > 200 else result.formatted_prompt
            print(f"    {preview}")
            
            return contains_code and contains_vietnamese
        else:
            print_test("format_prompt failed", False, result.error.message if result.error else "Unknown error")
            return False
            
    except Exception as e:
        print_test("DoD 2 test failed", False, f"Error: {str(e)}")
        return False

def test_dod_3_llm_gateway():
    """
    DoD 3: LLMGatewayModule
    - Có function process_request(prompt_id, context_data)
    - Function tích hợp PromptFormatterModule để format prompt
    - Function có architecture để gọi LLM (không cần API key thật)
    """
    print_section("DoD 3: LLMGatewayModule.process_request()")
    
    try:
        # Create gateway
        gateway = create_llm_gateway()
        print_test("LLMGatewayModule created", True)
        
        # Check if process_request method exists
        has_process_method = hasattr(gateway, 'process_request')
        print_test("Has process_request method", has_process_method)
        
        if not has_process_method:
            return False
        
        # Check if gateway has prompt_formatter
        has_formatter = hasattr(gateway, 'prompt_formatter')
        print_test("Gateway has PromptFormatterModule", has_formatter)
        
        # Check if gateway has provider infrastructure
        has_provider_factory = hasattr(gateway, 'provider_factory')
        print_test("Gateway has provider infrastructure", has_provider_factory)
        
        # Test process_request method signature and integration
        context_data = {
            "code_snippet": "def hello():\n    return 'world'",
            "language": "python"
        }
        
        # Test với config không có API key (sẽ fail ở LLM call nhưng architecture OK)
        config = LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key="test_key"  # Fake key
        )
        
        try:
            response = gateway.process_request("explain_code", context_data, config)
            
            # Response should have correct structure even if LLM call fails
            has_correct_structure = hasattr(response, 'success') and hasattr(response, 'template_used')
            print_test("Response has correct structure", has_correct_structure)
            
            # Should show template was used (formatter worked)
            template_used = response.template_used == "explain_code"
            print_test("Template 'explain_code' was used", template_used)
            
            # Check that formatting step worked (even if LLM fails)
            formatting_worked = response.template_used is not None
            print_test("Prompt formatting integration works", formatting_worked)
            
            if response.success:
                print_test("Full LLM integration works", True, "OpenAI call succeeded")
                return True
            else:
                # Expected to fail with fake API key, but architecture is correct
                auth_error = "authentication" in response.error_message.lower() or "api key" in response.error_message.lower()
                if auth_error:
                    print_test("Architecture correct (fails at auth as expected)", True, "LLM call structure is valid")
                    return has_correct_structure and template_used and formatting_worked
                else:
                    print_test("Unexpected error", False, response.error_message)
                    return False
                    
        except Exception as e:
            print_test("process_request call failed", False, f"Error: {str(e)}")
            return False
            
    except Exception as e:
        print_test("DoD 3 test failed", False, f"Error: {str(e)}")
        return False

def test_additional_templates():
    """Test additional templates are working."""
    print_section("Additional Templates Test")
    
    try:
        formatter = create_prompt_formatter()
        templates = formatter.list_templates()
        template_ids = [t.template_id for t in templates]
        
        print_test(f"Total templates loaded: {len(templates)}", len(templates) >= 5, 
                  f"Templates: {template_ids}")
        
        # Test a few additional templates
        additional_tests = [
            {
                "template_id": "analyze_function",
                "context_data": {
                    "function_name": "quicksort",
                    "function_code": "def quicksort(arr): return sorted(arr)",
                    "language": "python"
                }
            },
            {
                "template_id": "find_issues", 
                "context_data": {
                    "code_content": "def divide(a, b): return a / b",
                    "language": "python"
                }
            }
        ]
        
        success_count = 0
        for test_case in additional_tests:
            template_id = test_case["template_id"]
            if template_id in template_ids:
                result = formatter.format_prompt(template_id, test_case["context_data"])
                if result.success:
                    success_count += 1
                    print_test(f"Template '{template_id}' works", True)
                else:
                    print_test(f"Template '{template_id}' failed", False, result.error.message if result.error else "Unknown error")
            else:
                print_test(f"Template '{template_id}' not found", False)
        
        return success_count >= 2
        
    except Exception as e:
        print_test("Additional templates test failed", False, f"Error: {str(e)}")
        return False

def main():
    """Main test execution."""
    print_section("Task 3.4 DoD Compliance Verification")
    print("Testing implementation meets all Definition of Done requirements")
    print("without requiring real OpenAI API key")
    
    # Run DoD tests
    tests = [
        ("DoD 1: Prompt Template Design", test_dod_1_template_design),
        ("DoD 2: PromptFormatterModule", test_dod_2_prompt_formatter),
        ("DoD 3: LLMGatewayModule", test_dod_3_llm_gateway),
        ("Additional Templates", test_additional_templates)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_section("DoD Compliance Results")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} DoD requirements met ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 Task 3.4 DoD FULLY COMPLIANT!")
        print("✅ DoD 1: Prompt Template 'Giải thích code' với {code_snippet}")
        print("✅ DoD 2: PromptFormatterModule.format_prompt(template_id, context_data)")
        print("✅ DoD 3: LLMGatewayModule.process_request(prompt_id, context_data)")
        print("🚀 Ready for production with real OpenAI API key!")
    else:
        print(f"\n⚠️ {total-passed} DoD requirements not met. Task needs more work.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 