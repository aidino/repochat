# RepoChat Sequence Diagrams - Phase 1-3

## Overview

This document provides detailed sequence diagrams for all major workflows in RepoChat system from Phase 1 through Phase 3. Each diagram shows the temporal flow of interactions between components.

## Table of Contents

1. [Repository Analysis Workflow](#repository-analysis-workflow)
2. [PR Review Workflow](#pr-review-workflow)
3. [LLM Enhancement Workflow](#llm-enhancement-workflow)
4. [Code Parsing and CKG Construction](#code-parsing-and-ckg-construction)
5. [Orchestrator Task Execution](#orchestrator-task-execution)
6. [Error Handling Flows](#error-handling-flows)

---

## Repository Analysis Workflow

### Complete Repository Analysis Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant ORCH as OrchestratorAgent
    participant GIT as GitOperationsModule
    participant LANG as LanguageIdentifierModule
    participant DATA as DataPreparationModule
    participant COORD as CodeParserCoordinatorModule
    participant JAVA as JavaParser
    participant PY as PythonParser
    participant AST2CKG as ASTtoCKGBuilderModule
    participant NEO4J as Neo4jConnectionModule
    participant ARCH as ArchitecturalAnalyzerModule
    participant CKG_Q as CKGQueryInterfaceModule
    
    U->>ORCH: analyze_repository(repo_url)
    
    Note over ORCH: Phase 1: Data Acquisition
    ORCH->>GIT: clone_repository(repo_url)
    GIT->>GIT: validate_repository()
    GIT->>GIT: perform_clone()
    GIT-->>ORCH: ProjectDataContext(cloned_path)
    
    ORCH->>LANG: analyze_project_languages(cloned_path)
    LANG->>LANG: scan_file_extensions()
    LANG->>LANG: content_analysis()
    LANG->>LANG: confidence_scoring()
    LANG-->>ORCH: detected_languages[]
    
    ORCH->>DATA: prepare_project_data(context)
    DATA->>DATA: validate_structure()
    DATA->>DATA: organize_files()
    DATA-->>ORCH: prepared_context
    
    Note over ORCH: Phase 1: CKG Operations
    ORCH->>COORD: parse_project(context)
    
    loop For each language
        alt Java files found
            COORD->>JAVA: parse_files(java_files)
            JAVA->>JAVA: ast_parsing()
            JAVA->>JAVA: entity_extraction()
            JAVA-->>COORD: CodeEntity[]
        else Python files found
            COORD->>PY: parse_files(python_files)
            PY->>PY: ast_parsing()
            PY->>PY: entity_extraction()
            PY-->>COORD: CodeEntity[]
        end
    end
    
    COORD-->>ORCH: all_entities[]
    
    ORCH->>AST2CKG: build_ckg(entities)
    AST2CKG->>NEO4J: create_nodes(entities)
    NEO4J-->>AST2CKG: node_ids[]
    AST2CKG->>NEO4J: create_relationships(entities)
    NEO4J-->>AST2CKG: relationship_ids[]
    AST2CKG-->>ORCH: ckg_built_successfully
    
    Note over ORCH: Phase 2: Code Analysis
    ORCH->>ARCH: analyze_project_architecture(context)
    ARCH->>CKG_Q: find_circular_dependencies()
    CKG_Q->>NEO4J: execute_cypher_query()
    NEO4J-->>CKG_Q: dependency_cycles[]
    CKG_Q-->>ARCH: circular_deps[]
    
    ARCH->>ARCH: analyze_patterns()
    ARCH->>ARCH: generate_findings()
    ARCH-->>ORCH: AnalysisResult(findings)
    
    ORCH-->>U: final_analysis_result
```

---

## PR Review Workflow

### PR Impact Analysis Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant ORCH as OrchestratorAgent
    participant GIT as GitOperationsModule
    participant PR_IMPACT as PRImpactAnalyzerModule
    participant CKG_Q as CKGQueryInterfaceModule
    participant NEO4J as Neo4jConnectionModule
    participant LLM_SUP as LLMAnalysisSupportModule
    participant GATEWAY as LLMGatewayModule
    
    U->>ORCH: review_pr(repo_url, pr_id)
    
    Note over ORCH: Phase 1: PR Data Acquisition
    ORCH->>GIT: extract_pr_diff(repo_url, pr_id)
    GIT->>GIT: fetch_pr_metadata()
    GIT->>GIT: extract_diff_content()
    GIT->>GIT: parse_changed_files()
    GIT->>GIT: extract_function_changes()
    GIT-->>ORCH: PRDiffInfo(changes)
    
    Note over ORCH: Update Project Context
    ORCH->>ORCH: update_context_with_pr(pr_diff)
    
    Note over ORCH: Phase 2: PR Impact Analysis
    ORCH->>PR_IMPACT: analyze_pr_impact(context_with_pr)
    
    PR_IMPACT->>PR_IMPACT: validate_pr_data()
    
    loop For each changed function
        PR_IMPACT->>CKG_Q: find_function_callers(function_name)
        CKG_Q->>NEO4J: query_incoming_calls()
        NEO4J-->>CKG_Q: caller_functions[]
        CKG_Q-->>PR_IMPACT: callers[]
        
        PR_IMPACT->>CKG_Q: find_function_callees(function_name)
        CKG_Q->>NEO4J: query_outgoing_calls()
        NEO4J-->>CKG_Q: callee_functions[]
        CKG_Q-->>PR_IMPACT: callees[]
        
        PR_IMPACT->>PR_IMPACT: assess_impact_scope(callers, callees)
    end
    
    PR_IMPACT->>PR_IMPACT: generate_impact_findings()
    PR_IMPACT-->>ORCH: AnalysisResult(impact_findings)
    
    Note over ORCH: Phase 2: LLM Enhancement
    ORCH->>LLM_SUP: enhance_analysis(findings, pr_context)
    LLM_SUP->>LLM_SUP: prepare_llm_context()
    LLM_SUP->>GATEWAY: process_llm_request(context)
    GATEWAY->>GATEWAY: route_to_provider()
    GATEWAY->>GATEWAY: call_openai_api()
    GATEWAY-->>LLM_SUP: enhanced_analysis
    LLM_SUP-->>ORCH: enriched_findings
    
    ORCH-->>U: pr_review_result
```

---

## LLM Enhancement Workflow

### LLM Request Processing Sequence

```mermaid
sequenceDiagram
    participant CA as CodeAnalysisModule
    participant LLM_SUP as LLMAnalysisSupportModule
    participant ORCH as OrchestratorAgent
    participant GATEWAY as LLMGatewayModule
    participant TEAM_LLM as TeamLLMServices
    participant PROVIDER as LLMProviderAbstractionLayer
    participant OPENAI as OpenAIProvider
    participant API as OpenAI_API
    
    CA->>LLM_SUP: request_llm_analysis(findings, code_context)
    
    LLM_SUP->>LLM_SUP: prepare_prompt_context()
    LLM_SUP->>LLM_SUP: select_prompt_template()
    LLM_SUP->>LLM_SUP: create_llm_request()
    
    LLM_SUP->>ORCH: route_llm_request(llm_request)
    ORCH->>ORCH: validate_request()
    ORCH->>ORCH: apply_user_config()
    
    ORCH->>GATEWAY: process_request(llm_request)
    GATEWAY->>GATEWAY: validate_request_format()
    GATEWAY->>GATEWAY: check_rate_limits()
    
    GATEWAY->>TEAM_LLM: process_request(request)
    TEAM_LLM->>TEAM_LLM: route_by_prompt_type()
    
    TEAM_LLM->>PROVIDER: send_request(request)
    PROVIDER->>PROVIDER: select_provider_by_config()
    
    PROVIDER->>OPENAI: call_api(request)
    OPENAI->>OPENAI: prepare_api_call()
    OPENAI->>API: HTTP POST /chat/completions
    
    API-->>OPENAI: response_json
    OPENAI->>OPENAI: parse_response()
    OPENAI->>OPENAI: validate_response()
    OPENAI-->>PROVIDER: LLMResponse
    
    PROVIDER->>PROVIDER: standardize_response()
    PROVIDER-->>TEAM_LLM: standardized_response
    
    TEAM_LLM->>TEAM_LLM: post_process_response()
    TEAM_LLM-->>GATEWAY: processed_response
    
    GATEWAY->>GATEWAY: log_response_metrics()
    GATEWAY-->>ORCH: LLMServiceResponse
    
    ORCH->>ORCH: validate_response_quality()
    ORCH-->>LLM_SUP: enhanced_response
    
    LLM_SUP->>LLM_SUP: integrate_llm_insights()
    LLM_SUP->>LLM_SUP: update_analysis_findings()
    LLM_SUP-->>CA: enhanced_analysis_result
```

---

## Code Parsing and CKG Construction

### Multi-Language Parsing Sequence

```mermaid
sequenceDiagram
    participant ORCH as OrchestratorAgent
    participant COORD as CodeParserCoordinatorModule
    participant JAVA as JavaParser
    participant PY as PythonParser
    participant KT as KotlinParser
    participant DART as DartParser
    participant AST2CKG as ASTtoCKGBuilderModule
    participant NEO4J as Neo4jConnectionModule
    
    ORCH->>COORD: parse_project(project_context)
    
    COORD->>COORD: analyze_project_structure()
    COORD->>COORD: categorize_files_by_language()
    
    Note over COORD: Parallel Parsing by Language
    
    par Java Parsing
        COORD->>JAVA: parse_java_files(java_file_list)
        loop For each Java file
            JAVA->>JAVA: parse_ast(file_path)
            JAVA->>JAVA: extract_classes()
            JAVA->>JAVA: extract_methods()
            JAVA->>JAVA: extract_relationships()
        end
        JAVA-->>COORD: java_entities[]
    and Python Parsing
        COORD->>PY: parse_python_files(python_file_list)
        loop For each Python file
            PY->>PY: parse_ast(file_path)
            PY->>PY: extract_classes()
            PY->>PY: extract_functions()
            PY->>PY: extract_relationships()
        end
        PY-->>COORD: python_entities[]
    and Kotlin Parsing
        COORD->>KT: parse_kotlin_files(kotlin_file_list)
        loop For each Kotlin file
            KT->>KT: regex_parse(file_content)
            KT->>KT: extract_classes()
            KT->>KT: extract_functions()
        end
        KT-->>COORD: kotlin_entities[]
    and Dart Parsing
        COORD->>DART: parse_dart_files(dart_file_list)
        loop For each Dart file
            DART->>DART: regex_parse(file_content)
            DART->>DART: extract_classes()
            DART->>DART: extract_functions()
        end
        DART-->>COORD: dart_entities[]
    end
    
    COORD->>COORD: merge_all_entities()
    COORD->>COORD: resolve_cross_language_references()
    COORD-->>ORCH: consolidated_entities[]
    
    Note over ORCH: CKG Construction Phase
    ORCH->>AST2CKG: build_knowledge_graph(entities)
    
    AST2CKG->>AST2CKG: validate_entities()
    
    loop For each entity batch
        AST2CKG->>NEO4J: create_nodes(entity_batch)
        NEO4J->>NEO4J: validate_node_schema()
        NEO4J->>NEO4J: insert_nodes()
        NEO4J-->>AST2CKG: created_node_ids[]
    end
    
    loop For each relationship batch
        AST2CKG->>NEO4J: create_relationships(relationship_batch)
        NEO4J->>NEO4J: validate_relationship_schema()
        NEO4J->>NEO4J: insert_relationships()
        NEO4J-->>AST2CKG: created_relationship_ids[]
    end
    
    AST2CKG->>NEO4J: create_indexes()
    NEO4J-->>AST2CKG: index_creation_status
    
    AST2CKG-->>ORCH: ckg_construction_complete
```

---

## Orchestrator Task Execution

### Complete Task Orchestration Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant ORCH as OrchestratorAgent
    participant TDA as TEAM_DataAcquisition
    participant TCKG as TEAM_CKGOperations
    participant TCA as TEAM_CodeAnalysis
    participant TLLS as TEAM_LLMServices
    
    U->>ORCH: execute_task(task_definition)
    
    Note over ORCH: Task Initialization
    ORCH->>ORCH: validate_task_definition()
    ORCH->>ORCH: initialize_task_context()
    ORCH->>ORCH: setup_execution_plan()
    
    Note over ORCH: Phase 1 Execution
    ORCH->>TDA: initialize_data_acquisition()
    TDA->>TDA: setup_git_operations()
    TDA->>TDA: setup_language_detection()
    TDA-->>ORCH: data_acquisition_ready
    
    ORCH->>TDA: acquire_project_data(repo_url)
    TDA->>TDA: clone_repository()
    TDA->>TDA: detect_languages()
    TDA->>TDA: prepare_data()
    TDA-->>ORCH: project_data_context
    
    ORCH->>TCKG: initialize_ckg_operations()
    TCKG->>TCKG: setup_neo4j_connection()
    TCKG->>TCKG: setup_parsers()
    TCKG-->>ORCH: ckg_operations_ready
    
    ORCH->>TCKG: build_code_knowledge_graph(context)
    TCKG->>TCKG: coordinate_parsing()
    TCKG->>TCKG: build_graph_nodes()
    TCKG->>TCKG: build_graph_relationships()
    TCKG-->>ORCH: ckg_construction_result
    
    Note over ORCH: Phase 2 Execution
    ORCH->>TCA: initialize_code_analysis()
    TCA->>TCA: setup_architectural_analyzer()
    TCA->>TCA: setup_pr_impact_analyzer()
    TCA->>TCA: setup_llm_support()
    TCA-->>ORCH: code_analysis_ready
    
    ORCH->>TCA: perform_code_analysis(context, ckg_result)
    TCA->>TCA: run_architectural_analysis()
    TCA->>TCA: run_pr_impact_analysis()
    TCA->>TCA: aggregate_findings()
    TCA-->>ORCH: analysis_findings[]
    
    Note over ORCH: LLM Enhancement Phase
    ORCH->>TLLS: initialize_llm_services()
    TLLS->>TLLS: setup_gateway()
    TLLS->>TLLS: setup_providers()
    TLLS-->>ORCH: llm_services_ready
    
    loop For each finding requiring LLM enhancement
        ORCH->>TCA: request_llm_enhancement(finding)
        TCA->>TLLS: process_llm_request(request)
        TLLS->>TLLS: route_to_appropriate_provider()
        TLLS->>TLLS: call_llm_api()
        TLLS-->>TCA: llm_response
        TCA->>TCA: integrate_llm_insights()
        TCA-->>ORCH: enhanced_finding
    end
    
    Note over ORCH: Task Completion
    ORCH->>ORCH: aggregate_all_results()
    ORCH->>ORCH: generate_task_result()
    ORCH->>ORCH: cleanup_resources()
    
    ORCH-->>U: task_execution_result
```

---

## Error Handling Flows

### Error Recovery Sequence

```mermaid
sequenceDiagram
    participant ORCH as OrchestratorAgent
    participant COMP as Component
    participant ERROR as ErrorHandler
    participant LOG as LoggingSystem
    participant RETRY as RetryManager
    
    ORCH->>COMP: execute_operation()
    
    COMP->>COMP: attempt_operation()
    COMP->>COMP: operation_fails()
    COMP->>ERROR: handle_error(exception)
    
    ERROR->>ERROR: classify_error_type()
    ERROR->>LOG: log_error_details()
    
    alt Recoverable Error
        ERROR->>RETRY: attempt_retry(operation)
        RETRY->>RETRY: check_retry_count()
        RETRY->>RETRY: apply_backoff_delay()
        RETRY->>COMP: retry_operation()
        
        alt Retry Successful
            COMP-->>ORCH: operation_result
        else Retry Failed
            RETRY->>ERROR: max_retries_exceeded()
            ERROR->>ERROR: apply_fallback_strategy()
            ERROR-->>ORCH: fallback_result
        end
        
    else Non-Recoverable Error
        ERROR->>ERROR: generate_error_report()
        ERROR->>LOG: log_critical_error()
        ERROR-->>ORCH: error_result
        
        ORCH->>ORCH: graceful_degradation()
        ORCH->>ORCH: cleanup_partial_results()
    end
    
    ORCH-->>ORCH: update_task_status()
```

### Circuit Breaker Pattern for LLM Services

```mermaid
sequenceDiagram
    participant CA as CodeAnalysis
    participant CB as CircuitBreaker
    participant LLM as LLMService
    participant FB as Fallback
    
    CA->>CB: request_llm_analysis()
    
    CB->>CB: check_circuit_state()
    
    alt Circuit Closed (Normal Operation)
        CB->>LLM: forward_request()
        
        alt Request Successful
            LLM-->>CB: success_response
            CB->>CB: record_success()
            CB-->>CA: response
        else Request Failed
            LLM-->>CB: error_response
            CB->>CB: record_failure()
            CB->>CB: check_failure_threshold()
            
            alt Threshold Exceeded
                CB->>CB: open_circuit()
                CB->>FB: activate_fallback()
                FB-->>CB: fallback_response
                CB-->>CA: fallback_response
            else Under Threshold
                CB-->>CA: error_response
            end
        end
        
    else Circuit Open (Failing Fast)
        CB->>FB: use_fallback()
        FB-->>CB: fallback_response
        CB-->>CA: fallback_response
        
    else Circuit Half-Open (Testing)
        CB->>LLM: test_request()
        
        alt Test Successful
            LLM-->>CB: success_response
            CB->>CB: close_circuit()
            CB-->>CA: response
        else Test Failed
            LLM-->>CB: error_response
            CB->>CB: keep_circuit_open()
            CB->>FB: use_fallback()
            FB-->>CB: fallback_response
            CB-->>CA: fallback_response
        end
    end
```

---

## Performance Monitoring Sequence

### Real-time Performance Tracking

```mermaid
sequenceDiagram
    participant ORCH as OrchestratorAgent
    participant COMP as Component
    participant MONITOR as PerformanceMonitor
    participant METRICS as MetricsCollector
    participant ALERT as AlertManager
    
    ORCH->>COMP: start_operation()
    COMP->>MONITOR: start_timing(operation_id)
    
    COMP->>COMP: execute_operation()
    
    loop During Execution
        COMP->>MONITOR: record_metric(key, value)
        MONITOR->>METRICS: store_metric(timestamp, key, value)
        
        MONITOR->>MONITOR: check_thresholds()
        
        alt Threshold Exceeded
            MONITOR->>ALERT: trigger_alert(metric, value)
            ALERT->>ALERT: evaluate_alert_severity()
            ALERT->>ALERT: notify_stakeholders()
        end
    end
    
    COMP->>MONITOR: end_timing(operation_id)
    MONITOR->>METRICS: store_duration(operation_id, duration)
    
    COMP-->>ORCH: operation_complete
    
    MONITOR->>METRICS: aggregate_metrics()
    METRICS->>METRICS: calculate_statistics()
    METRICS->>METRICS: update_dashboards()
```

---

## Summary

These sequence diagrams provide a comprehensive view of:

1. **Data Flow Orchestration**: How data moves through the system components
2. **Error Handling**: Robust error recovery and fallback mechanisms
3. **Performance Monitoring**: Real-time system health tracking
4. **LLM Integration**: Complex request routing and response handling
5. **Multi-language Processing**: Parallel parsing coordination
6. **PR Analysis**: Detailed impact assessment workflows

Each diagram represents production-ready patterns that ensure:
- **Reliability**: Comprehensive error handling and recovery
- **Scalability**: Parallel processing and efficient resource utilization
- **Maintainability**: Clear component boundaries and responsibilities
- **Observability**: Extensive logging and monitoring throughout

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-28  
**Phase Coverage:** 1-3 Complete  
**Status:** Production Ready 