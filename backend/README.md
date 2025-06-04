# RepoChat Backend

Backend service cho RepoChat v1.0 - AI-powered repository analysis và code review assistant.

## Quick Start

### 🚀 Recommended: Using Docker (Production Ready)

```bash
# 1. Clone repository và navigate to project root
cd /path/to/repochat

# 2. Start the complete environment
docker compose up -d

# 3. Verify services are running
docker compose ps

# 4. Test the API
curl http://localhost:8000/health
```

### 🛠️ Development Setup

```bash
# 1. Setup development environment (one command)
./scripts/setup-dev.sh

# 2. Access backend container for development
docker compose exec backend bash

# 3. Run tests
docker compose exec backend python -m pytest tests/ -v
```

## Running the Application

### ❌ INCORRECT (Common Error)
```bash
# DON'T do this - will cause "No such file or directory" error
python backend/src/main.py
```

### ✅ CORRECT Ways to Run

#### Option 1: Docker Compose (Recommended)
```bash
cd /path/to/repochat
docker compose up -d
# Application will be available at http://localhost:8000
```

#### Option 2: Direct Docker Run
```bash
cd /path/to/repochat
docker compose exec backend python main.py
```

#### Option 3: Local Development (if not using Docker)
```bash
cd /path/to/repochat/backend
python main.py
# Note: Requires Neo4j running locally on port 7687
```

## API Endpoints

- **Health Check**: `GET http://localhost:8000/health`
- **Root Info**: `GET http://localhost:8000/`
- **Create Task**: `POST http://localhost:8000/tasks`
- **Task Status**: `GET http://localhost:8000/tasks/{execution_id}`
- **Agent Stats**: `GET http://localhost:8000/stats`

## Testing

### Unit Tests
```bash
# Run all tests
docker compose exec backend python -m pytest tests/ -v

# Run specific test modules
docker compose exec backend python -m pytest tests/test_language_identifier_module.py -v
docker compose exec backend python -m pytest tests/test_git_operations_module.py -v
docker compose exec backend python -m pytest tests/test_orchestrator_agent.py -v
```

### Integration Tests
```bash
# Test Task 1.3 - LanguageIdentifierModule integration
docker compose exec backend python test_task_1_3_integration.py
```

### Manual Testing
```bash
# Test language detection với real repositories
docker compose exec backend python -c "
from src.teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from src.teams.data_acquisition.git_operations_module import GitOperationsModule
git = GitOperationsModule()
lang = LanguageIdentifierModule()
path = git.clone_repository('https://github.com/flutter/flutter.git')
languages = lang.identify_languages(path)
print(f'Detected languages: {languages}')
git.cleanup_repository(path)
"
```

## File Structure

```
backend/
├── main.py                 # ✅ FastAPI application entry point
├── src/                    # Source code
│   ├── orchestrator/       # Central coordination
│   ├── teams/              # TEAM agents
│   │   ├── data_acquisition/    # Git operations, language detection
│   │   ├── ckg_operations/      # Code Knowledge Graph
│   │   ├── code_analysis/       # Code analysis algorithms
│   │   ├── llm_services/        # LLM integration
│   │   ├── interaction_tasking/ # User interaction
│   │   └── synthesis_reporting/ # Report generation
│   └── shared/             # Shared utilities and models
├── tests/                  # Test suite
├── logs/                   # Application logs
└── temp/                   # Temporary files (git clones, etc.)
```

## Current Status

### ✅ Completed Tasks (Phase 1)
- **Task 1.1**: Orchestrator Agent initialization với enhanced logging
- **Task 1.2**: GitOperationsModule với comprehensive Git operations  
- **Task 1.3**: LanguageIdentifierModule với advanced language detection

### 🔄 Next Tasks
- **Task 1.4**: DataPreparationModule và ProjectDataContext
- **Task 1.5**: Enhanced task processing workflow
- **Task 1.6**: PAT (Personal Access Token) handler

## Troubleshooting

### Common Issues

1. **"No such file or directory" error**
   - ❌ Don't run: `python backend/src/main.py`
   - ✅ Use Docker: `docker compose up -d`
   - ✅ Or correct path: `cd backend && python main.py`

2. **Container not starting**
   ```bash
   docker compose logs backend
   docker compose logs neo4j
   ```

3. **Port conflicts**
   ```bash
   # Check if ports 8000, 7474, 7687 are available
   lsof -i :8000
   lsof -i :7474  
   lsof -i :7687
   ```

## Logging

Logs are written to:
- `logs/repochat_YYYYMMDD.log` - General application logs
- `logs/repochat_debug_YYYYMMDD.log` - Debug logs with detailed information

```bash
# View live logs
tail -f logs/repochat_20250604.log

# View debug logs
tail -f logs/repochat_debug_20250604.log
```

## Development

### Code Style
- Python 3.11+
- Black formatting
- Type hints required
- Pydantic for data validation
- Comprehensive logging
- Unit tests for all new features

### Git Workflow
```bash
# After completing a task
git add .
git commit -m "Task X.Y: Description of completed work"
git push
``` 