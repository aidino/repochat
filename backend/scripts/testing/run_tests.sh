#!/bin/bash

# RepoChat Testing Script
# Updated for refactored structure
# Author: RepoChat Development Team
# Date: 2025-06-06

set -e  # Exit on any error

echo "🧪 RepoChat Testing Script - Refactored Structure"
echo "=================================================="

# Check if we're in the correct directory
if [[ ! -d "src" || ! -f "requirements.txt" ]]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: .../repochat/backend"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
echo "📂 PYTHONPATH set to: ${PYTHONPATH}"

# Function to run a test with error handling
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo ""
    echo "🔸 Running: $test_name"
    echo "   Command: $test_command"
    echo "   Time: $(date '+%Y-%m-%d %H:%M:%S')"
    
    if eval "$test_command"; then
        echo "   ✅ $test_name: PASSED"
        return 0
    else
        echo "   ❌ $test_name: FAILED"
        return 1
    fi
}

# Initialize test results
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0

# Test function with result tracking
test_with_tracking() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if run_test "$test_name" "$test_command"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo ""
echo "🧪 Phase 1: Unit Tests"
echo "======================"

# Core unit tests
test_with_tracking "Git Operations" "python -m pytest tests/test_git_operations_module.py -v"
test_with_tracking "Language Identifier" "python -m pytest tests/test_language_identifier_module.py -v"
test_with_tracking "Java Parser" "python -m pytest tests/test_java_parser.py -v"
test_with_tracking "Python Parser" "python -m pytest tests/test_python_parser.py -v"
test_with_tracking "Neo4j Connection" "python -m pytest tests/test_neo4j_connection_module.py -v"

echo ""
echo "🧪 Phase 2: Integration Tests"
echo "============================="

# Integration tests (updated paths)
test_with_tracking "Phase 1 Integration" "python tests/integration/integration_test_phase_1.py"
test_with_tracking "Quick Integration" "python tests/integration/quick_integration_test.py"

echo ""
echo "🧪 Phase 3: Specific Feature Tests"
echo "=================================="

# Phase 3 tests (updated paths)
test_with_tracking "Phase 3 Completion" "python tests/phase_3_specific/phase_3_completion_test.py"
test_with_tracking "Task 3.1 Architectural Analyzer" "python -m pytest tests/test_task_3_1_architectural_analyzer_module.py -v"
test_with_tracking "Task 3.3 LLM Services" "python -m pytest tests/test_task_3_3_llm_services.py -v"
test_with_tracking "Task 3.4 LLM Gateway" "python -m pytest tests/test_task_3_4_llm_gateway_formatter.py -v"
test_with_tracking "Task 3.5 LLM Analysis Support" "python -m pytest tests/test_task_3_5_llm_analysis_support.py -v"

echo ""
echo "🧪 Phase 4: Manual & Performance Tests"
echo "======================================"

# Manual tests (updated paths - optional, only if time permits)
if [[ "${QUICK_TEST:-}" != "true" ]]; then
    test_with_tracking "Manual Phase 2 Complete" "python tests/manual/manual_test_phase_2_complete_fixed.py"
    
    # Performance tests (updated paths - optional)
    if [[ "${PERFORMANCE_TEST:-}" == "true" ]]; then
        test_with_tracking "Performance Test" "python scripts/testing/performance_test_real_projects.py"
    fi
fi

echo ""
echo "📊 FINAL TEST RESULTS"
echo "===================="
echo "✅ Passed: $PASSED_TESTS/$TOTAL_TESTS tests"
echo "❌ Failed: $FAILED_TESTS/$TOTAL_TESTS tests"

# Calculate success percentage
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo "📈 Success Rate: ${SUCCESS_RATE}%"
else
    echo "⚠️  No tests were run"
    exit 1
fi

echo "🕐 Completed at: $(date '+%Y-%m-%d %H:%M:%S')"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED! RepoChat is ready for Phase 4!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please review and fix issues before proceeding."
    exit 1
fi 