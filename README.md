# 🤖 RepoChat v1.0 - AI Repository Analysis Assistant

**Docker-First Development** | **Enhanced Logging** | **Multi-Agent Architecture**

RepoChat là một trợ lý AI thông minh được thiết kế để phân tích repository code một cách sâu sắc và hiệu quả, hoạt động như một "đồng đội ảo" cho developers.

## 🌟 Key Features

- 🏗️ **Multi-Agent Architecture** - Kiến trúc đa agent với coordination thông minh
- 🔍 **Code Knowledge Graph** - Xây dựng knowledge graph từ source code
- 🤖 **AI-Powered Analysis** - Sử dụng LLM cho code analysis và insights
- 📊 **Comprehensive Logging** - Structured logging với JSON format cho debugging
- 🐳 **Docker-First Development** - Complete development environment trong 1 command
- 🚀 **Production Ready** - Multi-stage builds với security best practices

## 🚀 Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose
- Git
- 8GB+ RAM recommended

### One-Command Setup

```bash
# Clone repository
git clone <repository-url>
cd repochat

# Setup và start development environment
./scripts/setup-dev.sh

# ✅ Tất cả services sẽ được setup tự động:
# - Neo4j database (localhost:7474)
# - Backend API (localhost:8000) 
# - Health checks và testing
```

### Verify Installation

```bash
# Check services
docker-compose ps

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/

# Access Neo4j Browser
open http://localhost:7474
# Username: neo4j, Password: repochat123
```

## 🏗️ Architecture Overview

### Multi-Agent System

```
🎯 OrchestratorAgent (Central Coordinator)
├── 📦 DataAcquisitionAgent (Git & File Analysis)
├── 🧠 CKGOperationsAgent (Knowledge Graph) 
├── 🔍 CodeAnalysisAgents (Language-specific)
├── 🤖 SynthesisAgent (AI Integration)
└── 💭 ConversationAgent (Memory & Context)
```

### Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Database**: Neo4j (Graph Database)
- **AI/ML**: OpenAI GPT, LangChain, LangGraph
- **Development**: Docker Compose, pytest
- **Monitoring**: Structured logging, health checks

## 🛠️ Development Workflow

### Daily Development

```bash
# Start all services
docker-compose up -d

# Monitor logs
docker-compose logs -f backend

# Hot reload enabled - edit code và changes sẽ tự động reflect

# Run tests
docker-compose exec backend python -m pytest tests/ -v

# Stop services
docker-compose down
```

### API Testing

```bash
# Create analysis task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "https://github.com/example/repo"}'

# Check task status
curl http://localhost:8000/tasks/{execution_id}

# Get system statistics
curl http://localhost:8000/stats
```

### Debugging

```bash
# Container shell access
docker-compose exec backend bash

# VS Code debugging (port 5678)
# Set breakpoints và attach to remote debugger

# Structured log analysis
tail -f logs/repochat_debug_*.log | jq .
```

## 📊 Monitoring & Logging

### Enhanced Logging System

- **Structured JSON Logs**: Machine-readable format
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Performance Metrics**: Execution time tracking
- **Context Enrichment**: Agent ID, function names, metadata
- **Log Rotation**: Automatic với size-based rotation

### Log Analysis

```bash
# View real-time structured logs
docker-compose logs -f backend | jq .

# Filter errors only
cat logs/repochat_debug_*.log | jq 'select(.level=="ERROR")'

# Performance monitoring
cat logs/repochat_debug_*.log | jq 'select(.event_type=="performance_metric")'

# Function execution tracking
cat logs/repochat_debug_*.log | jq 'select(.event_type=="function_entry" or .event_type=="function_exit")'
```

### Health Monitoring

```bash
# Service health
curl http://localhost:8000/health

# Detailed statistics
curl http://localhost:8000/stats

# Docker metrics
docker stats
```

## 🧪 Testing

### Automated Testing

```bash
# Run all tests
docker-compose exec backend python -m pytest tests/ -v

# Coverage report
docker-compose exec backend python -m pytest tests/ --cov=src --cov-report=html

# Test specific component
docker-compose exec backend python -m pytest tests/test_orchestrator.py -v
```

### Manual Testing Scenarios

1. **Service Health**: All endpoints responsive
2. **Task Creation**: Repository analysis workflow
3. **Error Handling**: Invalid inputs và network issues
4. **Performance**: Response times và resource usage
5. **Logging**: Structured logs với proper format

## 📁 Project Structure

```
repochat/
├── 📋 DESIGN.md                 # Architecture documentation
├── 📝 TASK.md                   # Development progress
├── 🐳 docker-compose.yml        # Development environment
├── 🌍 env.example               # Environment template
├── 🔧 scripts/setup-dev.sh      # Automated setup
├── 📚 docs/                     # Documentation
│   └── DOCKER_DEVELOPMENT.md    # Docker guide
├── ⚙️  backend/                 # Python backend
│   ├── 🐳 Dockerfile            # Multi-stage build
│   ├── 🚀 main.py               # FastAPI application
│   ├── 📦 requirements.txt      # Dependencies
│   └── 🎯 src/                  # Source code
│       ├── orchestrator/        # Central coordinator
│       ├── teams/              # Agent teams
│       └── shared/             # Common utilities
└── 🧪 tests/                   # Test suite
```

## 🎯 Current Status (Phase 1)

### ✅ Completed - Task 1.1 Enhanced

- ✅ **Docker Development Environment**: Complete setup với 1 command
- ✅ **Enhanced Logging**: Structured logging với performance tracking
- ✅ **OrchestratorAgent**: Central coordination với comprehensive monitoring
- ✅ **FastAPI Application**: Production-ready với health checks
- ✅ **Testing Framework**: Automated testing với Docker integration
- ✅ **Documentation**: Complete setup và development guides

### 🔄 Next Phase - Task 1.2

- 🔜 **DataAcquisitionAgent**: Git repository cloning và analysis
- 🔜 **Language Detection**: Multi-language support
- 🔜 **File System Analysis**: Repository structure mapping
- 🔜 **Integration Testing**: End-to-end workflow testing

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (với defaults)
LOG_LEVEL=DEBUG
ENVIRONMENT=development
NEO4J_URI=bolt://neo4j:7687
BACKEND_PORT=8000
DEBUG_PORT=5678
```

### Custom Configuration

```bash
# Override default settings
cp env.example .env
# Edit .env với your settings

# Restart services
docker-compose restart backend
```

## 🚨 Troubleshooting

### Common Issues

```bash
# Port conflicts
lsof -i :8000
export BACKEND_PORT=8080

# Docker issues  
docker system prune -f
docker-compose build --no-cache

# Log permission issues
sudo chown -R $USER:$USER logs/

# Complete reset
docker-compose down -v --remove-orphans
./scripts/setup-dev.sh
```

### Debug Checklist

1. ✅ `docker-compose ps` - All services running
2. ✅ `curl http://localhost:8000/health` - API responsive  
3. ✅ `docker-compose logs backend` - No errors
4. ✅ Neo4j accessible at `http://localhost:7474`
5. ✅ Logs being written to `./logs/` directory

## 📚 Documentation

- 📋 [**DESIGN.md**](DESIGN.md) - Architecture và system design
- 📝 [**TASK.md**](TASK.md) - Development progress tracking
- 🐳 [**Docker Development Guide**](docs/DOCKER_DEVELOPMENT.md) - Detailed Docker workflow
- 🧪 **Testing Guide** - Testing strategies và best practices (TBD)

## 🤝 Contributing

### Development Setup

1. Fork repository
2. Run `./scripts/setup-dev.sh`
3. Create feature branch
4. Make changes với hot reload
5. Run tests: `docker-compose exec backend python -m pytest tests/ -v`
6. Submit pull request

### Coding Standards

- **Python**: PEP8, type hints, docstrings
- **Testing**: pytest với coverage > 80%
- **Logging**: Structured logging với context
- **Docker**: Multi-stage builds, health checks
- **Documentation**: Comprehensive documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- **LangChain/LangGraph**: Multi-agent orchestration
- **Neo4j**: Graph database technology  
- **FastAPI**: Modern Python web framework
- **Docker**: Containerization platform

---

**🚀 Ready to start? Run `./scripts/setup-dev.sh` và explore the API at `http://localhost:8000/docs`**
