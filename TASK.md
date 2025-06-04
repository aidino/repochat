# Danh sách Công việc Chi tiết Dự án RepoChat v1.0

**Tài liệu Kế hoạch Tham chiếu:** `PLANNING.md`
**Tài liệu Thiết kế Tham chiếu:** `DESIGN.md` 

## Phase 1: Thiết lập Backend Cốt lõi & Thu thập Dữ liệu Cơ bản

### Task 1.1 (F1.1): Khởi tạo Orchestrator Agent và thiết lập logging cơ bản ✅ COMPLETED & ENHANCED
- [x] **Task:** Thiết lập cấu trúc project Python cho Orchestrator Agent.
    - **DoD:**
        - ✅ Cấu trúc thư mục cơ bản cho Orchestrator được tạo.
        - ✅ Một class `OrchestratorAgent` rỗng hoặc với hàm khởi tạo cơ bản được tạo.
        - ✅ Thư viện logging (ví dụ: `logging` của Python) được cấu hình để ghi log ra console với các level cơ bản (INFO, ERROR).
        - ✅ Có thể chạy một script đơn giản để khởi tạo Orchestrator và thấy log output.
- [x] **Task:** Định nghĩa cấu trúc `TaskDefinition` ban đầu.
    - **DoD:**
        - ✅ Một Pydantic model hoặc data class `TaskDefinition` được tạo, ban đầu chỉ chứa trường `repository_url: str`.
- [x] **Enhanced Requirements (Added 6/6/2025):**
    - ✅ **Docker Compose Setup:** Complete containerized development environment with Neo4j and backend services
    - ✅ **Enhanced Logging:** Extensive structured logging with JSON format, file rotation, performance metrics, and debugging capabilities

**Ngày hoàn thành:** 4/6/2025 (Original) | 6/6/2025 (Enhanced)  
**Các file đã tạo:**
- `backend/src/orchestrator/orchestrator_agent.py` - Enhanced OrchestratorAgent class với extensive logging
- `backend/src/shared/models/task_definition.py` - TaskDefinition Pydantic model 
- `backend/src/shared/utils/logging_config.py` - Advanced structured logging configuration
- `backend/requirements.txt` - Dependencies cho dự án (fixed ast module issue)
- `backend/main.py` - Production-ready FastAPI application với health checks
- `backend/Dockerfile` - Multi-stage Docker build cho development/production
- `backend/.dockerignore` - Optimized Docker build context
- `docker-compose.yml` - Complete environment với Neo4j, backend, networking
- `scripts/setup-dev.sh` - Automated development environment setup
- `docs/DOCKER_DEVELOPMENT.md` - Comprehensive Docker development guide
- `env.example` - Environment template với OpenAI và Neo4j config
- `backend/tests/test_task_definition.py` - Unit tests cho TaskDefinition
- `backend/tests/test_orchestrator_agent.py` - Enhanced unit tests cho OrchestratorAgent  
**Kết quả test:** Tất cả 18 unit tests PASS ✅
**Docker Status:** All containers healthy (Neo4j + Backend) ✅
**APIs Working:** Health check, task creation, status retrieval, stats ✅  
**Enhanced Features:**
- Structured JSON logging với datetime handling
- Performance metrics tracking  
- Function entry/exit logging
- Log rotation và multiple log files (general + debug)
- Docker-first development workflow
- One-command environment setup
- Debugging support với port 5678
- Health checks cho all services

**Manual Test Scenarios:**
1. **Docker Environment Setup:**
   ```bash
   ./scripts/setup-dev.sh  # Should setup complete environment
   docker compose ps       # Should show all containers healthy
   ```

2. **API Testing:**
   ```bash
   curl http://localhost:8000/health  # Should return healthy status
   curl http://localhost:8000/        # Should return service info
   curl http://localhost:8000/stats   # Should return agent statistics
   
   # Create task
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/user/test"}'
   
   # Get task status (use execution_id from above)
   curl http://localhost:8000/tasks/{execution_id}
   ```

3. **Logging Verification:**
   ```bash
   ls logs/                                    # Should show log files
   tail -5 logs/repochat_20250604.log         # Should show JSON structured logs
   tail -10 logs/repochat_debug_20250604.log  # Should show debug logs
   ```

4. **Development Workflow:**
   ```bash
   docker compose exec backend bash           # Should access backend container
   docker compose logs backend               # Should show application logs
   # Debug port 5678 should be available for IDE attachment
   ```

### Task 1.2 (F1.2): `TEAM Data Acquisition` (`GitOperationsModule`): Thực hiện clone nông Git repository công khai ✅ COMPLETED
- [x] **Task:** Viết module Python `GitOperationsModule` có chức năng clone repository.
    - **DoD:**
        - ✅ Module có một hàm nhận `repository_url` làm đầu vào.
        - ✅ Hàm sử dụng thư viện `gitpython` để thực hiện `git clone --depth 1 <repository_url>` vào một thư mục tạm thời được chỉ định hoặc tự tạo.
        - ✅ Hàm trả về đường dẫn đến thư mục đã clone thành công.
        - ✅ Xử lý lỗi cơ bản nếu URL không hợp lệ hoặc không thể clone (ví dụ: log lỗi).

**Implementation Highlights:**
- **GitOperationsModule** với shallow cloning (--depth 1) cho efficiency
- **Enhanced validation** cho URL formats (HTTP/HTTPS/SSH protocols)
- **Comprehensive error handling** cho GitCommandError, PermissionError, OSError
- **Repository cleanup functionality** và automatic temp directory management
- **Extensive logging** với structured format và performance metrics
- **Repository stats tracking** và directory size calculations
- **25 unit tests** covering all scenarios (success, error, edge cases)
- **Integration với OrchestratorAgent** - automatic repository cloning trong task processing

**Enhanced Features:**
- Unique path generation với microsecond precision + random suffix
- Repository info extraction (branch, commit, size, remote URL)
- Failed clone cleanup
- SSH URL support (git@host:path format)
- Protocol validation (reject FTP, etc.)
- Comprehensive structured logging với function entry/exit tracking

**Manual Test Scenarios cho Task 1.2:**

1. **Basic Git Operations:**
   ```bash
   # Test valid GitHub repository cloning
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/octocat/Hello-World.git"}'
   
   # Get task status to verify successful cloning
   curl http://localhost:8000/tasks/{execution_id}
   
   # Should return status: "completed" with repository_path and clone metrics
   ```

2. **SSH URL Support:**
   ```bash
   # Test SSH URL validation (will fail clone due to no SSH key, but validation passes)
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "git@github.com:octocat/Hello-World.git"}'
   ```

3. **Error Handling:**
   ```bash
   # Test invalid URL
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "not-a-valid-url"}'
   # Should return 422 Validation Error for invalid URL
   
   # Test non-existent repository
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/nonexistent/repo.git"}'
   # Should complete but log clone error in task.errors
   
   # Test unsupported protocol
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "ftp://example.com/repo.git"}'
   # Should return validation error
   ```

4. **Repository Stats & Cleanup:**
   ```bash
   # Check agent stats after cloning
   curl http://localhost:8000/stats
   # Should show successful_tasks increment
   
   # Check logs for repository cloning details
   tail -20 logs/repochat_20250604.log | grep clone_repository
   # Should show detailed clone operation logs with timing metrics
   ```

5. **Performance & Metrics:**
   ```bash
   # Test multiple repositories to check performance
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/microsoft/vscode.git"}'
   
   # Check logs for performance metrics
   tail -10 logs/repochat_20250604.log | grep performance_metric
   # Should show clone timing và repository size metrics
   ```

6. **Docker Container Direct Testing:**
   ```bash
   # Test GitOperationsModule directly in container
   docker compose exec backend python -c "
   from teams.data_acquisition import GitOperationsModule
   git_ops = GitOperationsModule()
   result = git_ops.clone_repository('https://github.com/octocat/Hello-World.git')
   print(f'Clone result: {result}')
   stats = git_ops.get_repository_stats()
   print(f'Stats: {stats}')
   git_ops.cleanup_repository(result)
   print('Cleanup completed')
   "
   ```

**Current Status:** Task 1.2 COMPLETED with enhanced functionality (6/6/2025)
- 25/25 unit tests PASSING ✅
- Integration với OrchestratorAgent working ✅  
- Real-world testing với octocat/Hello-World repository successful ✅
- Comprehensive error handling và logging implemented ✅
- Performance metrics và cleanup functionality verified ✅

### Task 1.3 (F1.3): `TEAM Data Acquisition` (`LanguageIdentifierModule`): Xác định ngôn ngữ lập trình chính
- [ ] **Task:** Viết module Python `LanguageIdentifierModule` để xác định ngôn ngữ.
    - **DoD:**
        - Module có một hàm nhận đường dẫn đến thư mục code đã clone.
        - Hàm duyệt qua các file trong thư mục, xác định ngôn ngữ dựa trên phần mở rộng file (ví dụ: `.java` -> "java", `.py` -> "python", `.kt` -> "kotlin", `.dart` -> "dart").
        - Hàm có thể tham khảo các file cấu hình phổ biến (ví dụ: `pom.xml`, `build.gradle`, `pubspec.yaml`, `requirements.txt`) để tăng độ chính xác (tùy chọn cho DoD ban đầu, có thể chỉ dựa vào extension trước).
        - Hàm trả về một danh sách các ngôn ngữ được phát hiện (ví dụ: `["java", "python"]`).

### Task 1.4 (F1.4): `TEAM Data Acquisition` (`DataPreparationModule`): Đóng gói `ProjectDataContext`
- [ ] **Task:** Định nghĩa cấu trúc `ProjectDataContext`.
    - **DoD:**
        - Một Pydantic model hoặc data class `ProjectDataContext` được tạo, chứa các trường `cloned_code_path: str` và `detected_languages: List[str]`.
- [ ] **Task:** Viết module Python `DataPreparationModule`.
    - **DoD:**
        - Module có một hàm nhận kết quả từ `GitOperationsModule` (đường dẫn code) và `LanguageIdentifierModule` (danh sách ngôn ngữ).
        - Hàm tạo và trả về một instance của `ProjectDataContext`.

### Task 1.5 (F1.5): Orchestrator Agent: Tiếp nhận yêu cầu và kích hoạt `TEAM Data Acquisition`
- [ ] **Task:** Mở rộng `OrchestratorAgent` để xử lý `TaskDefinition`.
    - **DoD:**
        - `OrchestratorAgent` có một method (ví dụ: `handle_scan_project_task`) nhận `TaskDefinition` (chứa `repository_url`).
        - Method này gọi tuần tự các chức năng của `GitOperationsModule` và `LanguageIdentifierModule` (có thể thông qua một facade `TeamDataAcquisition`).
        - Kết quả `ProjectDataContext` được log ra.
        - Giao tiếp giữa Orchestrator và TDA được mô phỏng bằng cách gọi trực tiếp các module trong phase này.

### Task 1.6 (F1.6): `TEAM Data Acquisition` (`PATHandlerModule`): Mô phỏng quy trình yêu cầu PAT
- [ ] **Task:** Viết module Python `PATHandlerModule` (mô phỏng).
    - **DoD:**
        - Module có một hàm (ví dụ: `request_pat_if_needed`) nhận một `repository_url`.
        - Nếu URL được coi là "private" (ví dụ: chứa một từ khóa nhất định hoặc dựa trên một flag), hàm sẽ in ra console một lời nhắc yêu cầu người dùng nhập PAT.
        - Hàm trả về PAT (giả) đã nhập hoặc `None`.
        - `GitOperationsModule` được cập nhật để (mô phỏng) sử dụng PAT này nếu được cung cấp (ví dụ: chỉ log ra là "Sử dụng PAT: [giá trị PAT]").

## Phase 2: Xây dựng Code Knowledge Graph (CKG) Ban đầu

### Task 2.1 (F2.1): `TEAM CKG Operations`: Thiết lập kết nối đến Neo4j
- [ ] **Task:** Cài đặt Neo4j Community Edition.
    - **DoD:**
        - Neo4j được cài đặt và chạy cục bộ.
        - Có thể truy cập Neo4j Browser.
- [ ] **Task:** Viết module/utility để kết nối Neo4j từ Python.
    - **DoD:**
        - Một module Python có các hàm để thiết lập session với Neo4j sử dụng thư viện `neo4j`.
        - Có thể thực thi một truy vấn Cypher đơn giản (ví dụ: `RETURN 1`) và nhận kết quả.

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

### Task 6.6 (F6.6): Chuẩn bị script/hướng dẫn triển khai cơ bản
- [ ] **Task:** (Tùy chọn) Tạo Dockerfile cho backend.
    - **DoD:**
        - Dockerfile được tạo, có thể build image thành công.
        - Có thể chạy container từ image.
- [ ] **Task:** (Tùy chọn) Tạo Dockerfile cho frontend (hoặc hướng dẫn build static files).
    - **DoD:** Tương tự cho frontend.
- [ ] **Task:** Viết hướng dẫn triển khai cơ bản (ví dụ: sử dụng Docker Compose nếu có).
    - **DoD:** Tài liệu mô tả các bước để triển khai ứng dụng trên một server.

### Task 6.7 (F6.7): Đảm bảo PAT được xử lý an toàn
- [ ] **Task:** Rà soát code liên quan đến xử lý PAT.
    - **DoD:**
        - Xác minh PAT không bao giờ được ghi vào log file.
        - Xác minh PAT được xóa khỏi bộ nhớ của `PATHandlerModule` ngay sau khi tác vụ Git hoàn thành.
        - Nếu PAT được truyền giữa các agent/module, đảm bảo nó được truyền một cách an toàn và không bị lộ.
        - Xác minh PAT không hiển thị trong lịch sử chat hoặc UI sau khi nhập.