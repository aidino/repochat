#!/bin/bash

# 🚀 RepoChat Phase 4 Demo Script
# Demonstrates all implemented Phase 4 features

set -e  # Exit on any error

echo "🎉 =============================================="
echo "🚀 RepoChat Phase 4 Demo"
echo "🎉 =============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}🔵 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker Compose is running
print_header "Checking Prerequisites"

if ! docker-compose ps | grep -q "repochat-backend.*Up"; then
    print_error "Backend container is not running!"
    print_warning "Please start services first: docker-compose up -d"
    exit 1
fi

if ! docker-compose ps | grep -q "repochat-neo4j.*Up"; then
    print_error "Neo4j container is not running!"
    print_warning "Please start services first: docker-compose up -d"
    exit 1
fi

print_success "All prerequisites met!"

# Demo 1: System Status
print_header "Demo 1: System Status Check (CLI Framework)"

echo "Command: docker-compose exec backend python repochat_cli.py status"
echo ""

docker-compose exec -T backend python repochat_cli.py status || {
    print_error "System status check failed"
    exit 1
}

print_success "System status check completed"

# Demo 2: Help Documentation
print_header "Demo 2: Help Documentation"

echo "Command: docker-compose exec backend python repochat_cli.py --help"
echo ""

docker-compose exec -T backend python repochat_cli.py --help || {
    print_error "Help command failed"
    exit 1
}

print_success "Help documentation displayed"

# Demo 3: Scan Project (Task 4.1)
print_header "Demo 3: Scan Project Feature (Task 4.1)"

echo "Command: docker-compose exec backend python repochat_cli.py scan-project https://github.com/spring-projects/spring-petclinic.git -v"
echo ""
print_warning "This will clone a real repository and may take 5-10 seconds..."
echo ""

start_time=$(date +%s)
docker-compose exec -T backend python repochat_cli.py scan-project https://github.com/spring-projects/spring-petclinic.git -v || {
    print_error "Scan project failed"
    exit 1
}
end_time=$(date +%s)
duration=$((end_time - start_time))

print_success "Scan project completed in ${duration}s"

# Demo 4: Review PR (Task 4.2)
print_header "Demo 4: Review PR Feature (Task 4.2)"

echo "Command: docker-compose exec backend python repochat_cli.py review-pr https://github.com/spring-projects/spring-petclinic.git 123 -v"
echo ""
print_warning "This demonstrates PR review workflow..."
echo ""

start_time=$(date +%s)
docker-compose exec -T backend python repochat_cli.py review-pr https://github.com/spring-projects/spring-petclinic.git 123 -v || {
    print_error "Review PR failed"
    exit 1
}
end_time=$(date +%s)
duration=$((end_time - start_time))

print_success "Review PR completed in ${duration}s"

# Demo 5: Finding Aggregator Module (Task 4.4)
print_header "Demo 5: Finding Aggregator Module (Task 4.4)"

echo "Command: docker-compose exec backend python -m pytest tests/test_task_4_4_finding_aggregator.py -v --tb=short"
echo ""
print_warning "Running comprehensive test suite for FindingAggregatorModule..."
echo ""

docker-compose exec -T backend python -m pytest tests/test_task_4_4_finding_aggregator.py -v --tb=short || {
    print_error "Finding Aggregator tests failed"
    exit 1
}

print_success "All Finding Aggregator tests passed"

# Demo 6: Phase 3 Foundation Verification
print_header "Demo 6: Phase 3 Foundation Verification"

echo "Command: docker-compose exec backend python tests/phase_3_specific/phase_3_completion_test.py"
echo ""
print_warning "Verifying Phase 1-3 foundation is solid..."
echo ""

docker-compose exec -T backend python tests/phase_3_specific/phase_3_completion_test.py || {
    print_error "Phase 3 foundation verification failed"
    exit 1
}

print_success "Phase 3 foundation verification completed"

# Demo 7: Neo4j Database Inspection
print_header "Demo 7: Neo4j Database Content"

echo "Checking Neo4j database content after processing..."
echo ""

echo "Query: MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC"
echo ""

docker-compose exec -T neo4j cypher-shell -u neo4j -p repochat123 "
MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count 
ORDER BY Count DESC LIMIT 10
" || {
    print_warning "Neo4j query failed, but this is optional"
}

print_success "Database inspection completed"

# Demo 8: Performance Metrics
print_header "Demo 8: System Performance"

echo "Checking Docker container resource usage..."
echo ""

echo "Container Status:"
docker-compose ps

echo ""
echo "Resource Usage:"
timeout 5s docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" repochat-backend repochat-neo4j || {
    print_warning "Resource monitoring timed out"
}

print_success "Performance metrics collected"

# Summary
print_header "🎉 Demo Summary"

echo "✅ Phase 4 Features Demonstrated:"
echo "   • Task 4.1: CLI Interface với scan-project ✅"
echo "   • Task 4.2: CLI extension với review-pr ✅"
echo "   • Task 4.3: TaskInitiationModule (via CLI) ✅"
echo "   • Task 4.4: FindingAggregatorModule ✅"
echo ""
echo "🚧 Remaining Phase 4 Tasks:"
echo "   • Task 4.5: ReportGeneratorModule"
echo "   • Task 4.6: PR Impact Integration"
echo "   • Task 4.7: OutputFormatterModule"
echo "   • Task 4.8: PresentationModule"
echo "   • Task 4.9: Q&A Functionality"
echo ""
echo "📊 Foundation Status:"
echo "   • Phase 1: ✅ COMPLETED (100%)"
echo "   • Phase 2: ✅ COMPLETED (100%)"
echo "   • Phase 3: ✅ COMPLETED (100%)"
echo "   • Phase 4: 🚧 IN PROGRESS (4/9 tasks completed)"
echo ""
print_success "RepoChat v1.0 is ready for Phase 4 continuation!"
echo ""
echo "🔗 Next Steps:"
echo "   1. Implement Task 4.5 (ReportGeneratorModule)"
echo "   2. Continue with Tasks 4.6-4.9"
echo "   3. Move to Phase 5 (Vue.js Frontend)"
echo ""
print_success "Demo completed successfully! 🎉" 