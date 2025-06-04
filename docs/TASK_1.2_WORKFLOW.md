# Task 1.2 GitOperationsModule - Workflow & Manual Testing Guide

## 📋 Overview

Task 1.2 implement **GitOperationsModule** cho TEAM Data Acquisition với khả năng clone nông (shallow) Git repositories. Module này được tích hợp vào OrchestratorAgent và cung cấp functionality cốt lõi cho repository management trong RepoChat v1.0.

## 🏗️ Architecture Components

### 1. GitOperationsModule (teams/data_acquisition/git_operations_module.py)
- **Primary Function**: `clone_repository(repository_url, target_path=None)`
- **Secondary Functions**: `cleanup_repository()`, `get_repository_stats()`
- **Validation**: URL format validation cho HTTP/HTTPS/SSH protocols
- **Error Handling**: GitCommandError, PermissionError, OSError
- **Logging**: Comprehensive structured logging với performance metrics

### 2. OrchestratorAgent Integration (orchestrator/orchestrator_agent.py)
- **Initialization**: Tự động setup GitOperationsModule trong `_initialize()`
- **Task Processing**: Clone repository trong `handle_task()` method
- **Error Handling**: Continue processing ngay cả khi clone fails
- **Tracking**: Store repository path trong task info cho future use

### 3. FastAPI Endpoints (main.py)
- **POST /tasks**: Tạo task với repository_url
- **GET /tasks/{id}**: Get task status và repository cloning info
- **GET /stats**: Agent statistics và repository stats
- **GET /health**: Health check với system info

## 🔄 Workflow Description

### 1. Request Flow
```
HTTP Request → FastAPI → OrchestratorAgent → GitOperationsModule → Repository Clone
     ↓                                              ↓
Task Response ← FastAPI ← Task Tracking ← Git Operations ← Validation & Logging
```

### 2. Detailed Steps

1. **HTTP Request**: POST /tasks với repository_url
2. **Validation**: FastAPI validates TaskDefinition structure
3. **Orchestrator**: OrchestratorAgent.handle_task() được gọi
4. **Git Operations**: 
   - URL validation (HTTP/HTTPS/SSH)
   - Unique temp path generation
   - Shallow clone execution (--depth 1)
   - Repository info extraction
   - Performance metrics logging
5. **Task Tracking**: Store repository path, status, timing
6. **Response**: Return execution_id và task status

### 3. Error Handling Flow
```
URL Validation Error → ValueError → 422 HTTP Error
Git Clone Error → GitCommandError → Log error, continue task
Permission Error → PermissionError → Log error, continue task  
Network Error → OSError → Log error, continue task
```

## 🧪 Manual Test Scenarios

### Scenario 1: Successful Public Repository Clone
**Purpose**: Verify basic cloning functionality

```bash
# 1. Start services
docker compose up -d

# 2. Clone public repository
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "https://github.com/octocat/Hello-World.git"}'

# Expected Response:
# {"execution_id": "...", "status": "created", "task_definition": {...}}

# 3. Check task status
curl http://localhost:8000/tasks/{execution_id}

# Expected Result:
# - status: "completed"
# - steps_completed: 3 items
# - repository_path: "/tmp/repochat_Hello-World_..."
# - errors: []
# - Clone timing metrics
```

### Scenario 2: SSH URL Validation
**Purpose**: Test SSH URL format support

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "git@github.com:octocat/Hello-World.git"}'

# Expected Result:
# - URL validation passes
# - Clone may fail due to SSH key, but validation works
# - Error logged in task.errors if clone fails
```

### Scenario 3: Invalid URL Handling
**Purpose**: Test URL validation error handling

```bash
# Test completely invalid URL
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "not-a-valid-url"}'

# Expected Response: 422 Validation Error

# Test unsupported protocol
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "ftp://example.com/repo.git"}'

# Expected Response: 422 Validation Error
```

### Scenario 4: Non-existent Repository
**Purpose**: Test Git clone error handling

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "https://github.com/nonexistent/repo.git"}'

# Expected Result:
# - Task creates successfully
# - Clone fails with GitCommandError
# - Error logged in task.errors
# - Task status: "completed" (task continues despite clone failure)
# - repository_path: null
```

### Scenario 5: Performance & Metrics Testing
**Purpose**: Verify logging và performance tracking

```bash
# 1. Clone multiple repositories
for repo in "octocat/Hello-World" "microsoft/vscode" "facebook/react"; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"repository_url\": \"https://github.com/$repo.git\"}"
  sleep 2
done

# 2. Check agent statistics
curl http://localhost:8000/stats

# Expected Result:
# - total_tasks_handled: 3
# - successful_tasks: 3 (or 2 if vscode too large)
# - Repository cloning metrics trong logs

# 3. Check detailed logs
tail -50 logs/repochat_20250604.log | grep -E "(clone_repository|performance_metric)"

# Expected Log Entries:
# - Function entry/exit logs
# - Clone timing metrics
# - Repository size calculations
# - Performance metrics for each clone operation
```

### Scenario 6: Direct Module Testing
**Purpose**: Test GitOperationsModule trực tiếp

```bash
docker compose exec backend python -c "
from teams.data_acquisition import GitOperationsModule
import json

# Initialize module
git_ops = GitOperationsModule()
print('GitOperationsModule initialized')

# Clone repository
result = git_ops.clone_repository('https://github.com/octocat/Hello-World.git')
print(f'Clone result: {result}')

# Get repository stats
stats = git_ops.get_repository_stats()
print(f'Repository stats: {json.dumps(stats, indent=2)}')

# Cleanup
if result:
    cleanup_result = git_ops.cleanup_repository(result)
    print(f'Cleanup successful: {cleanup_result}')

print('Direct testing completed')
"
```

### Scenario 7: Logging Verification
**Purpose**: Verify structured logging functionality

```bash
# 1. Trigger clone operation
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "https://github.com/octocat/Hello-World.git"}'

# 2. Check structured JSON logs
tail -20 logs/repochat_20250604.log | jq '.'

# Expected Log Structure:
# - timestamp
# - level (INFO/DEBUG/ERROR)
# - logger (repochat.data_acquisition.git_operations)
# - module/function/line
# - message
# - process_id/thread_id
# - extra_data với detailed context

# 3. Check performance metrics
grep "performance_metric" logs/repochat_20250604.log | tail -5 | jq '.extra'

# Expected Metrics:
# - repository_clone_time (ms)
# - task_handling_time (ms)
# - Context data với repository_url, clone_size_mb
```

## ✅ Success Criteria Checklist

### Basic Functionality
- [ ] Public repository clone thành công
- [ ] Shallow clone (--depth 1) được sử dụng
- [ ] Unique temporary paths được generate
- [ ] Repository info extraction hoạt động
- [ ] Cleanup functionality hoạt động

### Error Handling
- [ ] Invalid URLs rejected với proper validation
- [ ] Git clone errors logged và handled gracefully
- [ ] Task processing continues sau clone failures
- [ ] Proper HTTP status codes returned

### Integration
- [ ] OrchestratorAgent integration hoạt động
- [ ] FastAPI endpoints respond correctly
- [ ] Task tracking với repository information
- [ ] Agent statistics update properly

### Logging & Monitoring
- [ ] Structured JSON logs generated
- [ ] Performance metrics captured
- [ ] Function entry/exit tracking
- [ ] Error details logged với context
- [ ] Repository statistics available

### Performance
- [ ] Clone operations complete trong reasonable time
- [ ] Memory usage stable during operations
- [ ] Temporary directories cleaned up properly
- [ ] Concurrent operations handled correctly

## 📊 Expected Performance Benchmarks

- **Small Repository (Hello-World)**: < 2 seconds clone time
- **Medium Repository**: < 10 seconds clone time  
- **Memory Usage**: < 100MB additional per clone operation
- **Concurrent Tasks**: Support multiple simultaneous clones
- [ ] Error Rate: < 1% for valid public repositories

## 🛠️ Troubleshooting Common Issues

### Issue 1: Clone Timeout
**Symptoms**: GitCommandError với timeout message
**Solution**: Check network connectivity, try smaller repository

### Issue 2: Permission Denied
**Symptoms**: PermissionError trong logs
**Solution**: Check container permissions, verify temp directory access

### Issue 3: SSH Key Issues
**Symptoms**: SSH authentication failure
**Solution**: Expected behavior cho SSH URLs without keys, check error logging

### Issue 4: Large Repository Clone
**Symptoms**: Very slow clone times
**Solution**: Shallow clone should mitigate, consider repository size limits

---

**Document Version**: 1.0  
**Last Updated**: 6/6/2025  
**Implementation Status**: ✅ COMPLETED với 25/25 unit tests PASSING 