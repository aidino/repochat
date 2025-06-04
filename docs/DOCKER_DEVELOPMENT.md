# RepoChat Docker Development Guide

Hướng dẫn chi tiết về môi trường phát triển Docker cho RepoChat v1.0

## 📋 Tổng quan

RepoChat sử dụng Docker Compose làm công cụ phát triển chính để đảm bảo môi trường nhất quán và dễ dàng setup. Hệ thống bao gồm:

- **Backend**: Python FastAPI application với debugging support
- **Neo4j**: Graph database cho Code Knowledge Graph
- **Frontend**: Vue.js application (Phase 5)

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Kiểm tra Docker và Docker Compose
docker --version
docker-compose --version

# Đảm bảo Docker daemon đang chạy
docker info
```

### 2. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd repochat

# Run automated setup
./scripts/setup-dev.sh
```

**Script sẽ tự động:**
- ✅ Kiểm tra Docker installation
- ✅ Tạo `.env` file từ `env.example`
- ✅ Tạo các thư mục cần thiết (`logs/`, `temp/`, `data/`)
- ✅ Build Docker images
- ✅ Start services và wait for health checks
- ✅ Run tests để verify setup

### 3. Verify Installation

```bash
# Kiểm tra services đang chạy
docker-compose ps

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

## 🏗️ Architecture Overview

### Services

```yaml
services:
  neo4j:       # Graph database
    ports: 7474 (browser), 7687 (bolt)
    
  backend:     # Python FastAPI
    ports: 8000 (API), 5678 (debug)
    
  frontend:    # Vue.js (future)
    ports: 3000
```

### Networking

```
repochat-network (172.20.0.0/16)
├── neo4j:7687 (database)
├── backend:8000 (API)
└── frontend:3000 (UI)
```

### Data Persistence

```
volumes:
  neo4j_data:/     # Database persistence
  logs:/           # Application logs  
  temp:/           # Temporary files
  data/:/          # Application data
```

## 🛠️ Development Workflow

### Daily Development

```bash
# Start services
docker-compose up -d

# View logs (real-time)
docker-compose logs -f backend
docker-compose logs -f neo4j

# Stop services
docker-compose down
```

### Code Development

```bash
# Code changes được hot-reload tự động
# Edit files trong ./backend/src/

# Restart specific service
docker-compose restart backend

# Rebuild after dependency changes
docker-compose build backend
docker-compose up -d backend
```

### Testing

```bash
# Run all tests
docker-compose exec backend python -m pytest tests/ -v

# Run specific test file
docker-compose exec backend python -m pytest tests/test_orchestrator.py -v

# Run with coverage
docker-compose exec backend python -m pytest tests/ --cov=src --cov-report=html
```

### Debugging

```bash
# Method 1: Container shell access
docker-compose exec backend bash
cd /app
python -c "from src.orchestrator.orchestrator_agent import OrchestratorAgent; agent = OrchestratorAgent(); print('Debug ready')"

# Method 2: VS Code Debug (Port 5678)
# 1. Set breakpoints in VS Code
# 2. Attach to Remote Debug (localhost:5678)
# 3. Trigger API calls

# Method 3: Logs inspection
tail -f logs/repochat_debug_*.log
```

## 📊 Monitoring & Health Checks

### Health Endpoints

```bash
# Application health
curl http://localhost:8000/health

# System statistics  
curl http://localhost:8000/stats

# Neo4j browser
open http://localhost:7474
# Username: neo4j, Password: repochat123
```

### Log Files

```bash
# Log structure
logs/
├── repochat_YYYYMMDD.log      # Main application logs
└── repochat_debug_YYYYMMDD.log # Debug logs với full details

# View structured logs
cat logs/repochat_debug_*.log | jq .

# Filter by log level
cat logs/repochat_debug_*.log | jq 'select(.level=="ERROR")'

# Monitor specific component
cat logs/repochat_debug_*.log | jq 'select(.logger | contains("orchestrator"))'
```

### Performance Monitoring

```bash
# Docker stats
docker stats

# Service resource usage
docker-compose exec backend ps aux
docker-compose exec backend df -h

# Neo4j monitoring
docker-compose exec neo4j cypher-shell -u neo4j -p repochat123 "CALL dbms.queryJmx('*:*')"
```

## 🔧 Configuration

### Environment Variables

File: `.env`
```bash
# Essential configuration
OPENAI_API_KEY=your_api_key_here
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j  
NEO4J_PASSWORD=repochat123

# Ports
BACKEND_PORT=8000
DEBUG_PORT=5678
NEO4J_BROWSER_PORT=7474
```

### Custom Configuration

```bash
# Override default ports
export BACKEND_PORT=8080
docker-compose up -d

# Change log level
export LOG_LEVEL=INFO
docker-compose restart backend

# Use external Neo4j
export NEO4J_URI=bolt://external-neo4j:7687
docker-compose up -d backend
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Error: Port 8000 already in use
lsof -i :8000
kill -9 <PID>

# Or use different port
export BACKEND_PORT=8080
docker-compose up -d
```

#### 2. Docker Build Issues
```bash
# Clear Docker cache
docker system prune -f
docker-compose build --no-cache backend

# Remove old containers
docker-compose down --remove-orphans
docker-compose up -d
```

#### 3. Neo4j Connection Issues
```bash
# Check Neo4j logs
docker-compose logs neo4j

# Verify health
docker-compose exec neo4j cypher-shell -u neo4j -p repochat123 "RETURN 1"

# Reset Neo4j data
docker-compose down -v
docker-compose up -d neo4j
```

#### 4. Log Permission Issues
```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/
chmod 755 logs/
```

### Debug Checklist

```bash
# 1. Check service status
docker-compose ps

# 2. Check health endpoints  
curl http://localhost:8000/health

# 3. Check logs for errors
docker-compose logs backend | grep ERROR

# 4. Verify environment
docker-compose exec backend env | grep -E "(LOG_LEVEL|NEO4J|ENVIRONMENT)"

# 5. Test database connection
docker-compose exec backend python -c "
import os; 
print('NEO4J_URI:', os.getenv('NEO4J_URI')); 
from neo4j import GraphDatabase;
driver = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=('neo4j', 'repochat123'));
driver.verify_connectivity();
print('Neo4j connection: OK')
"
```

## 🎯 Best Practices

### Development

1. **Always use Docker**: Đừng run directly trên host machine
2. **Monitor logs**: Luôn có terminal với `docker-compose logs -f`
3. **Regular cleanup**: `docker system prune -f` weekly
4. **Test early**: Run tests sau mỗi major change
5. **Environment consistency**: Sử dụng `.env` file

### Debugging

1. **Structured logging**: Sử dụng log levels phù hợp
2. **Debug ports**: VS Code debugging qua port 5678
3. **Container access**: `docker-compose exec backend bash` for investigation
4. **Health checks**: Regular health endpoint monitoring

### Performance

1. **Volume mounts**: Tận dụng bind mounts cho hot reload
2. **Resource limits**: Monitor container resource usage
3. **Log rotation**: Logs được rotate tự động 
4. **Database indexing**: Monitor Neo4j performance

## 📚 Additional Resources

### Useful Commands

```bash
# Complete cleanup và restart
docker-compose down -v --remove-orphans
docker system prune -f
./scripts/setup-dev.sh

# Database backup/restore
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/backup.dump
docker-compose exec neo4j neo4j-admin load --from=/tmp/backup.dump --database=neo4j

# Performance profiling
docker-compose exec backend python -m cProfile -o profile.stats -c "
from src.orchestrator.orchestrator_agent import OrchestratorAgent;
agent = OrchestratorAgent()
"
```

### VS Code Configuration

File: `.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to RepoChat Backend",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/backend",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

### Docker Compose Overrides

File: `docker-compose.override.yml` (optional)
```yaml
version: '3.8'
services:
  backend:
    environment:
      - LOG_LEVEL=DEBUG
      - CUSTOM_SETTING=value
    volumes:
      - ./custom_configs:/app/configs
```

---

**📝 Note**: Môi trường development này được thiết kế cho Phase 1 của RepoChat. Các phase sau sẽ có thêm services và configuration options. 