# RepoChat v1.0 - Phase 1 Testing Guide

## 🧪 Overview

Tài liệu này cung cấp hướng dẫn chi tiết để test và validate Phase 1 của RepoChat v1.0. Phase 1 bao gồm tất cả các component của TEAM Data Acquisition và workflow scan project cơ bản.

## 📋 Test Categories

### 1. Unit Tests
- **Location**: `tests/test_*.py`
- **Coverage**: 100+ test cases covering all modules
- **Command**: `python -m pytest tests/ -v`

### 2. Integration Tests
- **Location**: `tests/integration_test_phase_1.py`
- **Coverage**: End-to-end workflow validation
- **Command**: `python tests/integration_test_phase_1.py`

### 3. Manual Tests
- **Location**: `TASK.md` - Section "MANUAL TEST SCENARIOS - PHASE 1"
- **Coverage**: Real-world scenarios và user workflows
- **Format**: Step-by-step procedures với expected outputs

## 🚀 Quick Start Testing

### Prerequisites
```bash
# Check Python version
python --version  # Should be 3.8+

# Check Git installation
git --version

# Check internet connectivity
ping github.com
```

### Setup Environment
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# 4. Create logs directory
mkdir -p logs
```

### Run All Tests
```bash
# 1. Run unit tests
python -m pytest tests/ -v --tb=short

# 2. Run integration tests
python tests/integration_test_phase_1.py

# 3. Run manual validation (see TASK.md for details)
```

## 📊 Test Results Interpretation

### Unit Test Results
```bash
# Expected output format:
tests/test_data_preparation_module.py::TestDataPreparationModule::test_create_project_context_success PASSED
tests/test_git_operations_module.py::TestGitOperationsModule::test_clone_repository_success PASSED
tests/test_language_identifier_module.py::TestLanguageIdentifierModule::test_identify_languages_success PASSED
tests/test_orchestrator_agent.py::TestOrchestratorAgent::test_handle_scan_project_task_success PASSED
tests/test_pat_handler_module.py::TestPATHandlerModule::test_request_pat_if_needed_public_repo PASSED

====================== X passed in Y.YYs ======================
```

### Integration Test Results
```bash
# Expected output format:
🧪 TEST 1: Public Repository Scan (Task 1.5)
✅ Test 1 PASSED

🧪 TEST 2: PAT Handler Module (Task 1.6) 
✅ Test 2 PASSED

🧪 TEST 3: Private Repository Simulation
✅ Test 3 PASSED

🧪 TEST 4: Error Handling
✅ Test 4 PASSED

🧪 TEST 5: Component Integration
✅ Test 5 PASSED

🏁 INTEGRATION TEST RESULTS
✅ Passed: 5
❌ Failed: 0
📊 Total: 5
```

## 🔍 Common Issues & Solutions

### Issue 1: Import Errors
**Symptoms**: `ModuleNotFoundError: No module named 'src'`
**Solution**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
# Or run from backend directory with: python -m pytest
```

### Issue 2: Git Clone Timeouts
**Symptoms**: Clone operations hang or timeout
**Solution**:
```bash
# Check network connectivity
curl -I https://github.com
# Use smaller test repositories
# Check firewall settings
```

### Issue 3: Permission Errors
**Symptoms**: `PermissionError: [Errno 13] Permission denied`
**Solution**:
```bash
# Ensure logs directory is writable
chmod 755 logs/
# Check temp directory permissions
ls -la /tmp/
```

### Issue 4: Missing Dependencies
**Symptoms**: Import errors for external libraries
**Solution**:
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
# Check pip version
pip --version
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

| Test Scenario | Expected Time | Acceptable Range |
|--------------|---------------|------------------|
| Unit Tests Complete | <30 seconds | 10-60 seconds |
| Integration Tests | <5 minutes | 2-10 minutes |
| Small Repo Clone | <10 seconds | 5-30 seconds |
| Language Detection | <5 seconds | 1-15 seconds |
| Full Scan Workflow | <30 seconds | 15-120 seconds |

### Performance Monitoring
```bash
# Monitor test execution time
time python -m pytest tests/ -v

# Monitor memory usage during testing
# Use system monitoring tools like htop, Activity Monitor, etc.

# Check log file sizes
ls -lh logs/
```

## 🎯 Success Criteria

### Phase 1 Test Validation Checklist

- [ ] **Unit Tests**: All tests pass (>95% success rate)
- [ ] **Integration Tests**: All 5 scenarios pass
- [ ] **Manual Tests**: All 8 manual test scenarios validated
- [ ] **Performance**: Meets timing benchmarks
- [ ] **Logging**: Structured logs generated correctly
- [ ] **Security**: PAT handling secure (no persistence)
- [ ] **Error Handling**: Graceful degradation verified
- [ ] **Cleanup**: No temp files or directories left behind

### Ready for Phase 2 Criteria

✅ **Foundation Solid**: All core components working  
✅ **Data Flow**: TaskDefinition → ProjectDataContext pipeline complete  
✅ **Quality Assurance**: Comprehensive test coverage achieved  
✅ **Documentation**: Test procedures documented và validated  
✅ **Architecture**: Clean separation ready for CKG integration  

## 📞 Support & Troubleshooting

### Debug Mode
```bash
# Enable debug logging
export REPOCHAT_LOG_LEVEL=DEBUG

# Run with verbose output
python -m pytest tests/ -v -s

# Check detailed logs
tail -f logs/repochat_debug_$(date +%Y%m%d).log
```

### Log Analysis
```bash
# Search for errors
grep -i error logs/repochat_*.log

# Check performance metrics
grep "execution_time" logs/repochat_*.log

# Analyze module interactions
grep "log_function_entry\|log_function_exit" logs/repochat_debug_*.log
```

### Clean Test Environment
```bash
# Remove all temp files
rm -rf logs/*.log
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "repochat_*" -type d -exec rm -rf {} + 2>/dev/null || true

# Restart with clean slate
mkdir -p logs
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-06-05  
**Phase**: 1 - TEAM Data Acquisition  
**Status**: Production Ready ✅ 