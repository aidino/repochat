#!/bin/bash

# RepoChat Production Environment with Docker
# Script để deploy production stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 RepoChat Production Deployment${NC}"
echo -e "${BLUE}==================================${NC}"

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
    echo -e "${RED}❌ .env file not found. Please create it first.${NC}"
    exit 1
fi

# Production docker-compose override
create_prod_override() {
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  # Production Frontend with Nginx
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    volumes: []  # No volume mounts in production
    restart: always

  # Production Backend
  backend:
    build:
      target: production
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      # Only mount necessary directories
      - ./logs:/app/logs
      - ./temp:/app/temp
    restart: always

  # Production Neo4j
  neo4j:
    environment:
      - NEO4J_dbms_memory_heap_max__size=4g
    restart: always

volumes:
  # Remove dev-specific volumes
  frontend_node_modules: null
  backend_pip_cache: null
EOF
}

# Function to show service status
show_status() {
    echo -e "\n${BLUE}📊 Service Status:${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
}

# Function to show URLs
show_urls() {
    echo -e "\n${GREEN}🌐 Production URLs:${NC}"
    echo -e "  Frontend:          ${YELLOW}http://localhost${NC}"
    echo -e "  Backend API:       ${YELLOW}http://localhost/api${NC}"
    echo -e "  Backend Direct:    ${YELLOW}http://localhost:8000${NC}"
    echo -e "  Neo4j Browser:     ${YELLOW}http://localhost:7474${NC}"
    echo -e "  Neo4j Credentials: ${YELLOW}neo4j/repochat123${NC}"
}

# Main execution
case "${1:-deploy}" in
    "deploy"|"up")
        echo -e "${GREEN}📝 Creating production configuration...${NC}"
        create_prod_override
        
        echo -e "${GREEN}🏗️  Building production images...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
        
        echo -e "${GREEN}🚀 Deploying production stack...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        
        echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
        sleep 15
        
        show_status
        show_urls
        
        echo -e "\n${GREEN}✅ Production deployment completed!${NC}"
        echo -e "${BLUE}💡 Use './scripts/prod-docker.sh logs' to view logs${NC}"
        echo -e "${BLUE}💡 Use './scripts/prod-docker.sh stop' to stop services${NC}"
        ;;
        
    "build")
        echo -e "${GREEN}🔨 Building production images...${NC}"
        create_prod_override
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
        echo -e "${GREEN}✅ Build completed${NC}"
        ;;
        
    "stop"|"down")
        echo -e "${YELLOW}🛑 Stopping production services...${NC}"
        if [ -f docker-compose.prod.yml ]; then
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
        else
            docker-compose down
        fi
        echo -e "${GREEN}✅ Production services stopped${NC}"
        ;;
        
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up production environment...${NC}"
        if [ -f docker-compose.prod.yml ]; then
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --rmi all
        fi
        rm -f docker-compose.prod.yml
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
        
    "status")
        if [ -f docker-compose.prod.yml ]; then
            show_status
            show_urls
        else
            echo -e "${RED}❌ Production environment not deployed${NC}"
        fi
        ;;
        
    "logs")
        if [ -f docker-compose.prod.yml ]; then
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs "${2:-}"
        else
            echo -e "${RED}❌ Production environment not deployed${NC}"
        fi
        ;;
        
    "restart")
        echo -e "${YELLOW}♻️  Restarting production services...${NC}"
        if [ -f docker-compose.prod.yml ]; then
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart
            show_status
            show_urls
        else
            echo -e "${RED}❌ Production environment not deployed${NC}"
        fi
        ;;
        
    "help"|"-h"|"--help")
        echo -e "${BLUE}Usage: $0 [command]${NC}"
        echo -e ""
        echo -e "Commands:"
        echo -e "  deploy, up   - Deploy production environment (default)"
        echo -e "  build        - Build production Docker images"
        echo -e "  stop, down   - Stop production services"
        echo -e "  clean        - Stop and remove production environment"
        echo -e "  status       - Show service status and URLs"
        echo -e "  logs [svc]   - Show logs (optionally for specific service)"
        echo -e "  restart      - Restart production services"
        echo -e "  help         - Show this help message"
        ;;
        
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "Use '$0 help' for available commands"
        exit 1
        ;;
esac 