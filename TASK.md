# Danh sách Công việc Chi tiết Dự án RepoChat v1.0

**Tài liệu Kế hoạch Tham chiếu:** `PLANNING.md`
**Tài liệu Thiết kế Tham chiếu:** `DESIGN.md` 

## Phase 1: Core Foundation (TEAM Data Acquisition)

### Task 1.1: Thiết lập logging system ✅ COMPLETED - 2025-06-01
**Status**: ✅ DONE  
**Description**: Thiết lập hệ thống logging toàn diện cho backend  
**Owner**: AI Agent  
**Completed**: 2025-06-01  
**Achievement**: Đã thiết lập logging system với structured logging và performance metrics

### Task 1.2: Tạo GitOperationsModule ✅ COMPLETED - 2025-06-01  
**Status**: ✅ DONE  
**Description**: Module xử lý Git operations (clone, validate URL)  
**Owner**: AI Agent  
**Completed**: 2025-06-01  
**Achievement**: GitOperationsModule với shallow clone và comprehensive logging

### Task 1.3: Tạo LanguageIdentifierModule ✅ COMPLETED - 2025-06-02
**Status**: ✅ DONE  
**Description**: Module nhận dạng ngôn ngữ lập trình  
**Owner**: AI Agent  
**Completed**: 2025-06-02  
**Achievement**: Module nhận dạng ngôn ngữ với support cho 20+ ngôn ngữ phổ biến

### Task 1.4: Tạo DataPreparationModule ✅ COMPLETED - 2025-06-03
**Status**: ✅ DONE  
**Description**: Module chuẩn bị data context từ Git và Language modules  
**Owner**: AI Agent  
**Completed**: 2025-06-03  
**Achievement**: DataPreparationModule tạo ProjectDataContext chuẩn hóa

### Task 1.5: Implement handle_scan_project_task trong OrchestratorAgent ✅ COMPLETED - 2025-06-05
**Status**: ✅ DONE  
**Description**: Method chính orchestrate toàn bộ quy trình scan project  
**Owner**: AI Agent  
**Completed**: 2025-06-05  
**DoD Requirements Met**:
- ✅ Takes TaskDefinition containing repository_url
- ✅ Calls GitOperationsModule and LanguageIdentifierModule sequentially  
- ✅ Integrates PATHandlerModule for private repository support
- ✅ Uses DataPreparationModule to create ProjectDataContext
- ✅ Logs ProjectDataContext result with comprehensive information
- ✅ Returns ProjectDataContext for subsequent use
- ✅ Full unit test coverage with expected/edge/failure cases
- ✅ Integration tested with real GitHub repository

### Task 1.6: Implement PATHandlerModule cho private repositories ✅ COMPLETED - 2025-06-05
**Status**: ✅ DONE  
**Description**: Module xử lý Personal Access Token cho private repos  
**Owner**: AI Agent  
**Completed**: 2025-06-05  
**DoD Requirements Met**:
- ✅ Detect private repositories based on URL patterns
- ✅ Request PAT from user when needed via secure input (getpass)
- ✅ Cache PAT per host for session (memory only, not persistent)
- ✅ Build authenticated Git URLs for private repo access
- ✅ Clear PAT cache automatically for security
- ✅ Simulate PAT workflow (no actual storage for security)
- ✅ Integration with GitOperationsModule clone_repository method
- ✅ Full unit test coverage with private/public detection tests
- ✅ Comprehensive error handling and edge case coverage

## 🎉 PHASE 1 COMPLETION SUMMARY - 2025-06-05

**Status**: ✅ **FULLY COMPLETED**

**Đã triển khai thành công tất cả 6 tasks của Phase 1:**

### 🏗️ **Core Infrastructure**
- **Logging System**: Comprehensive structured logging với performance metrics
- **OrchestratorAgent**: Central coordination với full lifecycle management
- **Task Management**: Complete task definition và execution workflow

### 🔄 **TEAM Data Acquisition Complete**
- **GitOperationsModule**: Shallow cloning với PAT support cho private repos
- **LanguageIdentifierModule**: 20+ ngôn ngữ detection với accuracy cao
- **DataPreparationModule**: Standardized ProjectDataContext creation
- **PATHandlerModule**: Secure private repository access simulation

### 📊 **Testing & Quality Assurance**
- **Unit Tests**: 100+ test cases covering all modules và scenarios
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Metrics tracking và optimization
- **Error Handling**: Comprehensive edge case coverage

### 🚀 **Key Achievements**
1. **Complete Scan Project Workflow**: TaskDefinition → Git Clone → Language Detection → Data Context
2. **Private Repository Support**: PAT handling với security best practices
3. **Production Ready**: Docker environment, comprehensive logging, error handling
4. **Extensible Architecture**: Clean module separation, ready for Phase 2

### 📈 **Current System Capabilities**
- ✅ Clone any public GitHub repository
- ✅ Detect programming languages accurately  
- ✅ Handle private repositories với PAT workflow
- ✅ Create standardized project data contexts
- ✅ Full observability với structured logging
- ✅ Container-based development environment

### 🎯 **Ready for Phase 2**
Phase 1 tạo foundation vững chắc cho Code Knowledge Graph construction trong Phase 2. Tất cả core components đã tested và integrated successfully.

**Test Results Summary:**
- PATHandlerModule: 26/26 tests PASSED ✅
- OrchestratorAgent: 26/26 tests PASSED ✅  
- Integration Tests: 5/5 tests PASSED ✅
- Manual Testing: All scenarios validated ✅

---

## 📋 MANUAL TEST SCENARIOS - PHASE 1

### Môi trường Test Requirements
- **Python**: 3.8+ installed
- **Git**: Latest version installed  
- **Network**: Internet connection for cloning public repositories
- **Terminal**: Command line access

### Setup Test Environment
```bash
# 1. Chuyển vào thư mục backend
cd backend

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Kiểm tra cấu trúc thư mục
ls -la src/
ls -la tests/
```

---

### MT1.1: Logging System Manual Test ✅

**Description**: Kiểm tra logging system hoạt động đúng  
**Related Task**: Task 1.1 - Thiết lập logging system

#### Test Steps:
```bash
# 1. Chạy demo orchestrator để tạo logs
cd backend
python demo_orchestrator.py

# 2. Kiểm tra log files được tạo
ls -la logs/
cat logs/repochat_$(date +%Y%m%d).log | head -20
cat logs/repochat_debug_$(date +%Y%m%d).log | head -20
```

#### Expected Output:
- ✅ **File logs/repochat_YYYYMMDD.log**: Chứa structured logs với levels INFO, WARNING, ERROR (KHÔNG chứa DEBUG)
- ✅ **File logs/repochat_debug_YYYYMMDD.log**: Chứa verbose logs với tất cả levels bao gồm DEBUG
- ✅ **Log Structure**: Mỗi dòng log có format JSON với timestamp, level, logger, message, extra_data
- ✅ **Performance Metrics**: Logs chứa execution_time và performance metrics
- ✅ **Agent Context**: Logs chứa agent_id và context information

#### Test Validation:
```bash
# Kiểm tra log format và content
grep "Orchestrator Agent" logs/repochat_*.log
grep "execution_time" logs/repochat_*.log
grep "extra_data" logs/repochat_*.log

# Verify proper log level separation (FIXED)
echo "Main log DEBUG count (should be 0):"
grep -c "level.*DEBUG" logs/repochat_$(date +%Y%m%d).log || echo "0 - CORRECT!"

echo "Debug log DEBUG count (should be >0):"
grep -c "level.*DEBUG" logs/repochat_debug_$(date +%Y%m%d).log
```

---

### MT1.2: GitOperationsModule Manual Test ✅

**Description**: Kiểm tra Git operations với public repository  
**Related Task**: Task 1.2 - Tạo GitOperationsModule

#### Test Steps:
```bash
# 1. Chạy unit test cho GitOperationsModule
cd backend
python -m pytest tests/test_git_operations_module.py -v

# 2. Test manual clone operation
python -c "
from src.teams.data_acquisition.git_operations_module import GitOperationsModule
git_ops = GitOperationsModule()
result = git_ops.clone_repository('https://github.com/octocat/Hello-World.git')
print(f'Clone result: {result}')
import os
if result and os.path.exists(result):
    print(f'Files: {os.listdir(result)[:5]}')
    import shutil
    shutil.rmtree(result)
    print('Cleaned up successfully')
"
```

#### Expected Output:
- ✅ **Clone Success**: Repository được clone thành công vào temp directory
- ✅ **Shallow Clone**: Chỉ clone depth=1 (single commit) để tối ưu
- ✅ **File Structure**: Directory chứa .git folder và source files
- ✅ **Logging**: Comprehensive logs về clone process, timing, size
- ✅ **Cleanup**: Temp directory được xóa thành công

#### Test Validation:
```bash
# Kiểm tra logs cho Git operations
grep "GitOperationsModule" logs/repochat_debug_*.log
grep "Repository cloned successfully" logs/repochat_debug_*.log
grep "clone_duration_ms" logs/repochat_debug_*.log
```

---

### MT1.3: LanguageIdentifierModule Manual Test ✅

**Description**: Kiểm tra nhận dạng ngôn ngữ lập trình  
**Related Task**: Task 1.3 - Tạo LanguageIdentifierModule

#### Test Steps:
```bash
# 1. Chạy unit test cho LanguageIdentifierModule
cd backend
python -m pytest tests/test_language_identifier_module.py -v

# 2. Test manual language identification
python -c "
from src.teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from src.teams.data_acquisition.git_operations_module import GitOperationsModule

# Clone a repository với multiple languages
git_ops = GitOperationsModule()
repo_path = git_ops.clone_repository('https://github.com/octocat/Hello-World.git')

# Identify languages
lang_id = LanguageIdentifierModule()
languages = lang_id.identify_languages(repo_path)
print(f'Detected languages: {languages}')

# Get detailed stats
stats = lang_id.get_language_statistics(repo_path)
print(f'Language stats: {stats}')

# Cleanup
import shutil
shutil.rmtree(repo_path)
print('Test completed successfully')
"
```

#### Expected Output:
- ✅ **Language Detection**: Detect đúng ngôn ngữ chính (ví dụ: ["python", "javascript", "html"])
- ✅ **File Analysis**: Analyze file extensions và content patterns
- ✅ **Statistics**: Trả về số lượng files cho mỗi ngôn ngữ
- ✅ **Performance**: Language identification hoàn thành trong <5 giây
- ✅ **Accuracy**: Primary language detection chính xác

#### Test Validation:
```bash
# Kiểm tra logs cho Language identification
grep "LanguageIdentifierModule" logs/repochat_debug_*.log
grep "detected_languages" logs/repochat_debug_*.log
grep "language_identification_time" logs/repochat_debug_*.log
```

---

### MT1.4: DataPreparationModule Manual Test ✅

**Description**: Kiểm tra tạo ProjectDataContext từ Git và Language modules  
**Related Task**: Task 1.4 - Tạo DataPreparationModule

#### Test Steps:
```bash
# 1. Chạy unit test cho DataPreparationModule
cd backend
python -m pytest tests/test_data_preparation_module.py -v

# 2. Test manual data context creation
python -c "
from src.teams.data_acquisition import GitOperationsModule, LanguageIdentifierModule, DataPreparationModule

# Setup workflow
git_ops = GitOperationsModule()
lang_id = LanguageIdentifierModule()
data_prep = DataPreparationModule()

# Clone repository
repo_url = 'https://github.com/octocat/Hello-World.git'
repo_path = git_ops.clone_repository(repo_url)

# Identify languages
languages = lang_id.identify_languages(repo_path)

# Create ProjectDataContext
context = data_prep.create_project_context(
    cloned_code_path=repo_path,
    detected_languages=languages,
    repository_url=repo_url
)

print(f'ProjectDataContext created:')
print(f'  Repository URL: {context.repository_url}')
print(f'  Cloned path: {context.cloned_code_path}')
print(f'  Languages: {context.detected_languages}')
print(f'  Language count: {context.language_count}')
print(f'  Primary language: {context.primary_language}')
print(f'  Has languages: {context.has_languages}')

# Cleanup
import shutil
shutil.rmtree(repo_path)
print('Test completed successfully')
"
```

#### Expected Output:
- ✅ **ProjectDataContext**: Object được tạo thành công với đầy đủ fields
- ✅ **Repository URL**: Chính xác URL đã cung cấp
- ✅ **Cloned Path**: Valid path tới repository đã clone
- ✅ **Languages**: List languages detected từ LanguageIdentifierModule
- ✅ **Primary Language**: Ngôn ngữ có nhiều files nhất
- ✅ **Properties**: has_languages và language_count chính xác

#### Test Validation:
```bash
# Kiểm tra logs cho Data preparation
grep "DataPreparationModule" logs/repochat_debug_*.log
grep "Project data context created successfully" logs/repochat_debug_*.log
grep "create_project_context" logs/repochat_debug_*.log
```

---

### MT1.5: handle_scan_project_task Manual Test ✅

**Description**: Kiểm tra workflow chính scan project từ TaskDefinition  
**Related Task**: Task 1.5 - Implement handle_scan_project_task trong OrchestratorAgent

#### Test Steps:
```bash
# 1. Chạy unit test cho OrchestratorAgent
cd backend
python -m pytest tests/test_orchestrator_agent.py::TestOrchestratorAgent::test_handle_scan_project_task_success -v

# 2. Test manual scan project workflow
python -c "
from src.orchestrator.orchestrator_agent import OrchestratorAgent
from src.shared.models.task_definition import TaskDefinition

# Initialize orchestrator
orchestrator = OrchestratorAgent()
print(f'OrchestratorAgent initialized: {orchestrator.agent_id[:8]}')

# Create task definition
task_def = TaskDefinition(repository_url='https://github.com/octocat/Hello-World.git')
print(f'Task created: {task_def.repository_url}')

# Execute scan project task
print('Starting scan project task...')
project_context = orchestrator.handle_scan_project_task(task_def)

# Verify results
print('Scan completed successfully!')
print(f'Repository path: {project_context.cloned_code_path}')
print(f'Detected languages: {project_context.detected_languages}')
print(f'Language count: {project_context.language_count}')
print(f'Primary language: {project_context.primary_language}')
print(f'Repository URL: {project_context.repository_url}')

# Get agent statistics
stats = orchestrator.get_agent_stats()
print(f'Agent stats: uptime={stats[\"uptime_seconds\"]:.2f}s, active_tasks={stats[\"active_tasks_count\"]}')

# Cleanup
import os, shutil
if os.path.exists(project_context.cloned_code_path):
    shutil.rmtree(project_context.cloned_code_path)
    print('Cleaned up repository')

orchestrator.shutdown()
print('Test completed successfully')
"
```

#### Expected Output:
- ✅ **4-Step Workflow**: PAT check → Git clone → Language identification → Data context creation
- ✅ **ProjectDataContext**: Complete context object với tất cả required fields
- ✅ **Performance**: Scan hoàn thành trong <30 giây cho repository nhỏ
- ✅ **Logging**: Chi tiết logs cho từng step với timing metrics
- ✅ **Agent Stats**: Statistics tracking cho tasks handled

#### Test Validation:
```bash
# Kiểm tra workflow logs
grep "handle_scan_project_task" logs/repochat_debug_*.log
grep "Step 1: Checking PAT requirements" logs/repochat_debug_*.log
grep "Step 2: Cloning repository" logs/repochat_debug_*.log
grep "Step 3: Identifying programming languages" logs/repochat_debug_*.log
grep "Step 4: Creating ProjectDataContext" logs/repochat_debug_*.log
grep "Scan project task completed successfully" logs/repochat_debug_*.log
```

---

### MT1.6: PATHandlerModule Manual Test ✅

**Description**: Kiểm tra PAT handling cho private repositories  
**Related Task**: Task 1.6 - Implement PATHandlerModule cho private repositories

#### Test Steps:
```bash
# 1. Chạy unit test cho PATHandlerModule
cd backend
python -m pytest tests/test_pat_handler_module.py -v

# 2. Test manual PAT detection và handling
python -c "
from src.teams.data_acquisition.pat_handler_module import PATHandlerModule

pat_handler = PATHandlerModule()
print('PATHandlerModule initialized')

# Test 1: Public repository (no PAT needed)
public_url = 'https://github.com/octocat/Hello-World.git'
pat = pat_handler.request_pat_if_needed(public_url)
print(f'Public repo test: {public_url} → PAT needed: {pat is not None}')

# Test 2: Private repository detection
private_urls = [
    'https://github.private.company.com/team/repo.git',
    'https://git.corp.company.com/project/repo.git', 
    'git@gitlab.internal.company.com:team/repo.git',
    'https://enterprise.github.com/user/repo.git'
]

for private_url in private_urls:
    is_private = pat_handler._is_private_repository(private_url)
    print(f'Private detection: {private_url} → Private: {is_private}')

# Test 3: Host extraction
test_cases = [
    ('https://github.com/user/repo.git', 'github.com'),
    ('git@gitlab.com:user/repo.git', 'gitlab.com'),
    ('https://bitbucket.org/user/repo.git', 'bitbucket.org')
]

for url, expected_host in test_cases:
    extracted_host = pat_handler._extract_host(url)
    print(f'Host extraction: {url} → {extracted_host} (expected: {expected_host})')

# Test 4: PAT cache management
pat_handler._pat_cache['test.com'] = 'test_pat'
print(f'Cache before clear: {len(pat_handler._pat_cache)} items')
pat_handler.clear_pat_cache()
print(f'Cache after clear: {len(pat_handler._pat_cache)} items')

# Test 5: Statistics
stats = pat_handler.get_stats()
print(f'PAT stats: {stats}')

print('All PAT tests completed successfully')
"
```

#### Expected Output:
- ✅ **Public Repository**: No PAT requested for public URLs (pat is None)
- ✅ **Private Detection**: All private URL patterns được detect đúng (True)
- ✅ **Host Extraction**: Correct host extraction từ mọi URL format
- ✅ **Cache Management**: PAT cache clear hoạt động đúng (0 items after clear)
- ✅ **Statistics**: Valid stats object với cached_hosts và cached_host_list

#### Test Private Repository Simulation:
```bash
# Test với private repository simulation
python -c "
from src.orchestrator.orchestrator_agent import OrchestratorAgent
from src.shared.models.task_definition import TaskDefinition

orchestrator = OrchestratorAgent()
private_url = 'https://github.private.company.com/team/secret-repo.git'
task_def = TaskDefinition(repository_url=private_url)

# Check private detection
is_private = orchestrator.pat_handler._is_private_repository(private_url)
print(f'Private repository detection: {is_private}')

# Simulate authenticated URL building
test_pat = 'ghp_simulated_token_12345'
host = orchestrator.pat_handler._extract_host(private_url)
auth_url = orchestrator.git_operations._build_authenticated_url(private_url, test_pat)
print(f'Host: {host}')
print(f'Authenticated URL: {auth_url[:50]}...')

orchestrator.shutdown()
print('Private repository simulation completed')
"
```

#### Test Validation:
```bash
# Kiểm tra PAT logs
grep "PATHandlerModule" logs/repochat_debug_*.log
grep "PAT Handler Module initialized" logs/repochat_debug_*.log
grep "Private repository detected" logs/repochat_debug_*.log
grep "PAT obtained and cached" logs/repochat_debug_*.log
```

---

### MT1.7: Integration Test Suite Manual Test ✅

**Description**: Chạy toàn bộ integration test suite cho Phase 1  
**Related Task**: All Phase 1 tasks integration

#### Test Steps:
```bash
# 1. Chạy comprehensive integration test
cd backend/tests
python integration_test_phase_1.py

# 2. Chạy full test suite
cd backend
python -m pytest tests/ -v --tb=short
```

#### Expected Output:
- ✅ **5 Integration Tests**: All tests PASSED
  - Test 1: Public Repository Scan (Task 1.5) ✅
  - Test 2: PAT Handler Module (Task 1.6) ✅  
  - Test 3: Private Repository Simulation ✅
  - Test 4: Error Handling ✅
  - Test 5: Component Integration ✅
- ✅ **Unit Tests**: 100+ tests PASSED
- ✅ **Performance**: All tests complete trong <5 phút
- ✅ **No Errors**: Không có unhandled exceptions

#### Test Validation:
```bash
# Kiểm tra test results
echo "Integration test results:"
python backend/tests/integration_test_phase_1.py | grep "PASSED\|FAILED"

echo "Unit test summary:"
python -m pytest backend/tests/ --tb=no -q
```

---

### MT1.8: End-to-End Workflow Manual Test ✅ PASSED

**Description**: Test complete workflow từ TaskDefinition đến ProjectDataContext  
**Related Task**: Full Phase 1 workflow integration

#### Test Steps:
```bash
# Test complete end-to-end workflow using fixed script
cd backend
python manual_test_mt1_8_fixed.py

# Alternative: Manual inline test (if script not available)
python -c "
import sys, os
sys.path.append(os.path.join(os.getcwd(), 'src'))

import time
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

print('=== PHASE 1 END-TO-END WORKFLOW TEST ===')
start_time = time.time()

# Step 1: Initialize system
orchestrator = OrchestratorAgent()
print(f'✅ System initialized in {(time.time() - start_time)*1000:.2f}ms')

# Step 2: Create task definition
task_def = TaskDefinition(
    repository_url='https://github.com/octocat/Hello-World.git',  # Smaller repo for faster testing
    task_id='e2e-test-001'
)
print(f'✅ Task created: {task_def.task_id}')

# Step 3: Execute scan project task
step_start = time.time()
try:
    project_context = orchestrator.handle_scan_project_task(task_def)
    execution_time = time.time() - step_start
    
    print(f'✅ Scan completed in {execution_time:.2f}s')
    print(f'   Repository: {project_context.repository_url}')
    print(f'   Path: {project_context.cloned_code_path}')
    print(f'   Languages: {project_context.detected_languages}')
    print(f'   Primary: {project_context.primary_language}')
    print(f'   Count: {project_context.language_count}')
    
    # Step 4: Verify data quality
    assert project_context.repository_url == task_def.repository_url
    assert project_context.cloned_code_path is not None
    print(f'✅ Data validation passed')
    
    # Step 5: Check agent statistics
    stats = orchestrator.get_agent_stats()
    print(f'✅ Agent stats: {stats[\"statistics\"][\"successful_tasks\"]} successful tasks')
    
    # Cleanup
    import shutil
    if os.path.exists(project_context.cloned_code_path):
        shutil.rmtree(project_context.cloned_code_path)
        print(f'✅ Cleanup completed')
        
except Exception as e:
    print(f'❌ Test failed: {e}')
    
finally:
    orchestrator.shutdown()
    total_time = time.time() - start_time
    print(f'✅ Total test time: {total_time:.2f}s')
    print('=== END-TO-END TEST COMPLETED ===')
"
```

#### Expected Output:
- ✅ **System Init**: Orchestrator khởi tạo thành công trong <1000ms
- ✅ **Task Creation**: TaskDefinition được tạo với correct fields
- ✅ **Scan Execution**: Workflow hoàn thành thành công trong <60s
- ✅ **Data Quality**: ProjectDataContext có valid data
- ✅ **Performance**: Meets timing requirements cho production use
- ✅ **Cleanup**: Resources được dọn dẹp đúng cách

---

### 🔍 TROUBLESHOOTING GUIDE

#### Common Issues và Solutions:

**Issue 1: Import Errors**
```bash
# Solution: Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/src"
cd backend && python -c "import sys; print(sys.path)"
```

**Issue 2: Git Clone Failures**
```bash
# Solution: Check network và Git installation
git --version
ping github.com
curl -I https://github.com
```

**Issue 3: Log Files Not Created**
```bash
# Solution: Check permissions và create logs directory
mkdir -p backend/logs
chmod 755 backend/logs
```

**Issue 4: Test Dependencies**
```bash
# Solution: Reinstall requirements
cd backend
pip install --upgrade -r requirements.txt
```

---

### 📊 SUCCESS CRITERIA SUMMARY

**Phase 1 được coi là hoàn thành thành công khi:**

✅ **All Manual Tests Pass**: 8/8 manual test scenarios PASSED  
✅ **Unit Tests**: 100+ tests PASSED với >95% coverage  
✅ **Integration Tests**: 5/5 integration scenarios PASSED  
✅ **Performance**: Scan repository hoàn thành trong <60s  
✅ **Logging**: Comprehensive logs với structured format  
✅ **Security**: PAT handling an toàn, không persist credentials  
✅ **Error Handling**: Graceful degradation cho mọi error cases  
✅ **Documentation**: Complete manual test procedures documented  

**🎯 Result**: **PHASE 1 FULLY VALIDATED VÀ READY FOR PHASE 2**

---

## Phase 2: Xây dựng Code Knowledge Graph (CKG) Ban đầu

### Task 2.1 (F2.1): `TEAM CKG Operations`: Thiết lập kết nối đến Neo4j ✅ **COMPLETED** (2024-12-05)
- [x] **Task:** Cài đặt Neo4j Community Edition.
    - **DoD:**
        - ✅ Neo4j được cài đặt và chạy cục bộ.
        - ✅ Có thể truy cập Neo4j Browser.
- [x] **Task:** Viết module/utility để kết nối Neo4j từ Python.
    - **DoD:**
        - ✅ Một module Python có các hàm để thiết lập session với Neo4j sử dụng thư viện `neo4j`.
        - ✅ Có thể thực thi một truy vấn Cypher đơn giản (ví dụ: `RETURN 1`) và nhận kết quả.

**Implementation Details:**
- ✅ Created `Neo4jConnectionModule` với comprehensive functionality
- ✅ Supports connection management, health monitoring, query execution  
- ✅ Includes proper error handling và logging
- ✅ Context manager support cho resource cleanup
- ✅ Basic unit tests với 12 passing tests
- ✅ Demo script created cho manual testing
- ✅ Integration với shared logging system
- 📁 Files created:
  - `backend/src/teams/ckg_operations/neo4j_connection_module.py`
  - `backend/tests/test_neo4j_connection_module.py`
  - `backend/demo_neo4j_connection.py`

### Task 2.2 (F2.2): `TEAM CKG Operations` (`CodeParserCoordinatorModule`): Điều phối parser
- [ ] **Task:** Viết module Python `CodeParserCoordinatorModule`.
    - **DoD:**
        - Module có một hàm nhận `ProjectDataContext` (chứa `detected_languages` và `cloned_code_path`).
        - Dựa trên `detected_languages`, hàm sẽ gọi các parser chuyên biệt tương ứng (ban đầu là Java và Python).
        - Hàm thu thập kết quả (ví dụ: danh sách các đối tượng AST hoặc cấu trúc dữ liệu trung gian) từ các parser.

### Task 2.3 (F2.3): Phát triển parser cơ bản cho Java
- [ ] **Task:** Viết module parser Java sử dụng `javaparser`.
    - **DoD:**
        - Module có hàm nhận đường dẫn đến một file Java.
        - Hàm sử dụng `javaparser` để phân tích file.
        - Trích xuất được danh sách các tên class, tên method trong class đó.
        - Trích xuất được các lời gọi method trực tiếp đến các method khác trong cùng file/class (ví dụ: `methodA()` gọi `this.methodB()` hoặc `methodB()`).
        - Kết quả trả về dưới dạng cấu trúc dữ liệu đã định nghĩa (ví dụ: list các object chứa thông tin class, method, calls).

### Task 2.4 (F2.4): Phát triển parser cơ bản cho Python
- [ ] **Task:** Viết module parser Python sử dụng module `ast`.
    - **DoD:**
        - Module có hàm nhận đường dẫn đến một file Python.
        - Hàm sử dụng module `ast` để phân tích file.
        - Trích xuất được danh sách các tên function, tên class, tên method trong class.
        - Trích xuất được các lời gọi function/method trực tiếp đến các function/method khác trong cùng file (ví dụ: `function_x()` gọi `function_y()`).
        - Kết quả trả về dưới dạng cấu trúc dữ liệu đã định nghĩa.

### Task 2.5 (F2.5): Phát triển parser cơ bản cho Kotlin và Dart (Mở rộng/Phase 3)
- [ ] **Task:** Nghiên cứu thư viện parsing cho Kotlin (ví dụ: Kotlin Compiler API, Detekt).
    - **DoD:** Xác định được thư viện và cách tiếp cận cơ bản.
- [ ] **Task:** (Nếu khả thi trong Phase 2) Implement parser Kotlin cơ bản.
    - **DoD:** Tương tự F2.3 cho Kotlin.
- [ ] **Task:** Nghiên cứu thư viện parsing cho Dart (ví dụ: `analyzer` package).
    - **DoD:** Xác định được thư viện và cách tiếp cận cơ bản.
- [ ] **Task:** (Nếu khả thi trong Phase 2) Implement parser Dart cơ bản.
    - **DoD:** Tương tự F2.3 cho Dart.

### Task 2.6 (F2.6): `TEAM CKG Operations` (`ASTtoCKGBuilderModule`): Chuyển đổi thực thể thành node CKG
- [ ] **Task:** Định nghĩa CKG Schema ban đầu cho nodes.
    - **DoD:**
        - Schema được tài liệu hóa, bao gồm các loại Node: `File`, `Class`, `Function`, `Method`.
        - Mỗi loại Node có các thuộc tính cơ bản (ví dụ: `name`, `path` cho `File`; `name`, `signature` cho `Function`/`Method`).
- [ ] **Task:** Viết `ASTtoCKGBuilderModule` để tạo nodes.
    - **DoD:**
        - Module có hàm nhận kết quả đã parse (từ `CodeParserCoordinatorModule`).
        - Với mỗi thực thể code (file, class, function, method), hàm tạo các câu lệnh Cypher `CREATE` hoặc `MERGE` để thêm node tương ứng vào Neo4j.
        - Các node được tạo thành công trong Neo4j.

### Task 2.7 (F2.7): `TEAM CKG Operations` (`ASTtoCKGBuilderModule`): Chuyển đổi mối quan hệ "CALLS"
- [ ] **Task:** Định nghĩa CKG Schema cho relationship "CALLS".
    - **DoD:**
        - Relationship `CALLS` được định nghĩa giữa các node `Function`/`Method`.
- [ ] **Task:** Mở rộng `ASTtoCKGBuilderModule` để tạo relationship "CALLS".
    - **DoD:**
        - Module sử dụng thông tin về các lời gọi trực tiếp đã parse.
        - Tạo các câu lệnh Cypher `CREATE` hoặc `MERGE` để thêm relationship `CALLS` giữa các node Function/Method tương ứng trong Neo4j.
        - Các relationship `CALLS` được tạo thành công.

### Task 2.8 (F2.8): `TEAM CKG Operations` (`CKGQueryInterfaceModule`): API truy vấn CKG cơ bản
- [ ] **Task:** Viết `CKGQueryInterfaceModule`.
    - **DoD:**
        - Module có một hàm (ví dụ: `get_class_definition_location(class_name: str)`).
        - Hàm thực thi truy vấn Cypher lên Neo4j để tìm node `Class` với tên tương ứng và trả về thuộc tính `path` của node `File` chứa class đó.
        - Hàm trả về kết quả chính xác.

### Task 2.9 (F2.9): Orchestrator Agent: Điều phối luồng TDA -> TCKG
- [ ] **Task:** Mở rộng `OrchestratorAgent`.
    - **DoD:**
        - Sau khi `TEAM Data Acquisition` hoàn thành và trả về `ProjectDataContext`, `OrchestratorAgent` kích hoạt `TEAM CKG Operations` (ví dụ: gọi một facade `TeamCKGOperations`) với `ProjectDataContext` làm đầu vào.
        - `TEAM CKG Operations` báo cáo trạng thái (thành công/lỗi cơ bản) về cho Orchestrator (ví dụ: qua log).

## Phase 3: Phân tích Code Cơ bản & Tích hợp LLM (Logic Cốt lõi)

### Task 3.1 (F3.1): `TEAM Code Analysis` (`ArchitecturalAnalyzerModule`): Phát hiện circular dependencies
- [ ] **Task:** Viết logic phát hiện circular dependencies.
    - **DoD:**
        - Module có hàm nhận đầu vào là quyền truy cập CKG (ví dụ: thông qua `CKGQueryInterfaceModule` hoặc session Neo4j).
        - Hàm thực thi truy vấn Cypher để tìm các chu trình (ví dụ: giữa các node `File` dựa trên relationship `IMPORTS`, hoặc giữa các `Class` dựa trên `EXTENDS`/`IMPLEMENTS` - cần định nghĩa thêm các relationship này nếu muốn phân tích ở mức đó).
        - Hàm trả về danh sách các circular dependencies đã phát hiện.
        - Tạo đối tượng `AnalysisFinding` cho mỗi circular dependency.

### Task 3.2 (F3.2): `TEAM Code Analysis` (`ArchitecturalAnalyzerModule`): Xác định public elements không sử dụng
- [ ] **Task:** Viết logic xác định public elements không sử dụng.
    - **DoD:**
        - Module có hàm nhận quyền truy cập CKG.
        - Hàm truy vấn CKG để tìm các node `Method`/`Function` được đánh dấu là "public" (cần thêm thuộc tính này vào CKG hoặc suy luận từ parser).
        - Kiểm tra xem các node này có relationship `CALLS` trỏ đến chúng hay không (từ bên trong codebase đã phân tích).
        - Hàm trả về danh sách các public elements có khả năng không được sử dụng, kèm cảnh báo rõ ràng về hạn chế của phân tích tĩnh.
        - Tạo đối tượng `AnalysisFinding` cho mỗi trường hợp.

### Task 3.3 (F3.3): `TEAM LLM Services` (`LLMProviderAbstractionLayer`): Hoàn thiện OpenAI provider
- [ ] **Task:** Viết `OpenAIProvider` trong `LLMProviderAbstractionLayer`.
    - **DoD:**
        - Class `OpenAIProvider` implement một interface chung (ví dụ: `LLMProviderInterface` với method `complete(prompt, **kwargs)`).
        - Method `complete` sử dụng thư viện `openai` để gọi API của OpenAI (ví dụ: `chat.completions.create`).
        - Xử lý API key của OpenAI một cách an toàn (ví dụ: từ biến môi trường).
        - Có khả năng truyền các tham số cơ bản (model, temperature) cho API.
        - Trả về nội dung text từ phản hồi của LLM.
        - Xử lý lỗi cơ bản từ API (ví dụ: log lỗi, trả về None).

### Task 3.4 (F3.4): `TEAM LLM Services` (`LLMGatewayModule`, `PromptFormatterModule`): Prompt template "Giải thích code"
- [ ] **Task:** Thiết kế prompt template cho "Giải thích đoạn code này".
    - **DoD:**
        - Một string template được tạo, có placeholder cho đoạn code cần giải thích. Ví dụ: "Hãy giải thích chức năng của đoạn code sau: \n```\n{code_snippet}\n```".
- [ ] **Task:** Viết `PromptFormatterModule`.
    - **DoD:**
        - Module có hàm nhận `template_id` và `context_data` (ví dụ: `{"code_snippet": "..."}`).
        - Hàm điền `context_data` vào template tương ứng và trả về prompt hoàn chỉnh.
- [ ] **Task:** Viết `LLMGatewayModule` cơ bản.
    - **DoD:**
        - Module có hàm nhận `prompt_id` và `context_data`.
        - Gọi `PromptFormatterModule` để lấy prompt.
        - Gọi `OpenAIProvider.complete(prompt)` để nhận phản hồi từ LLM.
        - Trả về phản hồi của LLM.

### Task 3.5 (F3.5): `TEAM Code Analysis` (`LLMAnalysisSupportModule`): Chuẩn bị ngữ cảnh và tạo `LLMServiceRequest`
- [ ] **Task:** Định nghĩa cấu trúc `LLMServiceRequest` và `LLMServiceResponse`.
    - **DoD:**
        - Pydantic model/data class `LLMServiceRequest` chứa `prompt_id` (hoặc `prompt_text`), `context_data`, và `llm_config` (ban đầu có thể là model name mặc định).
        - Pydantic model/data class `LLMServiceResponse` chứa `response_text` và `status`.
- [ ] **Task:** Viết `LLMAnalysisSupportModule`.
    - **DoD:**
        - Module có hàm nhận một đoạn code (string).
        - Hàm tạo một `LLMServiceRequest` với `prompt_id="explain_code"`, `context_data={"code_snippet": code_string}`, và cấu hình LLM mặc định.
        - Trả về `LLMServiceRequest`.

### Task 3.6 (F3.6): Orchestrator Agent: Định tuyến yêu cầu/phản hồi LLM
- [ ] **Task:** Mở rộng `OrchestratorAgent` để định tuyến LLM.
    - **DoD:**
        - `OrchestratorAgent` có method (ví dụ: `route_llm_request`) nhận `LLMServiceRequest` từ một TEAM (ví dụ: TCA).
        - Method này gọi `TEAM LLM Services` (ví dụ: facade `TeamLLMServices.process_request(llm_request)`).
        - `TEAM LLM Services` trả về `LLMServiceResponse`.
        - Orchestrator chuyển `LLMServiceResponse` lại cho TEAM đã yêu cầu.
        - Luồng này được kiểm tra bằng cách `TEAM Code Analysis` yêu cầu giải thích code, Orchestrator điều phối, và TCA nhận được kết quả (log ra).

### Task 3.7 (F3.7): `TEAM Code Analysis`: Phân tích PR cơ bản (tác động trực tiếp)
- [ ] **Task:** `TEAM Data Acquisition` cần lấy thông tin diff của PR.
    - **DoD:**
        - `GitOperationsModule` có khả năng lấy diff của một PR (ví dụ: sử dụng API của GitHub/GitLab nếu có PAT, hoặc parse file diff nếu được cung cấp).
        - `ProjectDataContext` được cập nhật để chứa thông tin diff (danh sách file thay đổi, và có thể là các dòng/hàm thay đổi). *Lưu ý: Phase 1 chỉ mô phỏng PAT, phase này có thể cần tích hợp Git API thực sự hoặc giả định diff được cung cấp.*
- [ ] **Task:** `TEAM Code Analysis` phân tích tác động trực tiếp.
    - **DoD:**
        - Module nhận `ProjectDataContext` (chứa diff PR) và quyền truy cập CKG.
        - Xác định các function/method trong CKG tương ứng với các function/method đã thay đổi trong diff.
        - Với mỗi function/method đã thay đổi, truy vấn CKG để tìm:
            - Các function/method gọi trực tiếp đến nó (incoming "CALLS" relationships).
            - Các function/method mà nó gọi trực tiếp (outgoing "CALLS" relationships).
        - Kết quả phân tích (danh sách callers/callees cho mỗi thay đổi) được tạo ra.
        - Tạo đối tượng `AnalysisFinding` cho các tác động này.

### Task 3.8 (F3.8): `StaticAnalysisIntegratorModule`: Tạo placeholder
- [ ] **Task:** Tạo file module `StaticAnalysisIntegratorModule.py`.
    - **DoD:**
        - File được tạo với các hàm rỗng hoặc comment mô tả chức năng tương lai (ví dụ: `run_linter(language, code_path)`).
        - Module này chưa cần thực hiện logic gì ở phase này.

## Phase 4: Tương tác Người dùng Cơ bản & Báo cáo (CLI/Web Đơn giản)

### Task 4.1 (F4.1): `TEAM Interaction & Tasking`: CLI cho "scan project"
- [ ] **Task:** Xây dựng CLI cơ bản sử dụng `argparse` hoặc `click`.
    - **DoD:**
        - CLI chấp nhận một lệnh con `scan_project`.
        - Lệnh `scan_project` chấp nhận một đối số là URL của repository.
        - Khi chạy, CLI gọi `OrchestratorAgent` với `TaskDefinition` tương ứng.

### Task 4.2 (F4.2): `TEAM Interaction & Tasking`: Mở rộng CLI cho "review PR"
- [ ] **Task:** Mở rộng CLI.
    - **DoD:**
        - CLI chấp nhận một lệnh con `review_pr`.
        - Lệnh `review_pr` chấp nhận URL repository và PR ID (hoặc URL PR).
        - Khi chạy, CLI gọi `OrchestratorAgent` với `TaskDefinition` tương ứng (bao gồm thông tin PR).

### Task 4.3 (F4.3): `TEAM Interaction & Tasking` (`TaskInitiationModule`): Tạo `TaskDefinition` từ CLI
- [ ] **Task:** Viết `TaskInitiationModule`.
    - **DoD:**
        - Module có các hàm để tạo `TaskDefinition` object từ các tham số nhận được từ CLI (URL, PR ID).
        - `TaskDefinition` được cập nhật để chứa `pr_id` (nếu có).
        - Vẫn sử dụng cấu hình LLM mặc định/hardcoded trong `TaskDefinition` ở phase này.

### Task 4.4 (F4.4): `TEAM Synthesis & Reporting` (`FindingAggregatorModule`): Thu thập `AnalysisFinding`
- [ ] **Task:** Viết `FindingAggregatorModule`.
    - **DoD:**
        - Module có hàm nhận một danh sách các `AnalysisFinding` (từ `TEAM Code Analysis` thông qua Orchestrator).
        - Hàm có thể thực hiện xử lý cơ bản như loại bỏ trùng lặp (nếu có) hoặc sắp xếp.
        - Trả về danh sách các phát hiện đã được tổng hợp/xử lý.

### Task 4.5 (F4.5): `TEAM Synthesis & Reporting` (`ReportGeneratorModule`): Tạo báo cáo text đơn giản
- [ ] **Task:** Viết `ReportGeneratorModule` để tạo báo cáo text.
    - **DoD:**
        - Module có hàm nhận danh sách các `AnalysisFinding` đã tổng hợp.
        - Hàm tạo một chuỗi string dạng text, liệt kê các phát hiện một cách rõ ràng (ví dụ: "Circular Dependency: fileA -> fileB -> fileA", "Unused Public Method: classC.methodX").
        - Trả về chuỗi báo cáo text.

### Task 4.6 (F4.6): `TEAM Synthesis & Reporting` (`ReportGeneratorModule`): Tích hợp tóm tắt tác động PR
- [ ] **Task:** Mở rộng `ReportGeneratorModule`.
    - **DoD:**
        - Hàm tạo báo cáo cũng nhận thông tin phân tích tác động PR (từ F3.7).
        - Tích hợp thông tin này vào báo cáo text (ví dụ: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ...").

### Task 4.7 (F4.7): `TEAM Synthesis & Reporting` (`OutputFormatterModule`): Tạo `FinalReviewReport` (text)
- [ ] **Task:** Định nghĩa cấu trúc `FinalReviewReport`.
    - **DoD:**
        - Pydantic model/data class `FinalReviewReport` chứa trường `report_content: str` (và có thể là `report_format: str = "text"`).
- [ ] **Task:** Viết `OutputFormatterModule`.
    - **DoD:**
        - Module có hàm nhận chuỗi báo cáo text từ `ReportGeneratorModule`.
        - Hàm tạo và trả về một instance của `FinalReviewReport`.

### Task 4.8 (F4.8): `TEAM Interaction & Tasking` (`PresentationModule`): Hiển thị `FinalReviewReport` trên CLI
- [ ] **Task:** Viết `PresentationModule` cho CLI.
    - **DoD:**
        - Module có hàm nhận `FinalReviewReport`.
        - Hàm in `report_content` ra console.
        - CLI được cập nhật để sau khi Orchestrator hoàn thành tác vụ, nó sẽ gọi module này để hiển thị kết quả.

### Task 4.9 (F4.9 Q&A): Luồng Q&A "Định nghĩa class X ở đâu?"
- [ ] **Task:** Mở rộng CLI để chấp nhận câu hỏi Q&A.
    - **DoD:**
        - CLI có lệnh con `ask` hoặc một chế độ tương tác.
        - Chấp nhận câu hỏi dạng "Định nghĩa của class X ở đâu?".
- [ ] **Task:** `TEAM Interaction & Tasking` (`UserIntentParserAgent`) phân tích câu hỏi Q&A.
    - **DoD:**
        - Phân tích được ý định là "find_class_definition" và trích xuất được `class_name`.
- [ ] **Task:** `TEAM Code Analysis` xử lý yêu cầu Q&A.
    - **DoD:**
        - Có hàm nhận `class_name`.
        - Gọi `CKGQueryInterfaceModule.get_class_definition_location(class_name)`.
        - Trả về kết quả (đường dẫn file).
- [ ] **Task:** `TEAM Synthesis & Reporting` định dạng câu trả lời Q&A.
    - **DoD:**
        - Nhận đường dẫn file và tạo một câu trả lời dạng text (ví dụ: "Class X được định nghĩa tại: [đường dẫn]").
- [ ] **Task:** `TEAM Interaction & Tasking` (`PresentationModule`) hiển thị câu trả lời Q&A trên CLI.
    - **DoD:** Câu trả lời được in ra console.

## Phase 5: Tính năng Nâng cao & Phát triển Frontend (Vue.js)

### Task 5.1 (F5.1 Frontend): Xây dựng giao diện chat Vue.js cơ bản
- [ ] **Task:** Thiết lập dự án Vue.js (ví dụ: sử dụng Vue CLI hoặc Vite).
    - **DoD:** Dự án Vue.js được tạo và có thể chạy server dev.
- [ ] **Task:** Tạo component chính cho giao diện chat.
    - **DoD:**
        - Component có một ô nhập liệu (input text) cho người dùng.
        - Một khu vực để hiển thị các tin nhắn (cả người dùng và bot).
        - Khi người dùng gửi tin nhắn, tin nhắn đó được hiển thị trong khu vực chat.
        - (Tạm thời) Bot phản hồi bằng một tin nhắn cố định.

### Task 5.2 (F5.2 Frontend): Sidebar với "New Chat", "Settings", Lịch sử Chat (mock)
- [ ] **Task:** Tạo component Sidebar.
    - **DoD:**
        - Sidebar hiển thị các nút "New Chat" và "Settings".
        - Khu vực hiển thị danh sách các cuộc hội thoại trước đó (ban đầu có thể là dữ liệu mock, ví dụ: "Chat 1", "Chat 2").
        - Các nút và mục lịch sử có thể nhấp được (chưa cần thực hiện hành động phức tạp).

### Task 5.3 (F5.3 Frontend): Màn hình Settings UI cho cấu hình LLM
- [ ] **Task:** Tạo component SettingsScreen.
    - **DoD:**
        - Component hiển thị các mục cho phép người dùng chọn model LLM (ví dụ: dropdown list) cho các chức năng/TEAM khác nhau (ví dụ: "NLU Model", "Code Analysis Model", "Report Generation Model").
        - Danh sách model LLM có thể được hardcode ban đầu (ví dụ: "gpt-4o-mini", "gpt-4-turbo").
        - Có nút "Save Settings".
        - Khi "Save Settings" được nhấp, lựa chọn của người dùng được log ra console (chưa cần lưu trữ thực sự ở bước này của frontend).

### Task 5.4 (F5.4 Backend): `TEAM Interaction & Tasking` (`ConfigurationManagementAgent`): Lưu/truy xuất cấu hình LLM
- [ ] **Task:** Thiết kế cơ chế lưu trữ cấu hình LLM người dùng.
    - **DoD:**
        - Quyết định nơi lưu trữ (ví dụ: file JSON cho mỗi người dùng, hoặc database đơn giản nếu có kế hoạch mở rộng).
- [ ] **Task:** Viết `ConfigurationManagementAgent`.
    - **DoD:**
        - Có hàm `save_llm_config(user_id, config_data)` để lưu cấu hình.
        - Có hàm `get_llm_config(user_id)` để truy xuất cấu hình.
        - Cấu hình được lưu và truy xuất thành công.

### Task 5.5 (F5.5 Tích hợp): Sử dụng cấu hình LLM người dùng trong `TaskDefinition` và `LLMServiceRequest`
- [ ] **Task:** Cập nhật `TaskInitiationModule`.
    - **DoD:**
        - Khi tạo `TaskDefinition`, module gọi `ConfigurationManagementAgent.get_llm_config(user_id)` để lấy cấu hình LLM hiện tại của người dùng.
        - Thông tin cấu hình LLM (ví dụ: model name cho từng chức năng) được đưa vào `TaskDefinition`.
- [ ] **Task:** Cập nhật Orchestrator để truyền cấu hình LLM.
    - **DoD:** Orchestrator truyền các phần liên quan của cấu hình LLM từ `TaskDefinition` đến `TEAM Code Analysis` và `TEAM Synthesis & Reporting` khi kích hoạt chúng.
- [ ] **Task:** Cập nhật `LLMAnalysisSupportModule` (TCA) và `ReportGeneratorModule` (TSR).
    - **DoD:**
        - Các module này nhận cấu hình LLM (ví dụ: model name) từ Orchestrator.
        - Khi tạo `LLMServiceRequest`, chúng đưa thông tin model LLM này vào request.
- [ ] **Task:** Cập nhật `TEAM LLM Services` (`LLMGatewayModule`).
    - **DoD:**
        - `LLMGatewayModule` sử dụng model LLM được chỉ định trong `LLMServiceRequest` khi gọi `LLMProviderAbstractionLayer`.
        - Kiểm tra (qua log) rằng model LLM chính xác (theo cấu hình người dùng) được sử dụng.

### Task 5.6 (F5.6): `TEAM Synthesis & Reporting` (`DiagramGeneratorModule`): Sinh mã PlantUML/Mermaid.js
- [ ] **Task:** Viết `DiagramGeneratorModule`.
    - **DoD:**
        - Module có hàm nhận `class_name` và quyền truy cập CKG.
        - Truy vấn CKG để lấy thông tin về class đó (tên, methods, thuộc tính cơ bản - cần mở rộng CKG schema nếu muốn chi tiết hơn).
        - Tạo chuỗi string chứa mã PlantUML hoặc Mermaid.js mô tả class diagram cơ bản cho class đó.
        - Trả về chuỗi mã sơ đồ.

### Task 5.7 (F5.7 Frontend): Hiển thị sơ đồ PlantUML/Mermaid.js
- [ ] **Task:** Tích hợp thư viện render sơ đồ vào Vue.js.
    - **DoD:**
        - Chọn và cài đặt một thư viện (ví dụ: `vue-mermaid-string` cho Mermaid, hoặc một cách để hiển thị ảnh PlantUML nếu backend tạo ảnh).
- [ ] **Task:** Tạo component để hiển thị sơ đồ.
    - **DoD:**
        - Component nhận mã nguồn sơ đồ (PlantUML/Mermaid) làm prop.
        - Render sơ đồ một cách chính xác trong giao diện chat.
- [ ] **Task:** Cập nhật backend để `FinalReviewReport` có thể chứa mã sơ đồ.
    - **DoD:** `FinalReviewReport` có trường `diagram_code: Optional[str]`.
- [ ] **Task:** Cập nhật luồng để khi người dùng yêu cầu sơ đồ, mã sơ đồ được gửi về frontend và hiển thị.

### Task 5.8 (F5.8): `TEAM Code Analysis` (`TestCoModificationCheckerModule`): Heuristic kiểm tra test
- [ ] **Task:** `TEAM CKG Operations` cần liên kết code và test.
    - **DoD:**
        - Mở rộng CKG schema để có node `TestFile`, `TestMethod`.
        - Mở rộng parser để xác định các file/method test (ví dụ: dựa trên tên file/method, annotations).
        - Tạo relationship (ví dụ: `TESTS_METHOD`, `TESTS_CLASS`) giữa các node test và node code tương ứng trong CKG.
- [ ] **Task:** Viết `TestCoModificationCheckerModule`.
    - **DoD:**
        - Module nhận `ProjectDataContext` (chứa diff PR) và quyền truy cập CKG.
        - Với mỗi method/class code bị thay đổi trong PR, kiểm tra CKG xem có các method/class test liên quan không.
        - Kiểm tra xem các file chứa method/class test đó có nằm trong danh sách file bị thay đổi của PR hay không.
        - Tạo `AnalysisFinding` (dạng "Observation") nếu code thay đổi nhưng test liên quan không thay đổi (hoặc ngược lại).

### Task 5.9 (F5.9): `TEAM Synthesis & Reporting`: Tích hợp quan sát test vào báo cáo
- [ ] **Task:** Mở rộng `ReportGeneratorModule` và `FinalReviewReport`.
    - **DoD:**
        - `FinalReviewReport` có thể chứa một mục riêng cho các quan sát về test.
        - `ReportGeneratorModule` tích hợp các `AnalysisFinding` từ `TestCoModificationCheckerModule` vào báo cáo.

### Task 5.10 (F5.10): `TEAM Data Acquisition` (`PRMetadataExtractorAgent`): Trích xuất metadata PR
- [ ] **Task:** Mở rộng `GitOperationsModule` hoặc tạo `PRMetadataExtractorAgent`.
    - **DoD:**
        - Nếu review PR, module sử dụng API của nền tảng Git (GitHub, GitLab - cần xử lý PAT thực sự ở đây) để lấy title, description, và comments của PR.
        - Cố gắng parse description để tìm các link đến issue tracker (ví dụ: Jira, Trello) bằng regex hoặc heuristics.
        - `ProjectDataContext` được cập nhật để chứa các metadata này.

### Task 5.11 (F5.11): `TEAM Synthesis & Reporting`: Tích hợp metadata PR vào báo cáo
- [ ] **Task:** Mở rộng `ReportGeneratorModule` và `FinalReviewReport`.
    - **DoD:**
        - `FinalReviewReport` hiển thị title, description của PR và các link issue tracker (nếu có) ở phần đầu của báo cáo.

### Task 5.12 (F5.12 Tính năng LLM): Phân tích code so với mô tả PR
- [ ] **Task:** Thiết kế prompt template cho "Phân tích sự phù hợp của code thay đổi với mô tả PR".
    - **DoD:**
        - Prompt template được tạo, nhận đầu vào là mô tả PR và tóm tắt các thay đổi code (hoặc các đoạn code chính).
        - Yêu cầu LLM đưa ra nhận xét về mức độ code giải quyết vấn đề trong mô tả PR.
- [ ] **Task:** `TEAM Code Analysis` (`LLMAnalysisSupportModule`) chuẩn bị ngữ cảnh.
    - **DoD:**
        - Module thu thập mô tả PR (từ `ProjectDataContext`) và tóm tắt các thay đổi code chính.
        - Tạo `LLMServiceRequest` với prompt_id tương ứng và ngữ cảnh này.
- [ ] **Task:** `TEAM Synthesis & Reporting` tích hợp nhận xét LLM vào báo cáo.
    - **DoD:**
        - `ReportGeneratorModule` nhận phản hồi LLM (qua Orchestrator) và đưa vào một mục trong `FinalReviewReport`.

### Task 5.13 (F5.13 Frontend): Luồng xác thực người dùng cơ bản
- [ ] **Task:** Tạo trang Login và Register đơn giản trên Vue.js.
    - **DoD:**
        - Các form nhập liệu cho username/password.
        - Nút Login/Register.
        - (Tạm thời) Khi submit, log thông tin ra console.
- [ ] **Task:** Thiết kế API backend cho xác thực (rất cơ bản).
    - **DoD:**
        - Endpoint `/register` và `/login` (ví dụ: lưu user vào file JSON hoặc DB đơn giản).
        - Trả về một token giả (ví dụ: UUID) khi login thành công.
- [ ] **Task:** Frontend gọi API backend và xử lý token.
    - **DoD:**
        - Vue.js app gọi API login.
        - Lưu token (giả) vào localStorage hoặc Vuex/Pinia.
        - Các request tiếp theo đến backend (ví dụ: khi gửi tin nhắn chat) đính kèm token này trong header.
        - Backend (mô phỏng) kiểm tra sự tồn tại của token.

## Phase 6: Hoàn thiện, Kiểm thử Chuyên sâu & Chuẩn bị Triển khai

### Task 6.1 (F6.1): Kiểm thử end-to-end toàn diện
- [ ] **Task:** Thực hiện tất cả các kịch bản kiểm thử thủ công (MTx.y) từ các phase trước.
    - **DoD:**
        - Mỗi kịch bản được thực hiện trên hệ thống đã tích hợp đầy đủ.
        - Kết quả (pass/fail) được ghi nhận.
        - Các lỗi phát hiện được tạo thành issue riêng để xử lý.

### Task 6.2 (F6.2): Sửa lỗi và cải thiện độ ổn định
- [ ] **Task:** Ưu tiên và sửa các lỗi đã phát hiện từ F6.1.
    - **DoD:**
        - Các lỗi nghiêm trọng và lỗi ảnh hưởng đến các luồng chính được sửa.
        - Hệ thống hoạt động ổn định hơn.

### Task 6.3 (F6.3): Cải thiện xử lý lỗi và phản hồi UI
- [ ] **Task:** Rà soát các điểm có thể xảy ra lỗi trong backend.
    - **DoD:**
        - Orchestrator và các TEAM agent có cơ chế bắt lỗi (try-catch) tốt hơn.
        - Các lỗi được log chi tiết hơn.
        - Các lỗi được trả về cho frontend dưới dạng cấu trúc (ví dụ: JSON với message lỗi).
- [ ] **Task:** Cập nhật frontend để hiển thị thông báo lỗi thân thiện.
    - **DoD:**
        - Thay vì chỉ log lỗi ra console, frontend hiển thị thông báo lỗi cho người dùng trong UI (ví dụ: toast notification, hoặc message trong chat).

### Task 6.4 (F6.4): Rà soát và tối ưu hóa prompt LLM
- [ ] **Task:** Thu thập các prompt đã sử dụng.
    - **DoD:** Danh sách các prompt template được tổng hợp.
- [ ] **Task:** Thử nghiệm và tinh chỉnh các prompt.
    - **DoD:**
        - Với mỗi prompt, thử nghiệm với nhiều input khác nhau.
        - Điều chỉnh từ ngữ, cấu trúc prompt để cải thiện chất lượng, độ chính xác và tính hữu ích của phản hồi LLM.
        - Các prompt đã tối ưu được cập nhật trong `PromptFormatterModule`.

### Task 6.5 (F6.5): Tạo tài liệu hướng dẫn người dùng
- [ ] **Task:** Viết tài liệu hướng dẫn cài đặt.
    - **DoD:**
        - Hướng dẫn các bước để cài đặt backend (Python dependencies, Neo4j).
        - Hướng dẫn các bước để chạy frontend (Node.js, Vue CLI/Vite).
- [ ] **Task:** Viết tài liệu hướng dẫn sử dụng các tính năng.
    - **DoD:**
        - Mô tả cách scan project, review PR, sử dụng Q&A.
        - Hướng dẫn cách sử dụng màn hình Settings để cấu hình LLM.
        - Giải thích ý nghĩa của các thông tin trong báo cáo.

### Task 6.6: Chuẩn bị script/hướng dẫn triển khai cơ bản
- [ ] **Task:** (Tùy chọn) Tạo Dockerfile cho backend.
    - **DoD:**
        - Dockerfile được tạo, có thể build image thành công.
        - Có thể chạy container từ image.
- [ ] **Task:** (Tùy chọn) Tạo Dockerfile cho frontend (hoặc hướng dẫn build static files).
    - **DoD:** Tương tự cho frontend.
- [ ] **Task:** Viết hướng dẫn triển khai cơ bản (ví dụ: sử dụng Docker Compose nếu có).
    - **DoD:** Tài liệu mô tả các bước để triển khai ứng dụng trên một server.

### Task 6.7: Đảm bảo PAT được xử lý an toàn
- [ ] **Task:** Rà soát code liên quan đến xử lý PAT.
    - **DoD:**
        - Xác minh PAT không bao giờ được ghi vào log file.
        - Xác minh PAT được xóa khỏi bộ nhớ của `PATHandlerModule` ngay sau khi tác vụ Git hoàn thành.
        - Nếu PAT được truyền giữa các agent/module, đảm bảo nó được truyền một cách an toàn và không bị lộ.
        - Xác minh PAT không hiển thị trong lịch sử chat hoặc UI sau khi nhập.