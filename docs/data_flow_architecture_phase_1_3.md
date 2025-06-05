# RepoChat Data Flow Architecture - Phase 1-3

## Overview

This document describes the complete data flow architecture for RepoChat system from Phase 1 through Phase 3, covering:

- **Phase 1**: Data Acquisition & CKG Operations
- **Phase 2**: Code Analysis & LLM Services  
- **Phase 3**: Orchestrator Integration & PR Impact Analysis

## System Architecture Components

### Phase 1: Data Acquisition & CKG Operations

```mermaid
graph TB
    subgraph "TEAM Data Acquisition"
        GIT[GitOperationsModule]
        LANG[LanguageIdentifierModule]
        DATA[DataPreparationModule]
        PAT[PATHandlerModule]
    end
    
    subgraph "TEAM CKG Operations"
        COORD[CodeParserCoordinatorModule]
        JAVA[JavaParser]
        PYTHON[PythonParser] 
        KOTLIN[KotlinParser]
        DART[DartParser]
        AST2CKG[ASTtoCKGBuilderModule]
        CKG_QUERY[CKGQueryInterfaceModule]
        NEO4J[Neo4jConnectionModule]
    end
    
    subgraph "Data Models"
        PDC[ProjectDataContext]
        CE[CodeEntity]
        PR[ParseResult]
    end
    
    GIT --> PDC
    LANG --> PDC
    DATA --> PDC
    
    COORD --> JAVA
    COORD --> PYTHON
    COORD --> KOTLIN
    COORD --> DART
    
    JAVA --> CE
    PYTHON --> CE
    KOTLIN --> CE
    DART --> CE
    
    AST2CKG --> NEO4J
    CKG_QUERY --> NEO4J
```

### Phase 2: Code Analysis & LLM Services

```mermaid
graph TB
    subgraph "TEAM Code Analysis"
        ARCH[ArchitecturalAnalyzerModule]
        LLM_SUPPORT[LLMAnalysisSupportModule]
        PR_IMPACT[PRImpactAnalyzerModule]
        STATIC[StaticAnalysisIntegratorModule]
    end
    
    subgraph "TEAM LLM Services"
        GATEWAY[LLMGatewayModule]
        TEAM_LLM[TeamLLMServices]
        PROVIDER[LLMProviderAbstractionLayer]
        OPENAI[OpenAIProvider]
    end
    
    subgraph "Analysis Models"
        AF[AnalysisFinding]
        AR[AnalysisResult]
        LSR[LLMServiceRequest]
        LSRESP[LLMServiceResponse]
    end
    
    ARCH --> AF
    PR_IMPACT --> AF
    LLM_SUPPORT --> LSR
    
    GATEWAY --> TEAM_LLM
    TEAM_LLM --> PROVIDER
    PROVIDER --> OPENAI
    
    LSR --> GATEWAY
    GATEWAY --> LSRESP
```

### Phase 3: Orchestrator Integration

```mermaid
graph TB
    subgraph "Orchestrator Layer"
        ORCH[OrchestratorAgent]
        TD[TaskDefinition]
        TR[TaskResult]
    end
    
    subgraph "TEAM Integration Points"
        DA_INT[Data Acquisition Integration]
        CKG_INT[CKG Operations Integration]
        CA_INT[Code Analysis Integration]
        LLM_INT[LLM Services Integration]
    end
    
    ORCH --> TD
    ORCH --> DA_INT
    ORCH --> CKG_INT
    ORCH --> CA_INT
    ORCH --> LLM_INT
    
    DA_INT --> GIT
    CKG_INT --> COORD
    CA_INT --> ARCH
    LLM_INT --> GATEWAY
    
    ORCH --> TR
```

## Complete Data Flow Diagram

```mermaid
flowchart TD
    %% External Input
    USER[User Request]
    REPO_URL[Repository URL]
    PR_INFO[PR Information]
    
    %% Phase 1: Data Acquisition
    USER --> ORCH[OrchestratorAgent]
    REPO_URL --> GIT[GitOperationsModule]
    
    GIT --> |Clone Repo| LOCAL_CODE[Local Code Repository]
    LOCAL_CODE --> LANG[LanguageIdentifierModule]
    LANG --> |Detected Languages| PDC[ProjectDataContext]
    
    LOCAL_CODE --> DATA[DataPreparationModule]
    DATA --> |Prepared Data| PDC
    
    %% CKG Operations
    PDC --> COORD[CodeParserCoordinatorModule]
    
    COORD --> |Java Files| JAVA[JavaParser]
    COORD --> |Python Files| PYTHON[PythonParser]
    COORD --> |Kotlin Files| KOTLIN[KotlinParser]
    COORD --> |Dart Files| DART[DartParser]
    
    JAVA --> |CodeEntities| AST2CKG[ASTtoCKGBuilderModule]
    PYTHON --> |CodeEntities| AST2CKG
    KOTLIN --> |CodeEntities| AST2CKG
    DART --> |CodeEntities| AST2CKG
    
    AST2CKG --> |Nodes & Relationships| NEO4J[Neo4j Database]
    
    %% Phase 2: Code Analysis
    PDC --> ARCH[ArchitecturalAnalyzerModule]
    ARCH --> |Circular Dependencies| FINDINGS[AnalysisFindings]
    
    PDC --> PR_IMPACT[PRImpactAnalyzerModule]
    PR_INFO --> PR_DIFF[PRDiffInfo]
    PR_DIFF --> PDC
    PR_IMPACT --> |Impact Analysis| FINDINGS
    
    %% LLM Integration
    FINDINGS --> LLM_SUPPORT[LLMAnalysisSupportModule]
    LLM_SUPPORT --> |LLM Request| GATEWAY[LLMGatewayModule]
    GATEWAY --> |API Call| OPENAI[OpenAI API]
    OPENAI --> |LLM Response| GATEWAY
    GATEWAY --> |Enhanced Analysis| FINDINGS
    
    %% Phase 3: Orchestration
    ORCH --> |Task Definition| EXECUTION[Task Execution]
    EXECUTION --> |Coordinate| ARCH
    EXECUTION --> |Coordinate| PR_IMPACT
    EXECUTION --> |Route| GATEWAY
    
    FINDINGS --> |Aggregate| RESULTS[Final Results]
    RESULTS --> USER
    
    %% Static Analysis Placeholder
    PDC --> STATIC[StaticAnalysisIntegratorModule]
    STATIC --> |Placeholder| FINDINGS
    
    %% CKG Query Interface
    NEO4J --> CKG_QUERY[CKGQueryInterfaceModule]
    CKG_QUERY --> |Graph Queries| ARCH
    CKG_QUERY --> |Impact Queries| PR_IMPACT
```

## Data Flow Descriptions

### 1. Repository Acquisition Flow

```
User Request → OrchestratorAgent → GitOperationsModule → Local Repository
```

**Data Types:**
- Input: Repository URL, Authentication tokens
- Processing: Git clone operations, repository validation
- Output: ProjectDataContext with cloned code path

### 2. Language Detection Flow

```
Local Repository → LanguageIdentifierModule → ProjectDataContext
```

**Data Types:**
- Input: File system paths, file extensions, content analysis
- Processing: Language detection algorithms, confidence scoring
- Output: Detected languages list with confidence scores

### 3. Code Parsing Flow

```
ProjectDataContext → CodeParserCoordinatorModule → Language Parsers → CodeEntities
```

**Data Types:**
- Input: Source code files by language
- Processing: AST parsing, entity extraction, relationship identification
- Output: Structured CodeEntity objects with metadata

### 4. CKG Construction Flow

```
CodeEntities → ASTtoCKGBuilderModule → Neo4j Database
```

**Data Types:**
- Input: CodeEntity objects with relationships
- Processing: Graph node creation, relationship mapping, schema validation
- Output: Neo4j graph database with code knowledge graph

### 5. Architectural Analysis Flow

```
ProjectDataContext + CKG → ArchitecturalAnalyzerModule → AnalysisFindings
```

**Data Types:**
- Input: Project structure, dependency information, CKG queries
- Processing: Pattern detection, circular dependency analysis, architectural smells
- Output: AnalysisFinding objects with severity levels

### 6. PR Impact Analysis Flow

```
ProjectDataContext + PRDiffInfo → PRImpactAnalyzerModule → Impact AnalysisFindings
```

**Data Types:**
- Input: PR diff information, changed files, function modifications
- Processing: Impact scope analysis, caller/callee identification, risk assessment
- Output: Impact-specific AnalysisFinding objects

### 7. LLM Enhancement Flow

```
AnalysisFindings → LLMAnalysisSupportModule → LLMGatewayModule → Enhanced Analysis
```

**Data Types:**
- Input: Raw analysis findings, code snippets, context information
- Processing: Prompt engineering, API requests, response parsing
- Output: LLM-enhanced analysis with explanations and recommendations

### 8. Orchestration Coordination Flow

```
TaskDefinition → OrchestratorAgent → TEAM Coordination → TaskResult
```

**Data Types:**
- Input: Task specifications, user preferences, configuration
- Processing: Component coordination, data flow management, error handling
- Output: Aggregated results with execution metadata

## Data Models and Relationships

### Core Data Models

```mermaid
erDiagram
    ProjectDataContext {
        string cloned_code_path
        list detected_languages
        string repository_url
        PRDiffInfo pr_diff_info
        datetime created_at
    }
    
    PRDiffInfo {
        string pr_id
        string base_branch
        string head_branch
        list changed_files
        dict file_changes
        list function_changes
    }
    
    CodeEntity {
        string entity_id
        string name
        CodeEntityType entity_type
        string file_path
        int line_number
        VisibilityModifier visibility
        list parameters
        string return_type
    }
    
    AnalysisFinding {
        string finding_id
        AnalysisFindingType finding_type
        AnalysisSeverity severity
        string description
        dict metadata
        list recommendations
    }
    
    TaskDefinition {
        string task_id
        string task_type
        string repository_url
        string user_id
        dict llm_config
        dict metadata
    }
    
    ProjectDataContext ||--o| PRDiffInfo : contains
    ProjectDataContext ||--o{ CodeEntity : parsed_from
    CodeEntity ||--o{ AnalysisFinding : generates
    TaskDefinition ||--|| ProjectDataContext : processes
```

### Data Transformation Pipeline

```mermaid
graph LR
    subgraph "Raw Data"
        A[Repository URL]
        B[Source Code Files]
        C[PR Diff Data]
    end
    
    subgraph "Structured Data"
        D[ProjectDataContext]
        E[CodeEntity Objects]
        F[PRDiffInfo]
    end
    
    subgraph "Analysis Data"
        G[AnalysisFinding Objects]
        H[LLMServiceRequest]
        I[Graph Relationships]
    end
    
    subgraph "Results Data"
        J[AnalysisResult]
        K[TaskResult]
        L[Final Report]
    end
    
    A --> D
    B --> E
    C --> F
    F --> D
    
    D --> G
    E --> G
    G --> H
    E --> I
    
    G --> J
    H --> J
    J --> K
    K --> L
```

## Performance Considerations

### Data Volume Handling

1. **Large Repository Processing**
   - Incremental parsing for large codebases
   - Parallel processing for multi-language projects
   - Memory-efficient streaming for file processing

2. **CKG Scalability**
   - Batch operations for Neo4j insertions
   - Index optimization for common queries
   - Connection pooling for concurrent access

3. **LLM Request Optimization**
   - Request batching and rate limiting
   - Context size optimization
   - Response caching for similar queries

### Data Persistence Strategy

1. **Temporary Data**
   - ProjectDataContext: In-memory during task execution
   - Cloned repositories: Temporary storage with cleanup

2. **Persistent Data**
   - Neo4j CKG: Long-term storage for reusability
   - Analysis cache: Configurable retention period

3. **Streaming Data**
   - Real-time log streams for monitoring
   - Progressive result delivery for large analyses

## Error Handling and Data Integrity

### Data Validation

```mermaid
graph TD
    INPUT[Input Data] --> VALIDATE[Validation Layer]
    VALIDATE --> |Valid| PROCESS[Processing Layer]
    VALIDATE --> |Invalid| ERROR[Error Handler]
    
    PROCESS --> |Success| OUTPUT[Output Data]
    PROCESS --> |Failure| ERROR
    
    ERROR --> LOG[Error Logging]
    ERROR --> RECOVER[Recovery Strategy]
    
    RECOVER --> |Retry| PROCESS
    RECOVER --> |Fallback| FALLBACK[Fallback Response]
```

### Data Flow Monitoring

1. **Performance Metrics**
   - Processing time per component
   - Memory usage tracking
   - API call latency monitoring

2. **Data Quality Metrics**
   - Parse success rates
   - Analysis finding accuracy
   - LLM response quality scores

3. **System Health Indicators**
   - Component availability status
   - Resource utilization levels
   - Error rate thresholds

## Future Enhancements

### Phase 4+ Considerations

1. **Real-time Data Streaming**
   - Live repository monitoring
   - Incremental analysis updates
   - WebSocket-based result delivery

2. **Advanced Caching Strategies**
   - Multi-level caching hierarchy
   - Intelligent cache invalidation
   - Cross-repository analysis caching

3. **Data Pipeline Optimization**
   - Machine learning-based optimization
   - Adaptive processing strategies
   - Predictive resource allocation

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-28  
**Phase Coverage:** 1-3 Complete  
**Status:** Production Ready 