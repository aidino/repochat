# Manual Test Scenarios for Task 2.9: Orchestrator CKG Integration

## Scenario 1: Successful Full Workflow (Data Acquisition → CKG Operations)

### Prerequisites:
- Neo4j database is running and accessible
- Valid Git repository URL available

### Steps:
1. Initialize OrchestratorAgent
2. Create TaskDefinition with valid repository URL
3. Call `handle_scan_project_with_ckg_task()`
4. Verify complete workflow execution

### Expected Results:
- ✅ Data Acquisition completes successfully (ProjectDataContext created)
- ✅ CKG Operations facade is called with ProjectDataContext
- ✅ Code parsing completes for detected languages
- ✅ CKG building creates nodes and relationships in Neo4j
- ✅ CKGOperationResult indicates success with statistics
- ✅ Performance metrics logged for all phases
- ✅ No errors in logs

### Verification Commands:
```python
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

# Test with a real repository
orchestrator = OrchestratorAgent()
task = TaskDefinition(repository_url="https://github.com/your-test-repo.git")
project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(task)

# Verify results
assert project_context is not None
assert ckg_result.success == True
assert ckg_result.nodes_created > 0
assert ckg_result.relationships_created > 0

orchestrator.shutdown()
```

## Scenario 2: CKG Operations Failure Handling

### Prerequisites:
- Neo4j database is NOT running or misconfigured
- Valid Git repository URL available

### Steps:
1. Initialize OrchestratorAgent
2. Create TaskDefinition with valid repository URL
3. Call `handle_scan_project_with_ckg_task()`
4. Verify graceful error handling

### Expected Results:
- ✅ Data Acquisition completes successfully
- ✅ CKG Operations facade is called but fails due to Neo4j issues
- ✅ CKGOperationResult indicates failure with error details
- ✅ ProjectDataContext is still returned (data acquisition succeeded)
- ✅ Error messages logged appropriately
- ✅ No exceptions thrown to caller

### Verification Commands:
```python
# Stop Neo4j service first
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

orchestrator = OrchestratorAgent()
task = TaskDefinition(repository_url="https://github.com/your-test-repo.git")

try:
    project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(task)
    
    # Data acquisition should succeed
    assert project_context is not None
    assert len(project_context.detected_languages) > 0
    
    # CKG operations should fail gracefully
    assert ckg_result.success == False
    assert len(ckg_result.errors) > 0
    assert "Neo4j" in str(ckg_result.errors)
    
    print("✅ Graceful error handling verified")
except Exception as e:
    print(f"❌ Unexpected exception: {e}")
finally:
    orchestrator.shutdown()
```

## Scenario 3: Data Acquisition Failure

### Prerequisites:
- Invalid/inaccessible Git repository URL

### Steps:
1. Initialize OrchestratorAgent
2. Create TaskDefinition with invalid repository URL
3. Call `handle_scan_project_with_ckg_task()`
4. Verify error propagation

### Expected Results:
- ❌ Data Acquisition fails (invalid repository)
- ❌ CKG Operations is never called
- ❌ Exception is propagated to caller
- ✅ Error messages logged appropriately

### Verification Commands:
```python
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

orchestrator = OrchestratorAgent()
task = TaskDefinition(repository_url="https://invalid-repo-url.git")

try:
    project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(task)
    print("❌ Should have thrown exception")
except Exception as e:
    print(f"✅ Expected exception caught: {e}")
    assert "clone" in str(e).lower() or "repository" in str(e).lower()
finally:
    orchestrator.shutdown()
```

## Scenario 4: Empty Repository Handling

### Prerequisites:
- Empty Git repository (no source files)

### Steps:
1. Initialize OrchestratorAgent
2. Create TaskDefinition with empty repository URL
3. Call `handle_scan_project_with_ckg_task()`
4. Verify handling of empty projects

### Expected Results:
- ✅ Data Acquisition completes (empty ProjectDataContext)
- ✅ CKG Operations is called but finds no files to parse
- ✅ CKGOperationResult indicates success but with zero statistics
- ✅ No errors logged (empty project is valid)

### Verification Commands:
```python
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

orchestrator = OrchestratorAgent()
task = TaskDefinition(repository_url="https://github.com/empty-repo.git")
project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(task)

# Should succeed but with empty results
assert project_context is not None
assert len(project_context.detected_languages) == 0
assert ckg_result.success == True  # Success but empty
assert ckg_result.files_parsed == 0
assert ckg_result.nodes_created == 0

orchestrator.shutdown()
```

## Scenario 5: Statistics and Performance Monitoring

### Prerequisites:
- Valid Git repository with multiple languages

### Steps:
1. Initialize OrchestratorAgent
2. Process multiple repositories
3. Check performance metrics and statistics

### Expected Results:
- ✅ All operations complete within reasonable time
- ✅ Statistics are accurate and consistent
- ✅ Performance metrics are logged
- ✅ Facade operation count increments correctly

### Verification Commands:
```python
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

orchestrator = OrchestratorAgent()

# Process multiple repositories
repos = [
    "https://github.com/repo1.git",
    "https://github.com/repo2.git"
]

for repo_url in repos:
    task = TaskDefinition(repository_url=repo_url)
    project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(task)
    
    # Check timing
    assert ckg_result.operation_duration_ms > 0
    print(f"Processed {repo_url} in {ckg_result.operation_duration_ms:.2f}ms")

# Check facade statistics
facade_stats = orchestrator.ckg_operations.get_operation_statistics()
assert facade_stats['total_operations'] == len(repos)
assert facade_stats['total_processing_time_seconds'] > 0

orchestrator.shutdown()
```

## Scenario 6: Orchestrator Shutdown Cleanup

### Prerequisites:
- OrchestratorAgent initialized with CKG Operations

### Steps:
1. Initialize OrchestratorAgent
2. Perform some operations
3. Call shutdown()
4. Verify proper cleanup

### Expected Results:
- ✅ CKG Operations facade shutdown is called
- ✅ Neo4j connections are closed
- ✅ No resource leaks
- ✅ All cleanup logged appropriately

### Verification Commands:
```python
from orchestrator.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()

# Perform some operations
assert orchestrator.ckg_operations is not None
assert hasattr(orchestrator.ckg_operations, 'shutdown')

# Test shutdown
orchestrator.shutdown()

# Verify cleanup (check logs for shutdown messages)
print("✅ Shutdown completed - check logs for cleanup confirmation")
```

## Log Analysis

### During testing, monitor logs for:

1. **Initialization Phase:**
   - `TEAM CKG Operations initialized successfully`
   - Performance metrics for initialization

2. **Workflow Execution:**
   - `Starting full scan + CKG workflow`
   - `Phase 1: Data Acquisition`
   - `Phase 2: CKG Operations`
   - `Complete scan + CKG workflow finished`

3. **Error Handling:**
   - Appropriate error messages for failures
   - No stack traces for expected failures

4. **Performance Metrics:**
   - `full_scan_ckg_workflow_duration`
   - `ckg_operations_total_duration`
   - Individual component timing

5. **Shutdown Process:**
   - `Shutting down TEAM CKG Operations`
   - `TEAM CKG Operations shutdown completed`

## Success Criteria

All manual test scenarios should pass with:
- ✅ No unexpected exceptions
- ✅ Appropriate error handling
- ✅ Correct status reporting
- ✅ Performance within acceptable ranges
- ✅ Proper resource cleanup
- ✅ Comprehensive logging coverage 