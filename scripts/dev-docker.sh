#!/bin/bash

# RepoChat Development Environment with Docker
# Script để khởi chạy toàn bộ development stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 RepoChat Development Environment${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed.${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f env.template ]; then
        cp env.template .env
        echo -e "${GREEN}✅ .env file created from template${NC}"
        echo -e "${YELLOW}📝 Please edit .env file and add your API keys${NC}"
    else
        echo -e "${RED}❌ env.template not found${NC}"
        exit 1
    fi
fi

# Function to show service status
show_status() {
    echo -e "\n${BLUE}📊 Service Status:${NC}"
    docker-compose ps
}

# Function to show logs
show_logs() {
    echo -e "\n${BLUE}📋 Recent Logs:${NC}"
    docker-compose logs --tail=20
}

# Function to show URLs
show_urls() {
    echo -e "\n${GREEN}🌐 Service URLs:${NC}"
    echo -e "  Frontend (Vue.js): ${YELLOW}http://localhost:3000${NC}"
    echo -e "  Backend (FastAPI): ${YELLOW}http://localhost:8000${NC}"
    echo -e "  Neo4j Browser:     ${YELLOW}http://localhost:7474${NC}"
    echo -e "  Neo4j Credentials: ${YELLOW}neo4j/repochat123${NC}"
}

# Function to cleanup
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Set trap for cleanup on script exit
trap cleanup EXIT

# Main execution
case "${1:-start}" in
    "start"|"up")
        echo -e "${GREEN}🏁 Starting all services...${NC}"
        docker-compose up --build -d
        
        echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
        sleep 10
        
        show_status
        show_urls
        
        echo -e "\n${GREEN}✅ Development environment is ready!${NC}"
        echo -e "${BLUE}💡 Use 'docker-compose logs -f' to follow logs${NC}"
        echo -e "${BLUE}💡 Use 'Ctrl+C' to stop all services${NC}"
        
        # Follow logs
        echo -e "\n${BLUE}📋 Following logs (Ctrl+C to stop):${NC}"
        docker-compose logs -f
        ;;
        
    "build")
        echo -e "${GREEN}🔨 Building all services...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✅ Build completed${NC}"
        ;;
        
    "stop"|"down")
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        exit 0
        ;;
        
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up containers and volumes...${NC}"
        docker-compose down -v
        docker-compose down --rmi all --volumes --remove-orphans
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        exit 0
        ;;
        
    "status")
        show_status
        show_urls
        exit 0
        ;;
        
    "logs")
        show_logs
        exit 0
        ;;
        
    "restart")
        echo -e "${YELLOW}♻️  Restarting all services...${NC}"
        docker-compose restart
        show_status
        show_urls
        exit 0
        ;;
        
    "help"|"-h"|"--help")
        echo -e "${BLUE}Usage: $0 [command]${NC}"
        echo -e ""
        echo -e "Commands:"
        echo -e "  start, up    - Start all services (default)"
        echo -e "  build        - Build all Docker images"
        echo -e "  stop, down   - Stop all services"
        echo -e "  clean        - Stop and remove all containers/volumes"
        echo -e "  status       - Show service status and URLs"
        echo -e "  logs         - Show recent logs"
        echo -e "  restart      - Restart all services"
        echo -e "  help         - Show this help message"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "Use '$0 help' for available commands"
        exit 1
        ;;
esac 