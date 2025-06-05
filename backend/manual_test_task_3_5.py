#!/usr/bin/env python3
"""
Manual Test for Task 3.5: LLMAnalysisSupportModule

Test trực tiếp LLMAnalysisSupportModule để verify DoD compliance,
hoàn toàn isolated không import từ __init__.py.
"""

import sys
import os

# Add backend to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import trực tiếp từ modules
try:
    from src.teams.llm_services.models import (
        LLMServiceRequest, LLMServiceResponse, LLMConfig,
        LLMProviderType, LLMServiceStatus
    )
    print("✅ LLM Services models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LLM Services models: {e}")
    sys.exit(1)

try:
    from src.teams.code_analysis.llm_analysis_support_module_minimal import (
        LLMAnalysisSupportModule, 
        CodeAnalysisContext
    )
    print("✅ LLMAnalysisSupportModule (minimal) imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LLMAnalysisSupportModule: {e}")
    sys.exit(1)


def test_task_3_5_dod_compliance():
    """Test Task 3.5 DoD compliance manually."""
    print("\n" + "=" * 70)
    print("  TASK 3.5 DoD COMPLIANCE TEST")
    print("=" * 70)
    
    test_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
    
    print(f"Test Code ({len(test_code)} chars):")
    print(f"```python\n{test_code}\n```\n")
    
    # Test 1: LLMServiceRequest structure exists
    print("📋 DoD Test 1: LLMServiceRequest structure exists")
    try:
        module = LLMAnalysisSupportModule()
        request = module.create_explain_code_request(test_code)
        
        # Check structure
        assert hasattr(request, 'prompt_id'), "Missing prompt_id field"
        assert hasattr(request, 'context_data'), "Missing context_data field"
        assert hasattr(request, 'llm_config'), "Missing llm_config field"
        assert hasattr(request, 'prompt_text'), "Missing prompt_text field"
        
        print("   ✅ LLMServiceRequest has all required fields")
        print(f"   📝 Fields: prompt_id={request.prompt_id}, context_data keys={list(request.context_data.keys())}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: LLMServiceResponse structure exists  
    print("\n📋 DoD Test 2: LLMServiceResponse structure exists")
    try:
        response = LLMServiceResponse(
            response_text="Test response",
            status=LLMServiceStatus.SUCCESS
        )
        
        # Check structure
        assert hasattr(response, 'response_text'), "Missing response_text field"
        assert hasattr(response, 'status'), "Missing status field"
        
        print("   ✅ LLMServiceResponse has all required fields")
        print(f"   📝 Fields: response_text='{response.response_text}', status={response.status}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Module có function nhận code string
    print("\n📋 DoD Test 3: Module accepts code string")
    try:
        module = LLMAnalysisSupportModule()
        assert hasattr(module, 'create_explain_code_request'), "Missing create_explain_code_request method"
        
        request = module.create_explain_code_request(test_code)
        assert request is not None, "Method returned None"
        
        print("   ✅ Module accepts code string and returns result")
        print(f"   📝 Method: create_explain_code_request exists and works")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Function tạo LLMServiceRequest với prompt_id="explain_code"
    print("\n📋 DoD Test 4: Creates LLMServiceRequest with prompt_id='explain_code'")
    try:
        module = LLMAnalysisSupportModule()
        request = module.create_explain_code_request(test_code)
        
        assert isinstance(request, LLMServiceRequest), f"Wrong return type: {type(request)}"
        assert request.prompt_id == "explain_code", f"Wrong prompt_id: {request.prompt_id}"
        assert "code_snippet" in request.context_data, "Missing code_snippet in context_data"
        assert request.context_data["code_snippet"] == test_code, "Wrong code_snippet value"
        
        print("   ✅ Creates correct LLMServiceRequest")
        print(f"   📝 prompt_id='{request.prompt_id}', code_snippet length={len(request.context_data['code_snippet'])}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 5: Function sử dụng cấu hình LLM mặc định
    print("\n📋 DoD Test 5: Uses default LLM configuration")
    try:
        module = LLMAnalysisSupportModule()
        request = module.create_explain_code_request(test_code)
        
        assert isinstance(request.llm_config, LLMConfig), f"Wrong llm_config type: {type(request.llm_config)}"
        assert request.llm_config.provider == LLMProviderType.OPENAI, f"Wrong provider: {request.llm_config.provider}"
        assert request.llm_config.model == "gpt-3.5-turbo", f"Wrong model: {request.llm_config.model}"
        
        print("   ✅ Uses correct default LLM configuration")
        print(f"   📝 Provider: {request.llm_config.provider.value}, Model: {request.llm_config.model}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 6: Function trả về LLMServiceRequest
    print("\n📋 DoD Test 6: Returns LLMServiceRequest object")
    try:
        module = LLMAnalysisSupportModule()
        request = module.create_explain_code_request(test_code)
        
        assert isinstance(request, LLMServiceRequest), f"Wrong return type: {type(request)}"
        assert request is not None, "Returned None"
        
        print("   ✅ Returns correct LLMServiceRequest object")
        print(f"   📝 Type: {type(request).__name__}, Not None: {request is not None}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    return True


def test_additional_functionality():
    """Test additional functionality beyond DoD."""
    print("\n" + "=" * 70)
    print("  ADDITIONAL FUNCTIONALITY TEST")
    print("=" * 70)
    
    module = LLMAnalysisSupportModule()
    
    # Test multiple analysis types
    print("🌟 Testing multiple analysis types...")
    
    test_code = "def add(a, b): return a + b"
    
    # Test analyze_function
    try:
        request = module.create_analyze_function_request(
            function_name="add",
            function_code=test_code
        )
        assert request.prompt_id == "analyze_function"
        print("   ✅ analyze_function request works")
    except Exception as e:
        print(f"   ❌ analyze_function failed: {e}")
    
    # Test find_issues
    try:
        request = module.create_find_issues_request(
            code_content=test_code,
            file_path="test.py"
        )
        assert request.prompt_id == "find_issues"
        print("   ✅ find_issues request works")
    except Exception as e:
        print(f"   ❌ find_issues failed: {e}")
    
    # Test CodeAnalysisContext
    try:
        context = module.create_context_from_code(
            code_snippet=test_code,
            analysis_type="explain_code"
        )
        assert isinstance(context, CodeAnalysisContext)
        assert context.code_snippet == test_code
        print("   ✅ CodeAnalysisContext creation works")
    except Exception as e:
        print(f"   ❌ CodeAnalysisContext failed: {e}")


def demonstrate_usage():
    """Demonstrate typical usage of LLMAnalysisSupportModule."""
    print("\n" + "=" * 70)
    print("  USAGE DEMONSTRATION")
    print("=" * 70)
    
    # Sample code để analyze
    sample_code = """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)"""
    
    print("📝 Sample Code for Analysis:")
    print(f"```python\n{sample_code}\n```")
    
    module = LLMAnalysisSupportModule()
    
    # Create explain_code request
    print("\n🔍 Creating explain_code request...")
    request = module.create_explain_code_request(sample_code, "python")
    
    print(f"📋 Request Details:")
    print(f"   - Type: {type(request).__name__}")
    print(f"   - Prompt ID: {request.prompt_id}")
    print(f"   - Context Data Keys: {list(request.context_data.keys())}")
    print(f"   - Language: {request.context_data.get('language', 'N/A')}")
    print(f"   - LLM Provider: {request.llm_config.provider.value}")
    print(f"   - LLM Model: {request.llm_config.model}")
    print(f"   - User ID: {request.user_id}")
    print(f"   - Request ID: {request.request_id}")
    
    print("\n✨ This request is ready to send to TEAM LLM Services!")


def main():
    """Main test runner."""
    print("🚀 Testing Task 3.5: LLMAnalysisSupportModule")
    print("🎯 Goal: Verify DoD compliance for Code Analysis LLM bridge")
    
    # Run DoD compliance tests
    success = test_task_3_5_dod_compliance()
    
    if success:
        print("\n🎉 ALL DoD REQUIREMENTS PASSED!")
        print("\n✅ Task 3.5 Summary:")
        print("  1. ✅ LLMServiceRequest/Response structures exist")
        print("  2. ✅ LLMAnalysisSupportModule implemented")
        print("  3. ✅ Module accepts code string")
        print("  4. ✅ Creates explain_code requests correctly")
        print("  5. ✅ Uses default LLM configuration")
        print("  6. ✅ Returns LLMServiceRequest objects")
        
        # Test additional functionality
        test_additional_functionality()
        
        # Demonstrate usage
        demonstrate_usage()
        
        print("\n🚀 Task 3.5 COMPLETED SUCCESSFULLY!")
        print("🔗 Ready for Task 3.6: Orchestrator Agent LLM routing")
        
    else:
        print("\n❌ DoD requirements not fully met")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 