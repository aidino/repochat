#!/bin/bash

# =============================================================================
# RepoChat v1.0 Docker Stop Script
# =============================================================================

set -e

echo "🛑 Stopping RepoChat v1.0 Services..."

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

# Parse command line arguments
CLEANUP=false
REMOVE_VOLUMES=false
SERVICES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--cleanup)
            CLEANUP=true
            shift
            ;;
        -v|--volumes)
            REMOVE_VOLUMES=true
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
            echo "  -c, --cleanup        Remove containers and images"
            echo "  -v, --volumes        Remove volumes (WARNING: This will delete all data!)"
            echo "  -s, --services       Stop specific services only"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                   # Stop all services"
            echo "  $0 -c                # Stop and remove containers/images"
            echo "  $0 -v                # Stop and remove everything including data"
            echo "  $0 -s 'frontend'     # Stop only frontend service"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    print_error "docker compose is not installed."
    exit 1
fi

# Stop services
if [ -n "$SERVICES" ]; then
    print_status "Stopping specific services: $SERVICES"
    docker compose stop $SERVICES
else
    print_status "Stopping all services..."
    docker compose down
fi

if [ "$CLEANUP" = true ]; then
    print_status "Removing containers and networks..."
    docker compose down --remove-orphans
    
    print_status "Removing images..."
    docker compose down --rmi local
    
    # Clean up dangling images
    print_status "Cleaning up dangling images..."
    docker image prune -f
fi

if [ "$REMOVE_VOLUMES" = true ]; then
    print_warning "⚠️  WARNING: This will permanently delete all data!"
    read -p "Are you sure you want to remove all volumes? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_status "Removing volumes..."
        docker compose down -v
        
        # Remove custom data directories
        print_status "Removing data directories..."
        sudo rm -rf data/neo4j/* data/redis/* logs/neo4j/* 2>/dev/null || true
        
        print_warning "All data has been permanently deleted!"
    else
        print_status "Volume removal cancelled."
    fi
fi

print_success "RepoChat services stopped successfully!"

# Show remaining containers if any
if docker ps -q --filter "name=repochat" | grep -q .; then
    print_status "Remaining RepoChat containers:"
    docker ps --filter "name=repochat" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    print_success "All RepoChat containers have been stopped."
fi 