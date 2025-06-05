# 📊 Phase 1 - Luồng Dữ liệu và Sequence Diagram

**Tài liệu Phân tích**: RepoChat v1.0 Phase 1 Complete Data Flow Analysis  
**Ngày tạo**: 2025-06-05  
**Phiên bản**: 1.0  

## 🎯 Tổng quan Phase 1

Phase 1 đã hoàn thành thành công **Foundation Infrastructure** với 6 tasks chính, tạo nền tảng vững chắc cho **TEAM Data Acquisition** và **OrchestratorAgent**.

### ✅ Các Tính năng Đã hoàn thành

1. **Logging System** - Structured logging toàn hệ thống
2. **GitOperationsModule** - Git repository operations
3. **LanguageIdentifierModule** - Programming language detection  
4. **DataPreparationModule** - ProjectDataContext creation
5. **OrchestratorAgent** - Central coordination với scan project workflow
6. **PATHandlerModule** - Private repository access handling

---

## 🔄 Main Workflow: Scan Project Task

### Sequence Diagram - Scan Project Workflow

```mermaid
sequenceDiagram
    participant User as 👤 User/CLI
    participant Orch as 🎯 OrchestratorAgent
    participant PAT as 🔐 PATHandlerModule
    participant Git as 📦 GitOperationsModule
    participant Lang as 🔍 LanguageIdentifierModule
    participant Data as 📊 DataPreparationModule
    participant Log as 📝 LoggingSystem

    User->>Orch: TaskDefinition(repository_url)
    Orch->>Log: Log task initiation
    
    Note over Orch: Step 1: PAT Requirements Check
    Orch->>PAT: request_pat_if_needed(repository_url)
    
    alt Private Repository Detected
        PAT->>User: Request PAT input (secure)
        User->>PAT: Provide PAT
        PAT->>PAT: Cache PAT for session
        PAT-->>Orch: authenticated_url
    else Public Repository
        PAT-->>Orch: original_url
    end
    
    Note over Orch: Step 2: Git Repository Cloning
    Orch->>Git: clone_repository(url, auth_if_needed)
    Git->>Git: Shallow clone (depth=1)
    Git->>Log: Log clone metrics
    Git-->>Orch: cloned_path
    
    Note over Orch: Step 3: Language Identification
    Orch->>Lang: identify_languages(cloned_path)
    Lang->>Lang: Scan files & analyze patterns
    Lang->>Log: Log detection results
    Lang-->>Orch: detected_languages[]
    
    Note over Orch: Step 4: Data Context Creation
    Orch->>Data: create_project_context(path, languages, url)
    Data->>Data: Build ProjectDataContext
    Data->>Log: Log context creation
    Data-->>Orch: ProjectDataContext
    
    Orch->>Log: Log workflow completion
    Orch-->>User: ProjectDataContext result
    
    Note over PAT: Security: Clear PAT cache
    PAT->>PAT: clear_pat_cache()
```

---

## 📋 Data Flow Analysis

### 1. 🔐 PAT Handling Data Flow

```mermaid
flowchart TD
    A[Repository URL] --> B{Is Private Repository?}
    B -->|Yes| C[Request PAT from User]
    B -->|No| D[Use Original URL]
    
    C --> E[Secure Input via getpass]
    E --> F[Cache PAT in Memory]
    F --> G[Build Authenticated URL]
    G --> H[Return Auth URL]
    
    D --> I[Return Original URL]
    
    H --> J[Git Operations]
    I --> J
    J --> K[Clear PAT Cache for Security]
    
    style C fill:#ffcccb
    style F fill:#ffffcc
    style K fill:#90EE90
```


**Data Structures:**
```python
# Input
repository_url: str = "https://github.com/user/repo.git"

# Private repository patterns detected:
private_patterns = [
    "*.private.*", "*.corp.*", "*.internal.*", 
    "enterprise.github.com", "git@*"
]

# Output for private repos
authenticated_url: str = "https://token:PAT@github.com/user/repo.git"

# Security: PAT cleared after use
pat_cache = {}  # Cleared immediately after clone
```

### 2. 📦 Git Operations Data Flow

```mermaid
flowchart TD
    A[URL Input] --> B[Validate Git URL]
    B --> C[Create Temp Directory]
    C --> D[Execute Shallow Clone]
    D --> E{Clone Successful?}
    
    E -->|Yes| F[Verify .git Directory]
    E -->|No| G[Log Error & Cleanup]
    
    F --> H[Calculate Metrics]
    H --> I[Log Success Metrics]
    I --> J[Return Clone Path]
    
    G --> K[Return None]
    
    style D fill:#e1f5fe
    style H fill:#f3e5f5
    style I fill:#e8f5e8
```

**Performance Metrics Tracked:**
```python
clone_metrics = {
    "clone_duration_ms": 1234,
    "repository_size_mb": 5.2,
    "clone_depth": 1,
    "files_count": 156,
    "temp_directory": "/tmp/repochat_abc123"
}
```

### 3. 🔍 Language Detection Data Flow

```mermaid
flowchart TD
    A[Repository Path] --> B[Scan All Files]
    B --> C[Group by Extensions]
    C --> D[Analyze File Patterns]
    D --> E[Count Files per Language]
    E --> F[Apply Detection Rules]
    F --> G[Calculate Statistics]
    G --> H[Determine Primary Language]
    H --> I[Return Language List]
    
    subgraph "Detection Rules"
        J[File Extensions]
        K[Config Files]
        L[Framework Markers]
    end
    
    F --> J
    F --> K  
    F --> L
    
    style E fill:#fff3e0
    style H fill:#e3f2fd
```

**Language Statistics Output:**
```python
language_stats = {
    "python": {"count": 45, "percentage": 65.2},
    "javascript": {"count": 18, "percentage": 26.1}, 
    "html": {"count": 6, "percentage": 8.7},
    "total_files": 69,
    "primary_language": "python"
}
```

### 4. 📊 ProjectDataContext Creation Flow

```mermaid
flowchart TD
    A[Clone Path] --> E[ProjectDataContext Builder]
    B[Languages List] --> E
    C[Repository URL] --> E
    D[Statistics] --> E
    
    E --> F[Validate Inputs]
    F --> G[Build Context Object]
    G --> H[Calculate Properties]
    H --> I[Add Metadata]
    I --> J[Return ProjectDataContext]
    
    subgraph "Context Properties"
        K[repository_url]
        L[cloned_code_path] 
        M[detected_languages]
        N[primary_language]
        O[language_count]
        P[has_languages]
        Q[created_at]
    end
    
    G --> K
    G --> L
    G --> M
    G --> N
    G --> O
    G --> P
    G --> Q
    
    style E fill:#f1f8e9
    style J fill:#e8f5e8
```

**ProjectDataContext Structure:**
```python
@dataclass
class ProjectDataContext:
    repository_url: str
    cloned_code_path: str
    detected_languages: List[str]
    primary_language: Optional[str]
    language_count: int
    has_languages: bool
    created_at: datetime
    metadata: Dict[str, Any]
```

---

## 🎯 OrchestratorAgent Coordination Flow

### Main Orchestration Sequence

```mermaid
sequenceDiagram
    participant API as 🌐 External API/CLI
    participant Orch as 🎯 OrchestratorAgent
    participant Stats as 📊 Agent Statistics
    participant Teams as 👥 TEAM Modules
    participant Log as 📝 Logging System

    API->>Orch: initialize()
    Orch->>Stats: Initialize statistics tracking
    Orch->>Log: Register agent with unique ID
    
    API->>Orch: handle_scan_project_task(TaskDefinition)
    Orch->>Stats: Increment active_tasks_count
    Orch->>Log: Log task start with task_id
    
    loop 4-Step Workflow
        Orch->>Teams: Execute step (PAT/Git/Lang/Data)
        Teams->>Log: Log step execution
        Teams-->>Orch: Step result
        Orch->>Stats: Update step completion
    end
    
    Orch->>Stats: Increment successful_tasks
    Orch->>Log: Log workflow completion
    Orch-->>API: ProjectDataContext result
    
    API->>Orch: get_agent_stats()
    Orch->>Stats: Compile current statistics
    Stats-->>Orch: Agent statistics object
    Orch-->>API: Statistics summary
    
    API->>Orch: shutdown()
    Orch->>Log: Log agent shutdown
    Orch->>Stats: Final statistics capture
```

### Agent Statistics Tracking

```python
agent_statistics = {
    "agent_id": "orch_abc12345",
    "uptime_seconds": 127.45,
    "statistics": {
        "successful_tasks": 3,
        "failed_tasks": 0,
        "active_tasks_count": 0,
        "total_execution_time_ms": 45230
    },
    "performance_metrics": {
        "avg_task_duration_ms": 15076.7,
        "last_task_duration_ms": 12450
    }
}
```

---

## 🔒 Security & Error Handling Flows

### PAT Security Flow

```mermaid
flowchart TD
    A[PAT Request] --> B[Secure Input via getpass]
    B --> C[Memory-only Storage]
    C --> D[Build Auth URL]
    D --> E[Git Operation]
    E --> F[Immediate Cache Clear]
    F --> G[Zero PAT Persistence]
    
    style B fill:#ffebee
    style C fill:#fff3e0
    style F fill:#e8f5e8
    style G fill:#4caf50,color:#fff
```

### Error Handling Cascade

```mermaid
flowchart TD
    A[Operation Start] --> B{Error Occurred?}
    B -->|No| C[Continue Workflow]
    B -->|Yes| D[Log Error Details]
    D --> E[Cleanup Resources]
    E --> F[Update Statistics]
    F --> G[Return Error Response]
    
    subgraph "Error Types"
        H[Network Errors]
        I[Authentication Errors]
        J[File System Errors]
        K[Validation Errors]
    end
    
    D --> H
    D --> I
    D --> J
    D --> K
    
    style D fill:#ffcdd2
    style E fill:#fff3e0
    style G fill:#f44336,color:#fff
```

---

## 📈 Performance Metrics & Monitoring

### Logging Data Flow

```mermaid
flowchart TD
    A[Code Execution] --> B[Structured Logging]
    B --> C{Log Level}
    
    C -->|DEBUG| D[Debug Log File]
    C -->|INFO+| E[Main Log File]
    
    subgraph "Log Enrichment"
        F[Agent Context]
        G[Performance Metrics]
        H[Function Tracing]
        I[Error Context]
    end
    
    B --> F
    B --> G
    B --> H
    B --> I
    
    D --> J[Log Analysis Tools]
    E --> J
    J --> K[Monitoring Dashboard]
    
    style B fill:#e3f2fd
    style K fill:#4caf50,color:#fff
```

### Performance Tracking Points

```python
performance_checkpoints = {
    "task_initiation": "timestamp_ms",
    "pat_check_duration": "duration_ms", 
    "git_clone_duration": "duration_ms",
    "language_detection_duration": "duration_ms",
    "context_creation_duration": "duration_ms",
    "total_task_duration": "duration_ms"
}
```

---

## 🧪 Testing Data Flows

### Unit Test Coverage Flow

```mermaid
flowchart TD
    A[Source Code] --> B[Unit Tests]
    B --> C[Integration Tests] 
    C --> D[Manual Test Scenarios]
    
    subgraph "Test Categories"
        E[Expected Use Cases]
        F[Edge Cases]
        G[Failure Scenarios]
        H[Performance Tests]
    end
    
    B --> E
    B --> F
    B --> G
    C --> H
    
    D --> I[Test Results]
    I --> J{All Tests Pass?}
    J -->|Yes| K[Phase 1 Complete ✅]
    J -->|No| L[Fix & Retry]
    L --> A
    
    style K fill:#4caf50,color:#fff
    style L fill:#ff9800,color:#fff
```

---

## 🚀 Ready for Phase 2

Phase 1 đã tạo foundation vững chắc với:

- ✅ **Complete Data Acquisition Pipeline**
- ✅ **Robust Error Handling & Security**  
- ✅ **Comprehensive Logging & Monitoring**
- ✅ **Extensible Agent Architecture**
- ✅ **100+ Test Coverage**

**Next**: Phase 2 sẽ xây dựng **Code Knowledge Graph** dựa trên ProjectDataContext từ Phase 1.

---

## 📚 References

- **DESIGN.md**: Kiến trúc tổng thể hệ thống
- **PLANNING.md**: Kế hoạch triển khai từng phase
- **TASK.md**: Chi tiết progress và DoD requirements
- **Source Code**: `backend/src/` - Implementation details
- **Tests**: `backend/tests/` - Validation scenarios 