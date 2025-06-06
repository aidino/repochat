#!/bin/bash

# =============================================================================
# RepoChat v1.0 Docker Startup Script
# =============================================================================

set -e

echo "🚀 Starting RepoChat v1.0 Multi-Service Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    print_error "docker compose is not installed. Please install Docker Compose."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/neo4j data/redis logs/neo4j logs temp

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp env.template .env
    print_warning "Please edit .env file with your configuration before starting services"
    print_warning "Especially set your API keys: OPENAI_API_KEY, GOOGLE_API_KEY, etc."
fi

# Parse command line arguments
MODE="development"
SERVICES=""
DETACHED=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--production)
            MODE="production"
            shift
            ;;
        -d|--detached)
            DETACHED=true
            shift
            ;;
        -s|--services)
            SERVICES="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --production     Run in production mode"
            echo "  -d, --detached       Run in detached mode"
            echo "  -s, --services       Run specific services (e.g., 'neo4j backend')"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                   # Start all services in development mode"
            echo "  $0 -d                # Start detached"
            echo "  $0 -p -d             # Start in production mode, detached"
            echo "  $0 -s 'neo4j backend' # Start only neo4j and backend"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build Docker Compose command
COMPOSE_CMD="docker compose"

  if [ "$MODE" = "production" ]; then
    COMPOSE_CMD="$COMPOSE_CMD -f docker-compose.yml -f docker-compose.prod.yml"
    print_status "Starting in PRODUCTION mode..."
else
    print_status "Starting in DEVELOPMENT mode..."
fi

# Stop existing containers
print_status "Stopping existing containers..."
$COMPOSE_CMD down

# Pull latest images
print_status "Pulling latest images..."
$COMPOSE_CMD pull

# Build services
print_status "Building services..."
if [ -n "$SERVICES" ]; then
    $COMPOSE_CMD build $SERVICES
else
    $COMPOSE_CMD build
fi

# Start services
print_status "Starting services..."
if [ "$DETACHED" = true ]; then
    if [ -n "$SERVICES" ]; then
        $COMPOSE_CMD up -d $SERVICES
    else
        $COMPOSE_CMD up -d
    fi
    print_success "Services started in detached mode!"
else
    if [ -n "$SERVICES" ]; then
        $COMPOSE_CMD up $SERVICES
    else
        $COMPOSE_CMD up
    fi
fi

# Wait a moment for services to start
if [ "$DETACHED" = true ]; then
    sleep 5
    
    # Show service status
    print_status "Service Status:"
    $COMPOSE_CMD ps
    
    echo ""
    print_success "RepoChat v1.0 is now running!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "🗃️  Neo4j Browser: http://localhost:7474 (neo4j/repochat123)"
    echo "📊 Redis: localhost:6379"
    echo ""
    echo "📝 View logs: docker compose logs -f"
    echo "🛑 Stop services: docker compose down"
    echo "🔄 Restart: docker compose restart"
fi 