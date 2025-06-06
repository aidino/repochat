#!/bin/bash

# =============================================================================
# RepoChat v1.0 Docker Test Script
# =============================================================================

set -e

echo "🧪 Testing RepoChat v1.0 Docker Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running: $test_name"
    
    if eval "$test_command"; then
        print_success "$test_name"
        ((TESTS_PASSED++))
    else
        print_error "$test_name"
        ((TESTS_FAILED++))
    fi
    echo ""
}

echo "🔍 Pre-flight Checks..."
echo ""

# Test 1: Docker availability
run_test "Docker installation" "docker --version > /dev/null 2>&1"

# Test 2: Docker Compose availability
run_test "Docker Compose installation" "docker compose version > /dev/null 2>&1"

# Test 3: Docker service running
run_test "Docker service status" "docker info > /dev/null 2>&1"

# Test 4: Docker Compose file syntax
run_test "Docker Compose file syntax" "docker compose config > /dev/null 2>&1"

# Test 5: Required directories
run_test "Required directories exist" "mkdir -p data/neo4j data/redis logs/neo4j logs temp && echo 'Directories created'"

# Test 6: Environment file
if [ -f .env ]; then
    run_test "Environment file exists" "echo '.env file found'"
else
    print_warning "Environment file not found - will copy from template"
    run_test "Copy environment template" "cp env.template .env"
fi

echo "🚀 Docker Services Test..."
echo ""

# Test 7: Build services (if needed)
run_test "Build Docker images" "docker compose build --no-cache > /dev/null 2>&1"

# Test 8: Start services
print_status "Starting services in background..."
if docker compose up -d; then
    print_success "Services started"
    ((TESTS_PASSED++))
else
    print_error "Failed to start services"
    ((TESTS_FAILED++))
fi
echo ""

# Wait for services to initialize
print_status "Waiting for services to initialize (30 seconds)..."
sleep 30

# Test 9: Neo4j health check
run_test "Neo4j health check" "docker exec repochat-neo4j cypher-shell -u neo4j -p repochat123 'RETURN 1' > /dev/null 2>&1"

# Test 10: Backend health check
run_test "Backend health check" "curl -f http://localhost:8000/health > /dev/null 2>&1 || curl -f http://localhost:8000/ > /dev/null 2>&1"

# Test 11: Frontend health check  
run_test "Frontend health check" "curl -f http://localhost:3000 > /dev/null 2>&1"

# Test 12: Redis health check
run_test "Redis health check" "docker exec repochat-redis redis-cli ping > /dev/null 2>&1"

echo "📊 Service Status..."
echo ""
docker compose ps

echo ""
echo "📋 Test Summary:"
echo "=================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! 🎉"
    echo ""
    echo "✅ RepoChat v1.0 is ready to use!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo "   Neo4j:    http://localhost:7474 (neo4j/repochat123)"
    echo ""
    echo "📝 To stop services: ./stop-docker.sh"
else
    print_error "Some tests failed. Please check the logs above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check Docker is running: docker info"
    echo "   2. Check logs: docker compose logs"
    echo "   3. Restart services: docker compose restart"
    echo ""
    echo "📖 For detailed help, see: DOCKER_SETUP_COMPLETE.md"
fi

echo ""
echo "�� Test completed." 