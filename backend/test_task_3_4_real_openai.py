#!/usr/bin/env python3
"""
Real OpenAI Test Script cho Task 3.4

Test PromptFormatterModule và LLMGatewayModule với:
- Load templates từ markdown files  
- OpenAI API thật với gpt-3.5-turbo
- Code examples thật
- DoD compliance verification
"""

import sys
import os
import time
import logging
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.teams.llm_services import (
    # Task 3.4 refactored modules
    TemplateLoader, PromptFormatterModule, LLMGatewayModule,
    create_template_loader, create_prompt_formatter, create_llm_gateway,
    
    # Task 3.3 LLM infrastructure
    LLMConfig, LLMProviderType, get_default_openai_config,
    check_dependencies
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_task_3_4_real_openai.log'),
        logging.StreamHandler()
    ]
)
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

def check_openai_api_key() -> bool:
    """Check if OpenAI API key is available."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    if api_key == 'your_openai_api_key_here':
        print("❌ Please replace the placeholder API key with your real OpenAI API key")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    return True

def test_1_template_loader_from_markdown():
    """Test 1: TemplateLoader loads templates từ markdown files."""
    print_section("Test 1: Template Loader từ Markdown Files")
    
    try:
        # Test template loader
        loader = create_template_loader()
        print_test("TemplateLoader created", True)
        
        # Check template directory
        templates_dir = loader.templates_directory
        dir_exists = templates_dir.exists()
        print_test(f"Templates directory exists: {templates_dir}", dir_exists)
        
        if dir_exists:
            # List template files
            files = loader.list_template_files()
            print_test(f"Found {len(files)} template files", len(files) > 0, f"Files: {files}")
            
            # Load all templates
            result = loader.load_all_templates()
            print_test("Load all templates", result.success, 
                      f"Loaded: {result.successful_files}/{result.total_files}")
            
            if result.templates_loaded:
                for template in result.templates_loaded:
                    print(f"    📄 {template.template_id}: {template.name}")
                    print(f"        Variables: {template.required_variables}")
            
            return result.success and len(result.templates_loaded) >= 5
        else:
            print_test("Template directory missing", False, "No markdown templates to test")
            return False
            
    except Exception as e:
        print_test("Template loader test", False, f"Error: {str(e)}")
        return False

def test_2_prompt_formatter_with_markdown():
    """Test 2: PromptFormatterModule sử dụng markdown templates."""
    print_section("Test 2: PromptFormatter với Markdown Templates")
    
    try:
        # Create formatter that loads from markdown
        formatter = create_prompt_formatter()
        print_test("PromptFormatterModule created", True)
        
        # Get loaded templates  
        templates = formatter.list_templates()
        template_ids = [t.template_id for t in templates]
        print_test(f"Templates loaded: {len(templates)}", len(templates) > 0, 
                  f"IDs: {template_ids}")
        
        # Test explain_code template (DoD requirement)
        if "explain_code" in template_ids:
            context_data = {
                "code_snippet": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
                "language": "python"
            }
            
            result = formatter.format_prompt("explain_code", context_data)
            print_test("Format explain_code template", result.success,
                      f"Prompt length: {len(result.formatted_prompt) if result.formatted_prompt else 0}")
            
            if result.success and result.formatted_prompt:
                print("📝 Generated prompt preview:")
                print(result.formatted_prompt[:200] + "..." if len(result.formatted_prompt) > 200 else result.formatted_prompt)
            
            return result.success
        else:
            print_test("explain_code template missing", False)
            return False
            
    except Exception as e:
        print_test("PromptFormatter test", False, f"Error: {str(e)}")
        return False

def test_3_llm_gateway_with_openai():
    """Test 3: LLMGatewayModule với OpenAI API thật."""
    print_section("Test 3: LLM Gateway với OpenAI API")
    
    # Check API key first
    if not check_openai_api_key():
        return False
    
    try:
        # Create gateway with gpt-3.5-turbo
        gateway = create_llm_gateway()
        print_test("LLMGatewayModule created", True)
        
        # Configure for gpt-3.5-turbo
        config = get_default_openai_config()
        config.api_key = os.getenv('OPENAI_API_KEY')  # Set API key from environment
        print_test(f"Using model: {config.model}", config.model == "gpt-3.5-turbo")
        
        # Test with real code example
        code_example = """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result"""
        
        context_data = {
            "code_snippet": code_example,
            "language": "python"
        }
        
        print("🚀 Calling OpenAI API...")
        start_time = time.time()
        
        response = gateway.process_request("explain_code", context_data, config)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print_test("OpenAI API call completed", response.success,
                  f"Response time: {response_time:.2f}s")
        
        if response.success:
            print("🤖 OpenAI Response:")
            print("-" * 50)
            print(response.response_text[:500] + "..." if len(response.response_text) > 500 else response.response_text)
            print("-" * 50)
            
            # Check if response is in Vietnamese
            vietnamese_keywords = ["giải thích", "chức năng", "thuật toán", "phương thức"]
            has_vietnamese = any(keyword in response.response_text.lower() for keyword in vietnamese_keywords)
            print_test("Response contains Vietnamese", has_vietnamese)
            
            return True
        else:
            print_test("OpenAI API call failed", False, response.error_message)
            return False
            
    except Exception as e:
        print_test("LLM Gateway test", False, f"Error: {str(e)}")
        return False

def test_4_dod_compliance_real():
    """Test 4: DoD compliance với OpenAI thật."""
    print_section("Test 4: DoD Compliance với OpenAI")
    
    if not check_openai_api_key():
        return False
    
    try:
        # DoD 1: Template "Giải thích code" với {code_snippet}
        formatter = create_prompt_formatter()
        template = formatter.get_template("explain_code")
        
        dod1 = (template is not None and 
                "{code_snippet}" in template.template_text and
                "code_snippet" in template.required_variables)
        print_test("DoD 1: Template 'explain_code' với {code_snippet}", dod1)
        
        # DoD 2: PromptFormatterModule.format_prompt(template_id, context_data)
        context_data = {"code_snippet": "def hello_world():\n    print('Hello, World!')", "language": "python"}
        format_result = formatter.format_prompt("explain_code", context_data)
        
        dod2 = (format_result.success and 
                format_result.formatted_prompt is not None and
                "hello_world" in format_result.formatted_prompt)
        print_test("DoD 2: PromptFormatterModule.format_prompt() works", dod2)
        
        # DoD 3: LLMGatewayModule.process_request() calls formatter và OpenAI
        gateway = create_llm_gateway()
        config = get_default_openai_config()
        config.api_key = os.getenv('OPENAI_API_KEY')  # Set API key from environment
        
        gateway_response = gateway.process_request("explain_code", context_data, config)
        
        dod3 = (gateway_response.template_used == "explain_code" and
                gateway_response.success and
                gateway_response.response_text is not None)
        print_test("DoD 3: LLMGatewayModule.process_request() full chain", dod3)
        
        if dod3:
            print("📋 Full DoD Chain verified:")
            print(f"    Template used: {gateway_response.template_used}")
            print(f"    Processing time: {gateway_response.processing_time:.2f}s")
            print(f"    Response length: {len(gateway_response.response_text)} chars")
        
        return dod1 and dod2 and dod3
        
    except Exception as e:
        print_test("DoD compliance test", False, f"Error: {str(e)}")
        return False

def test_5_multiple_templates_real():
    """Test 5: Multiple templates với OpenAI thật."""
    print_section("Test 5: Multiple Templates với OpenAI")
    
    if not check_openai_api_key():
        return False
    
    try:
        gateway = create_llm_gateway()
        config = get_default_openai_config()
        config.api_key = os.getenv('OPENAI_API_KEY')  # Set API key from environment
        
        # Test cases for different templates
        test_cases = [
            {
                "template_id": "analyze_function",
                "context_data": {
                    "function_name": "binary_search",
                    "function_code": """def binary_search(arr, target):
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
                    "language": "python"
                },
                "description": "Function analysis"
            },
            {
                "template_id": "find_issues",
                "context_data": {
                    "code_content": """def divide_numbers(a, b):
    return a / b  # Potential division by zero

def get_user_age(user_data):
    return user_data['age']  # No error handling for missing key""",
                    "language": "python"
                },
                "description": "Issue detection"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            template_id = test_case["template_id"]
            context_data = test_case["context_data"]
            description = test_case["description"]
            
            print(f"\n📝 Test Case {i}: {description} ({template_id})")
            
            try:
                response = gateway.process_request(template_id, context_data, config)
                
                if response.success:
                    print_test(f"Template {template_id} successful", True,
                              f"Response: {len(response.response_text)} chars")
                    success_count += 1
                    
                    # Show brief response
                    print(f"    Response preview: {response.response_text[:100]}...")
                else:
                    print_test(f"Template {template_id} failed", False, response.error_message)
                    
            except Exception as e:
                print_test(f"Template {template_id} error", False, str(e))
        
        overall_success = success_count == len(test_cases)
        print_test(f"All templates successful", overall_success, 
                  f"{success_count}/{len(test_cases)} templates worked")
        
        return overall_success
        
    except Exception as e:
        print_test("Multiple templates test", False, f"Error: {str(e)}")
        return False

def main():
    """Main test execution."""
    print_section("Task 3.4 Real OpenAI Integration Test")
    print("Testing refactored PromptFormatterModule và LLMGatewayModule")
    print("với markdown templates và OpenAI gpt-3.5-turbo")
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("❌ Dependencies check failed")
        return
    
    # Run tests
    tests = [
        ("Template Loader từ Markdown", test_1_template_loader_from_markdown),
        ("PromptFormatter với Markdown", test_2_prompt_formatter_with_markdown), 
        ("LLM Gateway với OpenAI", test_3_llm_gateway_with_openai),
        ("DoD Compliance Real", test_4_dod_compliance_real),
        ("Multiple Templates Real", test_5_multiple_templates_real)
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
    print_section("Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Task 3.4 refactoring successful!")
        print("✅ Templates loading từ markdown files")
        print("✅ OpenAI integration với gpt-3.5-turbo") 
        print("✅ DoD requirements met")
        print("✅ Real code analysis working")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main() 