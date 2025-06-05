# Comprehensive Manual Test Scenarios - Phase 1 & 2
## Testing với Java Project Thực Tế

### 🐳 **DOCKER ENVIRONMENT SETUP**

#### 1. Tạo Docker Compose Environment

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.11-community
    container_name: repochat-neo4j-test
    ports:
      - "7474:7474"   # Browser interface
      - "7687:7687"   # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/repochat123
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - ./neo4j/plugins:/plugins
    healthcheck:
      test: cypher-shell "RETURN 1"
      interval: 10s
      timeout: 5s
      retries: 5

  repochat-backend:
    build: 
      context: .
      dockerfile: Dockerfile.test
    container_name: repochat-backend-test
    depends_on:
      neo4j:
        condition: service_healthy
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=repochat123
      - PYTHONPATH=/app/src
    volumes:
      - .:/app
      - /tmp/repochat-test:/tmp/repochat-test
    working_dir: /app
    command: tail -f /dev/null

volumes:
  neo4j_data:
  neo4j_logs:
```

#### 2. Setup Commands

```bash
# Tạo test environment
cd backend
docker-compose -f docker-compose.test.yml up -d

# Verify services
docker-compose -f docker-compose.test.yml ps
docker-compose -f docker-compose.test.yml logs neo4j

# Access backend container
docker exec -it repochat-backend-test bash
```

### 📋 **TEST PROJECT: Spring PetClinic**

**Repository**: `https://github.com/spring-projects/spring-petclinic.git`
**Why**: Real-world Spring Boot application với complex structure
**Languages**: Java, SQL, HTML, CSS, JavaScript
**Size**: ~50 files, multiple packages, good for testing

### 🔧 **PHASE 1 TESTING: TEAM Data Acquisition**

#### **Test 1.1: OrchestratorAgent Initialization**

```python
# File: test_phase1_orchestrator.py
from orchestrator.orchestrator_agent import OrchestratorAgent
import time

def test_orchestrator_initialization():
    print("=== Testing OrchestratorAgent Initialization ===")
    
    start_time = time.time()
    orchestrator = OrchestratorAgent()
    init_time = time.time() - start_time
    
    # Verify initialization
    assert orchestrator._is_initialized == True
    assert orchestrator.agent_id is not None
    assert hasattr(orchestrator, 'git_operations')
    assert hasattr(orchestrator, 'language_identifier') 
    assert hasattr(orchestrator, 'data_preparation')
    assert hasattr(orchestrator, 'pat_handler')
    
    print(f"✅ Agent initialized in {init_time:.3f}s")
    print(f"✅ Agent ID: {orchestrator.agent_id}")
    
    # Check stats
    stats = orchestrator.get_agent_stats()
    print(f"✅ Agent stats: {stats}")
    
    orchestrator.shutdown()
    print("✅ Agent shutdown completed")
```

#### **Test 1.2: GitOperationsModule**

```python
# File: test_phase1_git_operations.py
from teams.data_acquisition import GitOperationsModule
from shared.models.task_definition import TaskDefinition
import os
import shutil

def test_git_operations_real_project():
    print("=== Testing GitOperationsModule với Spring PetClinic ===")
    
    git_ops = GitOperationsModule()
    repo_url = "https://github.com/spring-projects/spring-petclinic.git"
    
    try:
        # Test clone
        print(f"🔄 Cloning {repo_url}")
        cloned_path = git_ops.clone_repository(repo_url)
        
        # Verify clone success
        assert os.path.exists(cloned_path)
        assert os.path.isdir(cloned_path)
        
        # Check for expected Java files
        java_files = []
        for root, dirs, files in os.walk(cloned_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        print(f"✅ Repository cloned to: {cloned_path}")
        print(f"✅ Found {len(java_files)} Java files")
        print(f"✅ Sample Java files:")
        for i, java_file in enumerate(java_files[:5]):
            relative_path = os.path.relpath(java_file, cloned_path)
            print(f"   - {relative_path}")
        
        # Verify main directories exist
        src_main = os.path.join(cloned_path, "src", "main", "java")
        assert os.path.exists(src_main), f"Main source directory not found: {src_main}"
        print(f"✅ Main source directory exists: {src_main}")
        
        return cloned_path
        
    except Exception as e:
        print(f"❌ Git operations failed: {e}")
        raise
```

#### **Test 1.3: LanguageIdentifierModule**

```python
# File: test_phase1_language_identifier.py
from teams.data_acquisition import LanguageIdentifierModule

def test_language_identifier_spring_petclinic(cloned_path):
    print("=== Testing LanguageIdentifierModule ===")
    
    lang_identifier = LanguageIdentifierModule()
    
    # Test language detection
    detected_languages = lang_identifier.identify_languages(cloned_path)
    
    print(f"✅ Detected languages: {detected_languages}")
    
    # Verify expected languages
    expected_languages = ["java"]  # Primary language
    for lang in expected_languages:
        assert lang in detected_languages, f"Expected language {lang} not detected"
    
    # Test detailed analysis
    file_analysis = lang_identifier.analyze_project_structure(cloned_path)
    
    print(f"✅ Total files analyzed: {file_analysis['total_files']}")
    print(f"✅ Language breakdown:")
    for lang, count in file_analysis['language_breakdown'].items():
        print(f"   - {lang}: {count} files")
    
    # Verify Java is dominant language
    java_count = file_analysis['language_breakdown'].get('java', 0)
    assert java_count > 0, "No Java files detected"
    print(f"✅ Java files: {java_count}")
    
    return detected_languages
```

#### **Test 1.4: DataPreparationModule**

```python
# File: test_phase1_data_preparation.py
from teams.data_acquisition import DataPreparationModule
from shared.models.project_data_context import ProjectDataContext

def test_data_preparation_spring_petclinic(cloned_path, detected_languages):
    print("=== Testing DataPreparationModule ===")
    
    data_prep = DataPreparationModule()
    repo_url = "https://github.com/spring-projects/spring-petclinic.git"
    
    # Create ProjectDataContext
    project_context = data_prep.create_project_context(
        cloned_code_path=cloned_path,
        detected_languages=detected_languages,
        repository_url=repo_url
    )
    
    # Verify ProjectDataContext
    assert isinstance(project_context, ProjectDataContext)
    assert project_context.cloned_code_path == cloned_path
    assert project_context.detected_languages == detected_languages
    assert project_context.repository_url == repo_url
    
    print(f"✅ ProjectDataContext created successfully")
    print(f"✅ Repository URL: {project_context.repository_url}")
    print(f"✅ Cloned path: {project_context.cloned_code_path}")
    print(f"✅ Languages: {project_context.detected_languages}")
    print(f"✅ Language count: {project_context.language_count}")
    print(f"✅ Has languages: {project_context.has_languages}")
    print(f"✅ Primary language: {project_context.primary_language}")
    
    return project_context
```

#### **Test 1.5: Complete Phase 1 Workflow**

```python
# File: test_phase1_complete_workflow.py
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

def test_complete_phase1_workflow():
    print("=== Testing Complete Phase 1 Workflow ===")
    
    orchestrator = OrchestratorAgent()
    
    # Test with Spring PetClinic
    task_definition = TaskDefinition(
        repository_url="https://github.com/spring-projects/spring-petclinic.git"
    )
    
    try:
        # Execute complete workflow
        print("🔄 Executing scan project task...")
        project_context = orchestrator.handle_scan_project_task(task_definition)
        
        # Verify results
        assert project_context is not None
        assert project_context.cloned_code_path is not None
        assert len(project_context.detected_languages) > 0
        assert "java" in project_context.detected_languages
        
        print(f"✅ Workflow completed successfully")
        print(f"✅ Project: {project_context.repository_url}")
        print(f"✅ Languages: {project_context.detected_languages}")
        print(f"✅ Primary: {project_context.primary_language}")
        
        return project_context
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        raise
    finally:
        orchestrator.shutdown()
```

### 🏗️ **PHASE 2 TESTING: TEAM CKG Operations**

#### **Test 2.1: Neo4jConnectionModule**

```python
# File: test_phase2_neo4j.py
from teams.ckg_operations import Neo4jConnectionModule

def test_neo4j_connection():
    print("=== Testing Neo4jConnectionModule ===")
    
    # Test connection with Docker Neo4j
    neo4j_conn = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        user="neo4j", 
        password="repochat123"
    )
    
    # Test connection
    connected = neo4j_conn.connect()
    assert connected, "Failed to connect to Neo4j"
    print("✅ Connected to Neo4j successfully")
    
    # Test health check
    health = neo4j_conn.health_check()
    assert health, "Neo4j health check failed"
    print("✅ Neo4j health check passed")
    
    # Test basic query
    session = neo4j_conn.get_session()
    try:
        result = session.run("RETURN 'Hello Neo4j' as message")
        record = result.single()
        assert record["message"] == "Hello Neo4j"
        print("✅ Basic query execution successful")
    finally:
        session.close()
    
    # Cleanup
    neo4j_conn.close()
    print("✅ Neo4j connection closed")
```

#### **Test 2.2 & 2.3: Java Parser Integration**

```python
# File: test_phase2_java_parser.py
from teams.ckg_operations import CodeParserCoordinatorModule
from shared.models.project_data_context import ProjectDataContext

def test_java_parser_spring_petclinic(project_context):
    print("=== Testing Java Parser với Spring PetClinic ===")
    
    parser_coordinator = CodeParserCoordinatorModule()
    
    # Execute parsing
    print("🔄 Parsing Java files...")
    parse_result = parser_coordinator.coordinate_parsing(project_context)
    
    # Verify parsing results
    assert parse_result.total_files_parsed > 0
    assert parse_result.total_entities_found > 0
    assert "java" in parse_result.languages_processed
    
    print(f"✅ Parsing completed successfully")
    print(f"✅ Files parsed: {parse_result.total_files_parsed}")
    print(f"✅ Entities found: {parse_result.total_entities_found}")
    print(f"✅ Relationships found: {parse_result.total_relationships_found}")
    print(f"✅ Languages processed: {parse_result.languages_processed}")
    
    # Detailed entity analysis
    java_results = parse_result.parser_results.get("java", [])
    if java_results:
        total_classes = sum(1 for result in java_results 
                          for entity in result.entities 
                          if entity.entity_type.value == "CLASS")
        total_methods = sum(1 for result in java_results 
                           for entity in result.entities 
                           if entity.entity_type.value == "METHOD")
        
        print(f"✅ Java classes found: {total_classes}")
        print(f"✅ Java methods found: {total_methods}")
        
        # Sample entities
        print(f"✅ Sample entities:")
        for i, result in enumerate(java_results[:3]):
            print(f"   File: {result.file_path}")
            for j, entity in enumerate(result.entities[:2]):
                print(f"     - {entity.entity_type.value}: {entity.name}")
    
    return parse_result
```

#### **Test 2.6 & 2.7: CKG Building**

```python
# File: test_phase2_ckg_building.py
from teams.ckg_operations import ASTtoCKGBuilderModule, Neo4jConnectionModule

def test_ckg_building_spring_petclinic(parse_result):
    print("=== Testing CKG Building với Spring PetClinic ===")
    
    # Setup Neo4j connection
    neo4j_conn = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="repochat123"
    )
    
    connected = neo4j_conn.connect()
    assert connected, "Failed to connect to Neo4j"
    
    # Clear existing data
    session = neo4j_conn.get_session()
    try:
        session.run("MATCH (n) DETACH DELETE n")
        print("✅ Cleared existing Neo4j data")
    finally:
        session.close()
    
    # Build CKG
    ckg_builder = ASTtoCKGBuilderModule(neo4j_conn)
    project_name = "spring-petclinic-test"
    
    print("🔄 Building Code Knowledge Graph...")
    build_result = ckg_builder.build_ckg_from_coordinator_result(
        parse_result, 
        project_name
    )
    
    # Verify build results
    assert build_result.success, f"CKG build failed: {build_result.errors}"
    assert build_result.nodes_created > 0
    assert build_result.relationships_created > 0
    
    print(f"✅ CKG building completed successfully")
    print(f"✅ Nodes created: {build_result.nodes_created}")
    print(f"✅ Relationships created: {build_result.relationships_created}")
    print(f"✅ Files processed: {build_result.files_processed}")
    print(f"✅ Build duration: {build_result.build_duration_ms:.2f}ms")
    
    # Verify graph structure
    session = neo4j_conn.get_session()
    try:
        # Count nodes by type
        node_counts = {}
        result = session.run("""
            MATCH (n) 
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY count DESC
        """)
        
        for record in result:
            node_counts[record["label"]] = record["count"]
        
        print(f"✅ Node distribution:")
        for label, count in node_counts.items():
            print(f"   - {label}: {count}")
        
        # Count relationships by type
        rel_counts = {}
        result = session.run("""
            MATCH ()-[r]->() 
            RETURN type(r) as rel_type, count(r) as count
            ORDER BY count DESC
        """)
        
        for record in result:
            rel_counts[record["rel_type"]] = record["count"]
        
        print(f"✅ Relationship distribution:")
        for rel_type, count in rel_counts.items():
            print(f"   - {rel_type}: {count}")
            
        # Verify expected Spring entities
        spring_entities = session.run("""
            MATCH (c:Class) 
            WHERE c.name CONTAINS "Controller" OR c.name CONTAINS "Service" OR c.name CONTAINS "Repository"
            RETURN c.name as name, c.file_path as file_path
            LIMIT 10
        """)
        
        print(f"✅ Spring components found:")
        for record in spring_entities:
            print(f"   - {record['name']} in {record['file_path']}")
            
    finally:
        session.close()
    
    neo4j_conn.close()
    return build_result
```

#### **Test 2.8: CKG Query Interface**

```python
# File: test_phase2_ckg_queries.py
from teams.ckg_operations import CKGQueryInterfaceModule, Neo4jConnectionModule

def test_ckg_queries_spring_petclinic():
    print("=== Testing CKG Query Interface ===")
    
    # Setup connection
    neo4j_conn = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="repochat123"
    )
    connected = neo4j_conn.connect()
    assert connected, "Failed to connect to Neo4j"
    
    query_interface = CKGQueryInterfaceModule(neo4j_conn)
    
    # Test 1: Get all classes
    print("🔍 Testing: Get all classes")
    classes = query_interface.get_all_classes()
    assert len(classes) > 0, "No classes found"
    print(f"✅ Found {len(classes)} classes")
    
    # Show sample classes
    for i, cls in enumerate(classes[:5]):
        print(f"   {i+1}. {cls['name']} ({cls['file_path']})")
    
    # Test 2: Get methods for a specific class
    if classes:
        test_class = classes[0]['name']
        print(f"🔍 Testing: Get methods for class '{test_class}'")
        methods = query_interface.get_class_methods(test_class)
        print(f"✅ Found {len(methods)} methods for {test_class}")
        
        for i, method in enumerate(methods[:3]):
            print(f"   {i+1}. {method['name']} (line {method.get('line_number', 'N/A')})")
    
    # Test 3: Find class definition location
    if classes:
        test_class = classes[0]['name']
        print(f"🔍 Testing: Find definition location for '{test_class}'")
        location = query_interface.get_class_definition_location(test_class)
        assert location is not None, f"Location not found for {test_class}"
        print(f"✅ Class '{test_class}' defined at: {location}")
    
    # Test 4: Get call relationships
    print("🔍 Testing: Get call relationships")
    call_relationships = query_interface.get_call_relationships()
    print(f"✅ Found {len(call_relationships)} call relationships")
    
    # Show sample relationships
    for i, rel in enumerate(call_relationships[:5]):
        caller = rel['caller']
        callee = rel['callee']
        print(f"   {i+1}. {caller} → {callee}")
    
    # Test 5: Custom query for Spring-specific patterns
    print("🔍 Testing: Spring-specific queries")
    
    # Find controllers
    controllers = query_interface.execute_custom_query("""
        MATCH (c:Class) 
        WHERE c.name ENDS WITH "Controller"
        RETURN c.name as name, c.file_path as file_path
        ORDER BY c.name
    """)
    print(f"✅ Found {len(controllers)} Controllers:")
    for ctrl in controllers[:3]:
        print(f"   - {ctrl['name']}")
    
    # Find services
    services = query_interface.execute_custom_query("""
        MATCH (c:Class) 
        WHERE c.name ENDS WITH "Service"
        RETURN c.name as name, c.file_path as file_path
        ORDER BY c.name
    """)
    print(f"✅ Found {len(services)} Services:")
    for svc in services[:3]:
        print(f"   - {svc['name']}")
    
    neo4j_conn.close()
    print("✅ CKG Query Interface testing completed")
```

#### **Test 2.9: Complete Phase 2 Workflow**

```python
# File: test_phase2_complete_workflow.py
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

def test_complete_phase2_workflow():
    print("=== Testing Complete Phase 1+2 Workflow ===")
    
    orchestrator = OrchestratorAgent()
    
    task_definition = TaskDefinition(
        repository_url="https://github.com/spring-projects/spring-petclinic.git"
    )
    
    try:
        print("🔄 Executing complete workflow...")
        project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(
            task_definition
        )
        
        # Verify Phase 1 results
        assert project_context is not None
        assert len(project_context.detected_languages) > 0
        assert "java" in project_context.detected_languages
        print(f"✅ Phase 1 completed: {project_context.language_count} languages")
        
        # Verify Phase 2 results
        assert ckg_result.success, f"CKG failed: {ckg_result.errors}"
        assert ckg_result.files_parsed > 0
        assert ckg_result.nodes_created > 0
        assert ckg_result.relationships_created > 0
        
        print(f"✅ Phase 2 completed successfully")
        print(f"✅ Files parsed: {ckg_result.files_parsed}")
        print(f"✅ Entities found: {ckg_result.entities_found}")
        print(f"✅ Nodes created: {ckg_result.nodes_created}")
        print(f"✅ Relationships created: {ckg_result.relationships_created}")
        print(f"✅ Total duration: {ckg_result.operation_duration_ms:.2f}ms")
        
        return project_context, ckg_result
        
    except Exception as e:
        print(f"❌ Complete workflow failed: {e}")
        raise
    finally:
        orchestrator.shutdown()
```

### 🧪 **COMPLETE TEST SUITE EXECUTION**

```python
# File: run_comprehensive_tests.py
#!/usr/bin/env python3
"""
Comprehensive Manual Test Suite for Phase 1 & 2
Run with Docker environment active
"""

import sys
import traceback
from test_phase1_orchestrator import test_orchestrator_initialization
from test_phase1_git_operations import test_git_operations_real_project  
from test_phase1_language_identifier import test_language_identifier_spring_petclinic
from test_phase1_data_preparation import test_data_preparation_spring_petclinic
from test_phase1_complete_workflow import test_complete_phase1_workflow
from test_phase2_neo4j import test_neo4j_connection
from test_phase2_java_parser import test_java_parser_spring_petclinic
from test_phase2_ckg_building import test_ckg_building_spring_petclinic
from test_phase2_ckg_queries import test_ckg_queries_spring_petclinic
from test_phase2_complete_workflow import test_complete_phase2_workflow

def run_comprehensive_tests():
    """Execute all manual tests in sequence"""
    
    print("🚀 Starting Comprehensive Manual Test Suite")
    print("📋 Testing Phase 1 & 2 with Spring PetClinic")
    print("=" * 60)
    
    results = {}
    
    try:
        # Phase 1 Tests
        print("\n🔵 PHASE 1: DATA ACQUISITION TESTING")
        print("-" * 40)
        
        test_orchestrator_initialization()
        results["orchestrator_init"] = "✅ PASS"
        
        cloned_path = test_git_operations_real_project()
        results["git_operations"] = "✅ PASS"
        
        detected_languages = test_language_identifier_spring_petclinic(cloned_path)
        results["language_identifier"] = "✅ PASS"
        
        project_context = test_data_preparation_spring_petclinic(cloned_path, detected_languages)
        results["data_preparation"] = "✅ PASS"
        
        project_context = test_complete_phase1_workflow()
        results["phase1_workflow"] = "✅ PASS"
        
        # Phase 2 Tests  
        print("\n🟢 PHASE 2: CKG OPERATIONS TESTING")
        print("-" * 40)
        
        test_neo4j_connection()
        results["neo4j_connection"] = "✅ PASS"
        
        parse_result = test_java_parser_spring_petclinic(project_context)
        results["java_parser"] = "✅ PASS"
        
        build_result = test_ckg_building_spring_petclinic(parse_result)
        results["ckg_building"] = "✅ PASS"
        
        test_ckg_queries_spring_petclinic()
        results["ckg_queries"] = "✅ PASS"
        
        project_context, ckg_result = test_complete_phase2_workflow()
        results["phase2_workflow"] = "✅ PASS"
        
    except Exception as e:
        results["error"] = f"❌ FAIL: {str(e)}"
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{test_name:25} | {result}")
    
    total_tests = len([r for r in results.values() if r.startswith("✅")])
    failed_tests = len([r for r in results.values() if r.startswith("❌")])
    
    print(f"\n📈 Summary: {total_tests} passed, {failed_tests} failed")
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! Phase 1 & 2 fully functional!")
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    run_comprehensive_tests()
```

### 📋 **EXECUTION INSTRUCTIONS**

#### 1. **Environment Setup**
```bash
# 1. Start Docker environment
cd backend
docker-compose -f docker-compose.test.yml up -d

# 2. Wait for Neo4j to be ready
docker-compose -f docker-compose.test.yml logs -f neo4j

# 3. Access backend container
docker exec -it repochat-backend-test bash
```

#### 2. **Run Tests**
```bash
# Inside container
cd /app
export PYTHONPATH=/app/src

# Run individual test modules
python test_phase1_orchestrator.py
python test_phase2_neo4j.py

# Or run complete suite
python run_comprehensive_tests.py
```

#### 3. **Verify Results**

**Neo4j Browser**: `http://localhost:7474`
- Username: `neo4j`
- Password: `repochat123`

**Sample Queries**:
```cypher
// Check total nodes and relationships
MATCH (n) RETURN count(n) as total_nodes
MATCH ()-[r]->() RETURN count(r) as total_relationships

// View Spring PetClinic structure
MATCH (c:Class) 
WHERE c.name CONTAINS "Pet" OR c.name CONTAINS "Owner" OR c.name CONTAINS "Vet"
RETURN c.name, c.file_path
LIMIT 10

// Check method calls
MATCH (m1:Method)-[:CALLS]->(m2:Method)
RETURN m1.name, m2.name
LIMIT 10
```

### ✅ **SUCCESS CRITERIA**

#### **Phase 1 Success Indicators:**
- ✅ Repository cloned successfully (~50+ files)
- ✅ Java detected as primary language
- ✅ ProjectDataContext created with valid data
- ✅ No exceptions during workflow

#### **Phase 2 Success Indicators:**
- ✅ Neo4j connection established
- ✅ Java files parsed (20+ classes expected)
- ✅ CKG nodes created (100+ nodes expected) 
- ✅ Relationships established (50+ relationships expected)
- ✅ Spring components (Controllers, Services) identified
- ✅ Query interface returns valid results

#### **Performance Benchmarks:**
- Repository clone: < 30 seconds
- Language detection: < 5 seconds
- Java parsing: < 60 seconds
- CKG building: < 120 seconds
- Total workflow: < 300 seconds

This comprehensive test suite validates tất cả tính năng Phase 1 và 2 với real-world Java project! 