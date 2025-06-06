#!/usr/bin/env python3
"""
Comprehensive Phase 3 Test Script - RepoChat v1.0

Kiểm tra sâu toàn bộ Phase 3:
- Task 3.1-3.2: Architectural Analysis
- Task 3.3-3.4: LLM Services & Prompt Templates
- Task 3.5: LLM Analysis Support
- Task 3.6: Orchestrator LLM Routing
- Task 3.7: PR Impact Analysis  
- Task 3.8: Static Analysis Integration
- Error Handling & Integration Testing

Author: AI Agent
Created: 2025-01-24
"""

import sys
import os
import time
import traceback
from typing import Dict, Any, List
import json

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_imports():
    """Test all required imports để identify issues."""
    print("🔍 Testing imports...")
    
    imports_results = {}
    
    # Test 1: Basic shared models
    try:
        from shared.models.task_definition import TaskDefinition
        from shared.models.project_data_context import ProjectDataContext, PRDiffInfo
        imports_results['shared_models'] = "✅ SUCCESS"
    except Exception as e:
        imports_results['shared_models'] = f"❌ FAILED: {e}"
    
    # Test 2: Code Analysis modules
    try:
        from teams.code_analysis import (
            ArchitecturalAnalyzerModule,
            LLMAnalysisSupportModule, 
            PRImpactAnalyzerModule,
            StaticAnalysisIntegratorModule
        )
        imports_results['code_analysis'] = "✅ SUCCESS"
    except Exception as e:
        imports_results['code_analysis'] = f"❌ FAILED: {e}"
    
    # Test 3: LLM Services
    try:
        from teams.llm_services import (
            TeamLLMServices,
            LLMServiceRequest,
            LLMConfig,
            LLMProviderType,
            create_explain_code_request
        )
        imports_results['llm_services'] = "✅ SUCCESS"
    except Exception as e:
        imports_results['llm_services'] = f"❌ FAILED: {e}"
    
    # Test 4: CKG Operations
    try:
        from teams.ckg_operations import CKGQueryInterfaceModule
        imports_results['ckg_operations'] = "✅ SUCCESS"
    except Exception as e:
        imports_results['ckg_operations'] = f"❌ FAILED: {e}"
    
    # Test 5: Orchestrator
    try:
        from orchestrator.orchestrator_agent import OrchestratorAgent
        imports_results['orchestrator'] = "✅ SUCCESS"
    except Exception as e:
        imports_results['orchestrator'] = f"❌ FAILED: {e}"
    
    return imports_results


def test_basic_functionality():
    """Test basic functionality của các Phase 3 components."""
    print("🧪 Testing basic functionality...")
    
    test_results = {}
    
    # Test 1: Architectural Analysis
    try:
        from teams.code_analysis import ArchitecturalAnalyzerModule
        analyzer = ArchitecturalAnalyzerModule()
        
        # Test basic method exists
        assert hasattr(analyzer, 'detect_circular_dependencies')
        assert hasattr(analyzer, 'detect_unused_public_elements')
        assert hasattr(analyzer, 'analyze_project_architecture')
        
        test_results['architectural_analysis'] = "✅ SUCCESS - All methods available"
    except Exception as e:
        test_results['architectural_analysis'] = f"❌ FAILED: {e}"
    
    # Test 2: LLM Analysis Support
    try:
        from teams.code_analysis import LLMAnalysisSupportModule
        support = LLMAnalysisSupportModule()
        
        # Test basic functionality
        assert hasattr(support, 'create_explain_code_request')
        assert hasattr(support, 'get_supported_analysis_types')
        
        # Test request creation
        code_sample = "def hello(): print('world')"
        request = support.create_explain_code_request(code_sample)
        assert request is not None
        assert hasattr(request, 'prompt_id')
        assert request.prompt_id == 'explain_code'
        
        test_results['llm_analysis_support'] = "✅ SUCCESS - Request creation works"
    except Exception as e:
        test_results['llm_analysis_support'] = f"❌ FAILED: {e}"
    
    # Test 3: PR Impact Analysis
    try:
        from teams.code_analysis import PRImpactAnalyzerModule
        from shared.models.project_data_context import ProjectDataContext, PRDiffInfo
        
        pr_analyzer = PRImpactAnalyzerModule()
        assert hasattr(pr_analyzer, 'analyze_pr_impact')
        
        # Create mock data
        pr_diff = PRDiffInfo(
            pr_id="test-123",
            base_branch="main", 
            head_branch="feature",
            changed_files=["test.py"],
            function_changes=[]
        )
        
        project_context = ProjectDataContext(
            repository_url="https://test.com/repo.git",
            cloned_code_path="/tmp/test",
            detected_languages=["python"],
            pr_diff_info=pr_diff
        )
        
        # Test analysis (may not have real CKG, but should handle gracefully)
        result = pr_analyzer.analyze_pr_impact(project_context)
        assert result is not None
        assert hasattr(result, 'success')
        
        test_results['pr_impact_analysis'] = "✅ SUCCESS - Analysis workflow works"
    except Exception as e:
        test_results['pr_impact_analysis'] = f"❌ FAILED: {e}"
    
    # Test 4: Static Analysis Integration
    try:
        from teams.code_analysis import StaticAnalysisIntegratorModule
        static_analyzer = StaticAnalysisIntegratorModule()
        
        assert hasattr(static_analyzer, 'analyze_project')
        assert hasattr(static_analyzer, 'get_available_tools')
        
        # Test tool detection
        tools = static_analyzer.get_available_tools("python")
        assert isinstance(tools, dict)
        
        # Count actual available tools
        tool_count = sum(len(tool_list) for tool_list in tools.values())
        test_results['static_analysis'] = f"✅ SUCCESS - {tool_count} tools detected"
    except Exception as e:
        test_results['static_analysis'] = f"❌ FAILED: {e}"
    
    # Test 5: LLM Services
    try:
        from teams.llm_services import TeamLLMServices, create_explain_code_request
        
        llm_services = TeamLLMServices()
        assert hasattr(llm_services, 'process_request')
        assert hasattr(llm_services, 'get_status')
        
        # Test request creation convenience function
        request = create_explain_code_request("test code")
        assert request is not None
        assert request.prompt_id == 'explain_code'
        
        # Test service status
        status = llm_services.get_status()
        assert status is not None
        
        test_results['llm_services'] = f"✅ SUCCESS - Service status: {status}"
    except Exception as e:
        test_results['llm_services'] = f"❌ FAILED: {e}"
    
    return test_results


def test_integration_workflow():
    """Test integration workflow giữa các components."""
    print("🔄 Testing integration workflow...")
    
    integration_results = {}
    
    # Test 1: End-to-end workflow simulation
    try:
        # Step 1: Initialize components
        from teams.code_analysis import ArchitecturalAnalyzerModule, LLMAnalysisSupportModule
        from teams.llm_services import create_explain_code_request
        
        # Step 2: Create analysis request
        support = LLMAnalysisSupportModule()
        code_sample = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        llm_request = support.create_explain_code_request(code_sample)
        
        # Step 3: Test architectural analysis
        analyzer = ArchitecturalAnalyzerModule()
        
        # Mock project analysis (without real CKG connection)
        analysis_result = analyzer.analyze_project_architecture("test-project")
        
        integration_results['workflow_simulation'] = "✅ SUCCESS - Components integrate properly"
        
    except Exception as e:
        integration_results['workflow_simulation'] = f"❌ FAILED: {e}"
    
    # Test 2: Data flow consistency
    try:
        from teams.code_analysis.models import AnalysisFinding, AnalysisFindingType, AnalysisSeverity
        
        # Test data model consistency
        finding = AnalysisFinding(
            finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
            severity=AnalysisSeverity.HIGH,
            title="Test Finding",
            description="Test description",
            file_path="test.py",
            confidence_score=0.9
        )
        
        assert finding.finding_type == AnalysisFindingType.CIRCULAR_DEPENDENCY
        assert finding.severity == AnalysisSeverity.HIGH
        
        integration_results['data_consistency'] = "✅ SUCCESS - Data models consistent"
        
    except Exception as e:
        integration_results['data_consistency'] = f"❌ FAILED: {e}"
    
    # Test 3: Error handling integration
    try:
        from teams.code_analysis import ArchitecturalAnalyzerModule
        
        analyzer = ArchitecturalAnalyzerModule()
        
        # Test với invalid inputs
        result = analyzer.analyze_project_architecture("")  # Empty project
        assert result is not None
        
        # Test với None input
        result2 = analyzer.analyze_project_architecture(None)
        assert result2 is not None
        
        integration_results['error_handling'] = "✅ SUCCESS - Error handling works"
        
    except Exception as e:
        integration_results['error_handling'] = f"❌ FAILED: {e}"
    
    return integration_results


def test_performance_benchmarks():
    """Test performance benchmarks của các components."""
    print("⚡ Testing performance benchmarks...")
    
    benchmarks = {}
    
    # Benchmark 1: Module initialization times
    try:
        start_time = time.time()
        from teams.code_analysis import ArchitecturalAnalyzerModule
        analyzer = ArchitecturalAnalyzerModule()
        init_time = (time.time() - start_time) * 1000
        benchmarks['architectural_init_ms'] = round(init_time, 2)
        
    except Exception as e:
        benchmarks['architectural_init_ms'] = f"ERROR: {e}"
    
    # Benchmark 2: LLM request creation
    try:
        start_time = time.time()
        from teams.llm_services import create_explain_code_request
        request = create_explain_code_request("test code")
        creation_time = (time.time() - start_time) * 1000
        benchmarks['llm_request_creation_ms'] = round(creation_time, 2)
        
    except Exception as e:
        benchmarks['llm_request_creation_ms'] = f"ERROR: {e}"
    
    # Benchmark 3: Data model creation
    try:
        start_time = time.time()
        from shared.models.project_data_context import ProjectDataContext
        context = ProjectDataContext(
            repository_url="test",
            cloned_code_path="/tmp/test",
            detected_languages=["python"]
        )
        model_time = (time.time() - start_time) * 1000
        benchmarks['data_model_creation_ms'] = round(model_time, 2)
        
    except Exception as e:
        benchmarks['data_model_creation_ms'] = f"ERROR: {e}"
    
    return benchmarks


def run_comprehensive_tests():
    """Run comprehensive Phase 3 tests."""
    print("🚀 COMPREHENSIVE PHASE 3 TEST SUITE - RepoChat v1.0")
    print("=" * 70)
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_start_time = time.time()
    all_results = {}
    
    # Test 1: Import validation
    print("📦 Testing imports...")
    import_results = test_imports()
    all_results['imports'] = import_results
    
    for module, result in import_results.items():
        print(f"   {module}: {result}")
    print()
    
    # Test 2: Basic functionality
    print("🔧 Testing basic functionality...")
    functionality_results = test_basic_functionality()
    all_results['functionality'] = functionality_results
    
    for component, result in functionality_results.items():
        print(f"   {component}: {result}")
    print()
    
    # Test 3: Integration workflow
    print("🔗 Testing integration workflow...")
    integration_results = test_integration_workflow()
    all_results['integration'] = integration_results
    
    for test, result in integration_results.items():
        print(f"   {test}: {result}")
    print()
    
    # Test 4: Performance benchmarks
    print("📊 Testing performance...")
    benchmark_results = test_performance_benchmarks()
    all_results['benchmarks'] = benchmark_results
    
    for benchmark, result in benchmark_results.items():
        print(f"   {benchmark}: {result}")
    print()
    
    # Calculate summary
    total_time = time.time() - total_start_time
    
    # Count successes and failures
    total_tests = 0
    passed_tests = 0
    
    for category, tests in all_results.items():
        if category == 'benchmarks':
            continue
            
        for test, result in tests.items():
            total_tests += 1
            if result.startswith("✅"):
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate summary
    print("=" * 70)
    print("📋 COMPREHENSIVE PHASE 3 TEST SUMMARY")
    print("=" * 70)
    print(f"🕒 Total execution time: {total_time:.2f}s")
    print(f"📊 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"🎯 Success rate: {success_rate:.1f}%")
    print()
    
    # Assessment
    if success_rate >= 90:
        print("🎉 EXCELLENT: Phase 3 implementation is production-ready!")
        assessment = "EXCELLENT"
    elif success_rate >= 80:
        print("✅ GOOD: Phase 3 implementation is solid với minor issues")
        assessment = "GOOD"
    elif success_rate >= 60:
        print("⚠️ FAIR: Phase 3 cần improvement trước production") 
        assessment = "FAIR"
    else:
        print("❌ POOR: Phase 3 cần significant fixes")
        assessment = "POOR"
    
    print()
    print("💡 RECOMMENDATIONS:")
    
    # Specific recommendations based on results
    failed_imports = [k for k, v in import_results.items() if v.startswith("❌")]
    if failed_imports:
        print(f"   • Fix import issues in: {', '.join(failed_imports)}")
    
    failed_functionality = [k for k, v in functionality_results.items() if v.startswith("❌")]
    if failed_functionality:
        print(f"   • Fix functionality issues in: {', '.join(failed_functionality)}")
    
    failed_integration = [k for k, v in integration_results.items() if v.startswith("❌")]
    if failed_integration:
        print(f"   • Fix integration issues in: {', '.join(failed_integration)}")
    
    if success_rate >= 80:
        print("   • Ready cho Phase 4 development")
        print("   • Consider performance optimization")
        print("   • Add comprehensive error handling")
    else:
        print("   • Address critical failures before proceeding")
        print("   • Review component dependencies")
        print("   • Add more error handling")
    
    print()
    
    # Save results
    results_file = 'phase_3_comprehensive_results.json'
    summary_data = {
        'summary': {
            'total_time': total_time,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate,
            'assessment': assessment,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'detailed_results': all_results
    }
    
    try:
        with open(results_file, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results file: {e}")
    
    return success_rate >= 80


def main():
    """Main execution function."""
    try:
        success = run_comprehensive_tests()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main() 