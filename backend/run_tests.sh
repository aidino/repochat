#!/bin/bash

# RepoChat Phase 1-3 Quick Test Runner
# Runs various test scenarios with different configurations

set -e

echo "🧪 RepoChat Phase 1-3 Test Runner"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "comprehensive_phase_1_3_manual_test.py" ]]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Activate virtual environment if it exists
if [[ -d "venv" ]]; then
    print_info "Activating virtual environment..."
    source venv/bin/activate
fi

# Test scenarios
echo ""
echo "📋 Available Test Scenarios:"
echo "1. Quick Test (Small Repository)"
echo "2. Java Repository Test (Spring PetClinic)"
echo "3. Python Repository Test (Flask)"
echo "4. Full Test with LLM (requires OpenAI API key)"
echo "5. Performance Test (Multiple repositories)"
echo "6. Custom Repository Test"
echo ""

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [scenario_number|custom_url]"
    echo "Example: $0 1                    # Quick test"
    echo "Example: $0 4                    # Full test with LLM"
    echo "Example: $0 https://github.com/user/repo.git  # Custom repository"
    exit 1
fi

SCENARIO=$1

case $SCENARIO in
    1)
        print_info "Running Quick Test with small repository..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/octocat/Hello-World.git \
            --output quick_test_results.json
        ;;
    2)
        print_info "Running Java Repository Test (Spring PetClinic)..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/spring-projects/spring-petclinic.git \
            --output java_test_results.json
        ;;
    3)
        print_info "Running Python Repository Test (Flask)..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/pallets/flask.git \
            --output python_test_results.json
        ;;
    4)
        print_info "Running Full Test with LLM (requires OpenAI API key)..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/spring-projects/spring-petclinic.git \
            --openai-test \
            --output full_llm_test_results.json
        ;;
    5)
        print_info "Running Performance Test with multiple repositories..."
        
        # Small repo
        print_info "Testing small repository..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/octocat/Hello-World.git \
            --output perf_small_results.json
        
        # Medium repo
        print_info "Testing medium repository..."
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url https://github.com/spring-projects/spring-petclinic.git \
            --output perf_medium_results.json
        
        print_success "Performance testing completed!"
        ;;
    6)
        if [[ $# -lt 2 ]]; then
            echo "❌ Please provide a repository URL for custom test"
            echo "Example: $0 6 https://github.com/user/repo.git"
            exit 1
        fi
        
        CUSTOM_URL=$2
        print_info "Running Custom Repository Test: $CUSTOM_URL"
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url "$CUSTOM_URL" \
            --output custom_test_results.json
        ;;
    http*|git*)
        # URL provided directly
        print_info "Running Custom Repository Test: $SCENARIO"
        python comprehensive_phase_1_3_manual_test.py \
            --repo-url "$SCENARIO" \
            --output custom_test_results.json
        ;;
    *)
        echo "❌ Invalid scenario: $SCENARIO"
        echo "Valid scenarios: 1, 2, 3, 4, 5, 6, or a repository URL"
        exit 1
        ;;
esac

echo ""
print_success "Test execution completed!"
echo ""
echo "📊 View Results:"
echo "  - Check test_results/ directory for JSON files"
echo "  - Check logs/ directory for detailed logs"
echo ""
echo "📈 Quick Analysis:"
if [[ -f "test_results/$(ls -t test_results/ | head -1)" ]]; then
    LATEST_RESULT="test_results/$(ls -t test_results/ | head -1)"
    echo "  Latest result file: $LATEST_RESULT"
    
    if command -v jq &> /dev/null; then
        echo ""
        echo "  📋 Test Summary:"
        jq -r '.summary | "    Total Tests: \(.total_tests // "N/A") | Success Rate: \(.success_rate // "N/A")% | Overall: \(if .overall_success then "✅ PASS" else "❌ FAIL" end)"' "$LATEST_RESULT"
        
        echo ""
        echo "  🔍 Phase Results:"
        jq -r '.phases[] | "    \(if .success then "✅" else "❌" end) \(.phase) (\(.tests | length) tests)"' "$LATEST_RESULT"
    else
        echo "  Install 'jq' for detailed result analysis: brew install jq"
    fi
fi

echo ""
echo "🚀 Next Steps:"
echo "  - Review test results and logs"
echo "  - Check Neo4j Browser: http://localhost:7474"
echo "  - Run different scenarios to test various repositories"
echo "" 