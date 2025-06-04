#!/bin/bash

# RepoChat Development Environment Setup Script
# This script sets up the Docker development environment for RepoChat v1.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_docker() {
    log "Checking Docker installation..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Installation instructions: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command_exists docker compose; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Installation instructions: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are available"
    
    # Show versions
    docker_version=$(docker --version)
    compose_version=$(docker compose --version)
    log "Docker version: $docker_version"
    log "Docker Compose version: $compose_version"
}

# Function to setup environment file
setup_env() {
    log "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            log_success "Created .env file from env.example"
            log_warning "Please edit .env file and add your OpenAI API key"
        else
            log_error "env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        log_success ".env file already exists"
    fi
}

# Function to create required directories
create_directories() {
    log "Creating required directories..."
    
    directories=(
        "logs"
        "temp" 
        "data/neo4j"
        "data/uploads"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log "Directory already exists: $dir"
        fi
    done
}

# Function to build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build backend image
    log "Building backend image..."
    docker compose build backend
    log_success "Backend image built successfully"
    
    # Note: Frontend will be built in later phases
    log "Frontend image build will be available in Phase 5"
}

# Function to start services
start_services() {
    log "Starting RepoChat services..."
    
    # Start only backend and Neo4j (no frontend in Phase 1)
    docker compose up -d neo4j
    log "Waiting for Neo4j to be healthy..."
    
    # Wait for Neo4j to be ready
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker compose exec -T neo4j cypher-shell -u neo4j -p repochat123 "RETURN 1" >/dev/null 2>&1; then
            log_success "Neo4j is ready!"
            break
        fi
        
        attempt=$((attempt + 1))
        log "Waiting for Neo4j... (attempt $attempt/$max_attempts)"
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Neo4j failed to start within expected time"
        exit 1
    fi
    
    # Start backend
    docker compose up -d backend
    log_success "Backend service started"
    
    # Show service status
    docker compose ps
}

# Function to show useful information
show_info() {
    log_success "RepoChat development environment is ready!"
    echo
    echo "📋 Service Information:"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "  🔍 Neo4j Browser: http://localhost:7474"
    echo "     Username: neo4j"
    echo "     Password: repochat123"
    echo
    echo "📁 Important directories:"
    echo "  📝 Logs: ./logs/"
    echo "  🗃️  Temp files: ./temp/"
    echo "  💾 Neo4j data: ./data/neo4j/"
    echo
    echo "🛠️  Useful commands:"
    echo "  📊 View logs: docker compose logs -f backend"
    echo "  🔄 Restart backend: docker compose restart backend"
    echo "  ⏹️  Stop all: docker compose down"
    echo "  🗑️  Clean up: docker compose down -v --remove-orphans"
    echo
    echo "🧪 Run tests:"
    echo "  docker compose exec backend python -m pytest tests/ -v"
    echo
    echo "🐛 Debug:"
    echo "  VS Code can attach to debug port 5678"
    echo "  Or exec into container: docker compose exec backend bash"
}

# Function to run tests
run_tests() {
    log "Running tests to verify setup..."
    
    # Wait a bit for backend to be ready
    sleep 5
    
    if docker compose exec -T backend python -m pytest tests/ -v; then
        log_success "All tests passed!"
    else
        log_warning "Some tests failed. Check the logs for details."
        log "You can run tests manually with: docker compose exec backend python -m pytest tests/ -v"
    fi
}

# Main execution
main() {
    echo "🚀 RepoChat v1.0 Development Environment Setup"
    echo "=============================================="
    echo
    
    check_docker
    setup_env
    create_directories
    build_images
    start_services
    run_tests
    show_info
    
    log_success "Setup completed successfully! 🎉"
}

# Handle script arguments
case "${1:-}" in
    --build-only)
        log "Building images only..."
        build_images
        ;;
    --start-only)
        log "Starting services only..."
        start_services
        ;;
    --test-only)
        log "Running tests only..."
        run_tests
        ;;
    *)
        main
        ;;
esac 