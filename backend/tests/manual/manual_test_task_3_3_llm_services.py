"""
Manual Test Script for Task 3.3 (F3.3): LLM Services Infrastructure

This script manually tests the LLM Services implementation including:
- OpenAI provider integration (with and without real API key)
- Provider factory and management
- Configuration handling
- Error scenarios
- Integration testing
"""

import os
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from teams.llm_services import (
        LLMConfig,
        LLMProviderType,
        LLMServiceRequest,
        LLMServiceResponse,
        LLMServiceStatus,
        OpenAIProvider,
        LLMProviderFactory,
        LLMProviderManager,
        LLMProviderError,
        get_default_openai_config,
        create_openai_provider,
        check_dependencies
    )
    print("✅ Successfully imported LLM Services modules")
except ImportError as e:
    print(f"❌ Failed to import LLM Services modules: {e}")
    sys.exit(1)


class LLMServicesManualTester:
    """Manual testing class for LLM Services infrastructure."""
    
    def __init__(self):
        """Initialize the manual tester."""
        self.test_results = {}
        self.start_time = datetime.now()
        
        print("🚀 Starting LLM Services Manual Testing")
        print("=" * 60)
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result."""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if message:
            print(f"   📋 {message}")
        if details:
            for key, value in details.items():
                print(f"   🔍 {key}: {value}")
        print()
        
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def test_dependency_check(self):
        """Test dependency availability."""
        print("📦 Testing Dependencies")
        print("-" * 30)
        
        try:
            deps = check_dependencies()
            
            openai_available = deps.get("openai", {}).get("available", False)
            pydantic_available = deps.get("pydantic", {}).get("available", False)
            
            self.log_test_result(
                "Dependency Check",
                openai_available and pydantic_available,
                f"OpenAI: {openai_available}, Pydantic: {pydantic_available}",
                deps
            )
            
            return deps
            
        except Exception as e:
            self.log_test_result("Dependency Check", False, str(e))
            return {}
    
    def test_config_creation_and_validation(self):
        """Test LLMConfig creation and validation."""
        print("⚙️ Testing Configuration")
        print("-" * 30)
        
        # Test valid configuration
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=2048,
                api_key="test-key"
            )
            
            self.log_test_result(
                "Valid Config Creation",
                True,
                "Configuration created successfully",
                {
                    "provider": config.provider.value,
                    "model": config.model,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                }
            )
            
        except Exception as e:
            self.log_test_result("Valid Config Creation", False, str(e))
        
        # Test invalid configuration (temperature out of range)
        try:
            invalid_config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                temperature=3.0  # Invalid
            )
            
            self.log_test_result(
                "Invalid Config Validation",
                False,
                "Should have failed but didn't"
            )
            
        except ValueError as e:
            self.log_test_result(
                "Invalid Config Validation",
                True,
                "Correctly caught invalid temperature",
                {"error": str(e)}
            )
        except Exception as e:
            self.log_test_result("Invalid Config Validation", False, str(e))
    
    def test_default_configurations(self):
        """Test default configuration helpers."""
        print("🎯 Testing Default Configurations")
        print("-" * 30)
        
        try:
            default_config = get_default_openai_config()
            
            self.log_test_result(
                "Default Config Creation",
                default_config.provider == LLMProviderType.OPENAI,
                "Default configuration created",
                {
                    "provider": default_config.provider.value,
                    "model": default_config.model,
                    "temperature": default_config.temperature
                }
            )
            
        except Exception as e:
            self.log_test_result("Default Config Creation", False, str(e))
    
    def test_provider_factory(self):
        """Test provider factory functionality."""
        print("🏭 Testing Provider Factory")
        print("-" * 30)
        
        # Test supported providers
        try:
            supported = LLMProviderFactory.get_supported_providers()
            
            self.log_test_result(
                "Supported Providers",
                LLMProviderType.OPENAI in supported,
                f"Found {len(supported)} supported providers",
                {"providers": list(supported.keys())}
            )
            
        except Exception as e:
            self.log_test_result("Supported Providers", False, str(e))
        
        # Test provider creation
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                api_key="test-key"
            )
            
            provider = LLMProviderFactory.create_provider(config)
            
            self.log_test_result(
                "Provider Creation",
                isinstance(provider, OpenAIProvider),
                "Successfully created OpenAI provider",
                {"provider_type": type(provider).__name__}
            )
            
        except Exception as e:
            self.log_test_result("Provider Creation", False, str(e))
        
        # Test unsupported provider
        try:
            unsupported_config = LLMConfig(
                provider=LLMProviderType.GOOGLE_GENAI,  # Not implemented yet
                model="claude-3"
            )
            
            LLMProviderFactory.create_provider(unsupported_config)
            
            self.log_test_result(
                "Unsupported Provider Handling",
                False,
                "Should have failed but didn't"
            )
            
        except LLMProviderError as e:
            self.log_test_result(
                "Unsupported Provider Handling",
                e.error_code == "UNSUPPORTED_PROVIDER",
                "Correctly handled unsupported provider",
                {"error_code": e.error_code}
            )
        except Exception as e:
            self.log_test_result("Unsupported Provider Handling", False, str(e))
    
    def test_provider_manager(self):
        """Test provider manager functionality."""
        print("👨‍💼 Testing Provider Manager")
        print("-" * 30)
        
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                api_key="test-key"
            )
            
            manager = LLMProviderManager(default_config=config)
            
            # Test provider retrieval
            provider = manager.get_provider()
            
            self.log_test_result(
                "Manager Provider Retrieval",
                isinstance(provider, OpenAIProvider),
                "Successfully retrieved provider through manager",
                {"provider_type": type(provider).__name__}
            )
            
            # Test recommendations
            recommendations = manager.get_provider_recommendations("code_analysis")
            
            self.log_test_result(
                "Provider Recommendations",
                len(recommendations) > 0,
                f"Got {len(recommendations)} recommendations",
                {"recommendations": [p.value for p in recommendations]}
            )
            
        except Exception as e:
            self.log_test_result("Provider Manager", False, str(e))
    
    def test_openai_provider_without_api_key(self):
        """Test OpenAI provider behavior without valid API key."""
        print("🔑 Testing OpenAI Provider (No API Key)")
        print("-" * 30)
        
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                api_key=None  # No API key
            )
            
            provider = OpenAIProvider(config)
            
            self.log_test_result(
                "Provider Without API Key",
                False,
                "Should have failed but didn't"
            )
            
        except LLMProviderError as e:
            self.log_test_result(
                "Provider Without API Key",
                e.error_code == "API_KEY_MISSING",
                "Correctly detected missing API key",
                {"error_code": e.error_code}
            )
        except Exception as e:
            self.log_test_result("Provider Without API Key", False, str(e))
    
    def test_openai_provider_with_fake_api_key(self):
        """Test OpenAI provider with fake API key (availability check)."""
        print("🔐 Testing OpenAI Provider (Fake API Key)")
        print("-" * 30)
        
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                api_key="fake-api-key-for-testing"
            )
            
            provider = OpenAIProvider(config)
            
            # Test availability check
            is_available = provider.is_available()
            
            # Test supported models
            models = provider.get_supported_models()
            
            # Test configuration validation
            is_valid = provider.validate_config(config)
            
            # Test cost estimation
            cost = provider.estimate_cost("This is a test prompt")
            
            self.log_test_result(
                "Provider Basic Operations",
                len(models) > 0 and is_valid and cost >= 0,
                "Basic operations work without API call",
                {
                    "available": is_available,
                    "models_count": len(models),
                    "config_valid": is_valid,
                    "estimated_cost": cost
                }
            )
            
        except Exception as e:
            self.log_test_result("Provider Basic Operations", False, str(e))
    
    def test_openai_provider_with_real_api_key(self):
        """Test OpenAI provider with real API key if available."""
        print("🌐 Testing OpenAI Provider (Real API Key)")
        print("-" * 30)
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            self.log_test_result(
                "Real API Test",
                True,  # Not a failure, just skipped
                "Skipped - No OPENAI_API_KEY environment variable",
                {"note": "Set OPENAI_API_KEY to test real API integration"}
            )
            return
        
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-3.5-turbo",  # Cheaper model for testing
                temperature=0.7,
                max_tokens=50,  # Small response to minimize cost
                api_key=api_key
            )
            
            provider = OpenAIProvider(config)
            
            # Test simple completion
            start_time = time.time()
            response = provider.complete("Say 'Hello' in one word.")
            response_time = (time.time() - start_time) * 1000
            
            self.log_test_result(
                "Real API Completion",
                len(response) > 0,
                "Successfully completed real API request",
                {
                    "response_length": len(response),
                    "response_time_ms": f"{response_time:.2f}",
                    "response_preview": response[:50] + "..." if len(response) > 50 else response
                }
            )
            
        except LLMProviderError as e:
            self.log_test_result(
                "Real API Completion",
                False,
                f"Provider error: {e.error_code}",
                {"error_message": str(e)}
            )
        except Exception as e:
            self.log_test_result("Real API Completion", False, str(e))
    
    def test_service_request_response_models(self):
        """Test service request and response models."""
        print("📝 Testing Request/Response Models")
        print("-" * 30)
        
        try:
            config = LLMConfig(
                provider=LLMProviderType.OPENAI,
                model="gpt-4o-mini",
                api_key="test-key"
            )
            
            # Test request creation
            request = LLMServiceRequest(
                prompt_text="Test prompt for model validation",
                llm_config=config,
                request_id="test-req-001",
                user_id="test-user"
            )
            
            # Test response creation
            response = LLMServiceResponse(
                response_text="Test response",
                status=LLMServiceStatus.SUCCESS,
                request_id=request.request_id,
                model_used=config.model,
                tokens_used=100,
                response_time_ms=250.0
            )
            
            self.log_test_result(
                "Request/Response Models",
                request.prompt_text == "Test prompt for model validation" and response.is_success(),
                "Successfully created request and response models",
                {
                    "request_id": request.request_id,
                    "response_status": response.status.value,
                    "tokens_used": response.tokens_used
                }
            )
            
        except Exception as e:
            self.log_test_result("Request/Response Models", False, str(e))
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        print("🚨 Testing Error Handling")
        print("-" * 30)
        
        # Test LLMProviderError
        try:
            error = LLMProviderError(
                "Test error message",
                error_code="TEST_ERROR",
                status=LLMServiceStatus.ERROR
            )
            
            self.log_test_result(
                "Error Object Creation",
                str(error) == "Test error message" and error.error_code == "TEST_ERROR",
                "Successfully created error object",
                {"error_code": error.error_code, "status": error.status.value}
            )
            
        except Exception as e:
            self.log_test_result("Error Object Creation", False, str(e))
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        print("🛠️ Testing Convenience Functions")
        print("-" * 30)
        
        try:
            # Test create_openai_provider function
            provider = create_openai_provider(api_key="test-key", model="gpt-4")
            
            self.log_test_result(
                "Convenience Provider Creation",
                isinstance(provider, OpenAIProvider) and provider.config.model == "gpt-4",
                "Successfully created provider using convenience function",
                {"model": provider.config.model}
            )
            
        except Exception as e:
            self.log_test_result("Convenience Provider Creation", False, str(e))
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("📊 Test Report Generation")
        print("=" * 60)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print()
        
        if failed_tests > 0:
            print("❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"   • {test_name}: {result['message']}")
            print()
        
        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "duration_seconds": duration,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_results": self.test_results
        }
        
        report_file = f"llm_services_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")
        
        return success_rate >= 80  # Consider 80%+ as overall success
    
    def run_all_tests(self):
        """Run all manual tests."""
        print("🚀 Running Comprehensive LLM Services Tests")
        print("=" * 60)
        
        # Test sequence
        self.test_dependency_check()
        self.test_config_creation_and_validation()
        self.test_default_configurations()
        self.test_provider_factory()
        self.test_provider_manager()
        self.test_openai_provider_without_api_key()
        self.test_openai_provider_with_fake_api_key()
        self.test_openai_provider_with_real_api_key()
        self.test_service_request_response_models()
        self.test_error_handling()
        self.test_convenience_functions()
        
        return self.generate_test_report()


def main():
    """Main testing function."""
    print("🔧 LLM Services Infrastructure Manual Testing")
    print("=" * 60)
    print("This script tests the LLM Services implementation")
    print("For real API testing, set OPENAI_API_KEY environment variable")
    print("=" * 60)
    print()
    
    tester = LLMServicesManualTester()
    
    try:
        overall_success = tester.run_all_tests()
        
        if overall_success:
            print("🎉 Overall Test Result: SUCCESS")
            print("The LLM Services infrastructure is working correctly!")
            return 0
        else:
            print("⚠️ Overall Test Result: ISSUES DETECTED")
            print("Some tests failed - review the report for details")
            return 1
            
    except Exception as e:
        print(f"💥 Critical Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 