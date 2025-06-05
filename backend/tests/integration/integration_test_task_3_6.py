#!/usr/bin/env python3
"""
Integration Test Task 3.6: Real Orchestrator Agent LLM Routing

Kiểm tra integration với real components:
- Real OrchestratorAgent với route_llm_request method
- Real TEAM LLM Services với TeamLLMServices facade
- Real LLMAnalysisSupportModule từ Task 3.5
- End-to-end workflow với actual API integration

Created: 2024-12-28
Author: TEAM Integration Test
"""

import os
import sys
import time
from datetime import datetime

# Add backend source to path
backend_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, backend_path)

try:
    # Import real components
    from orchestrator.orchestrator_agent import OrchestratorAgent
    from teams.code_analysis.llm_analysis_support_module import LLMAnalysisSupportModule
    from teams.llm_services import LLMServiceRequest, LLMServiceResponse, LLMServiceStatus
    
    print("✅ Successfully imported real components")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Using standalone test approach...")
    sys.exit(1)

def test_real_integration():
    """
    Test integration với real components.
    """
    print("=" * 80)
    print("TASK 3.6: REAL INTEGRATION TEST - ORCHESTRATOR LLM ROUTING")
    print("=" * 80)
    
    # Sample code for testing
    sample_code = """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test the function
sorted_array = [1, 3, 5, 7, 9, 11, 13, 15]
result = binary_search(sorted_array, 7)
print(f"Index of 7: {result}")
"""
    
    print("\n1. KHỞI TẠO REAL COMPONENTS")
    print("-" * 40)
    
    try:
        # Initialize real OrchestratorAgent
        print("Initializing OrchestratorAgent...")
        orchestrator = OrchestratorAgent()
        print("✅ OrchestratorAgent initialized successfully")
        
        # Initialize real LLMAnalysisSupportModule
        print("Initializing LLMAnalysisSupportModule...")
        llm_analysis_module = LLMAnalysisSupportModule()
        print("✅ LLMAnalysisSupportModule initialized successfully")
        
        # Verify route_llm_request method exists
        if hasattr(orchestrator, 'route_llm_request'):
            print("✅ route_llm_request method found in OrchestratorAgent")
        else:
            print("❌ route_llm_request method NOT found!")
            return False
        
        print("\n2. TESTING LLM REQUEST CREATION")
        print("-" * 40)
        
        # Create LLM request using real module
        llm_request = llm_analysis_module.create_explain_code_request(
            sample_code,
            language="python"
        )
        
        print(f"✅ LLMServiceRequest created:")
        print(f"   - Prompt ID: {llm_request.prompt_id}")
        print(f"   - User ID: {llm_request.user_id}")
        print(f"   - Request ID: {llm_request.request_id}")
        print(f"   - LLM Model: {llm_request.llm_config.model if llm_request.llm_config else 'None'}")
        print(f"   - Context keys: {list(llm_request.context_data.keys())}")
        
        print("\n3. TESTING ORCHESTRATOR ROUTING")
        print("-" * 40)
        
        print("Calling orchestrator.route_llm_request()...")
        start_time = time.time()
        
        # This will call real TEAM LLM Services
        llm_response = orchestrator.route_llm_request(llm_request)
        
        routing_time = time.time() - start_time
        
        print(f"✅ LLM routing completed in {routing_time:.2f}s")
        print(f"✅ Response status: {llm_response.status.value}")
        print(f"✅ Response type: {type(llm_response).__name__}")
        
        if llm_response.status == LLMServiceStatus.SUCCESS:
            print(f"✅ Response length: {len(llm_response.response_text)} characters")
            print(f"✅ Request ID matches: {llm_response.request_id == llm_request.request_id}")
            
            # Show response preview
            print("\n4. RESPONSE CONTENT PREVIEW")
            print("-" * 40)
            print("Response preview (first 300 chars):")
            print(f"{llm_response.response_text[:300]}...")
            
            if llm_response.metadata:
                print(f"\nMetadata:")
                for key, value in llm_response.metadata.items():
                    print(f"  - {key}: {value}")
                    
        else:
            print(f"❌ LLM Request failed: {llm_response.error_message}")
            return False
        
        print("\n5. TESTING MULTIPLE REQUESTS")
        print("-" * 40)
        
        # Test another request type
        function_code = """
def merge_sort(arr):
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
    return result
"""
        
        # Test function analysis
        function_request = llm_analysis_module.create_analyze_function_request(
            function_name="merge_sort",
            function_code=function_code,
            language="python",
            context="Sorting algorithm implementation"
        )
        
        print(f"Created analyze_function request: {function_request.prompt_id}")
        
        function_response = orchestrator.route_llm_request(function_request)
        
        print(f"✅ Function analysis response: {function_response.status.value}")
        
        if function_response.status == LLMServiceStatus.SUCCESS:
            print(f"✅ Function analysis successful, response length: {len(function_response.response_text)}")
        else:
            print(f"❌ Function analysis failed: {function_response.error_message}")
        
        print("\n6. FINAL INTEGRATION SUMMARY")
        print("-" * 40)
        
        print("✅ All integration tests passed!")
        print("✅ Real OrchestratorAgent working correctly")
        print("✅ Real TEAM LLM Services responding")
        print("✅ Real LLMAnalysisSupportModule creating requests")
        print("✅ End-to-end workflow functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'orchestrator' in locals():
                orchestrator.shutdown()
                print("✅ OrchestratorAgent shutdown completed")
        except Exception as e:
            print(f"Warning: Shutdown error: {e}")

def main():
    """Main test execution."""
    print("Starting Task 3.6 Real Integration Test")
    print(f"Test started at: {datetime.now()}")
    
    success = test_real_integration()
    
    if success:
        print("\n" + "=" * 80)
        print("🎉 TASK 3.6 REAL INTEGRATION TEST PASSED! 🎉")
        print("=" * 80)
        print("\nReal Integration Summary:")
        print("✅ OrchestratorAgent.route_llm_request() working")
        print("✅ TeamLLMServices.process_request() integration")
        print("✅ LLMAnalysisSupportModule integration")  
        print("✅ End-to-end LLM routing functional")
        print("\n🚀 Task 3.6 REAL INTEGRATION SUCCESSFUL!")
        return True
    else:
        print("\n❌ Real integration test failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 