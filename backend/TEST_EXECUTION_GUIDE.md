# 🧪 Hướng Dẫn Test Manual - Phase 1 & 2
## Testing RepoChat với Project Java Thực Tế

### 📋 **OVERVIEW**

Test suite này validate toàn bộ functionality của Phase 1 (Data Acquisition) và Phase 2 (CKG Operations) bằng cách sử dụng **Spring PetClinic** - một real-world Java project.

**Test Coverage:**
- ✅ **Phase 1**: Git Operations, Language Detection, Data Preparation
- ✅ **Phase 2**: Neo4j Connection, Java Parsing, CKG Building, Querying
- ✅ **Integration**: Complete Orchestrator workflow

### 🐳 **ENVIRONMENT SETUP**

#### 1. **Prerequisites**
```bash
# Kiểm tra Docker installed
docker --version
docker-compose --version

# Kiểm tra current directory
pwd  # Should be in /path/to/repochat/backend
```

#### 2. **Start Test Environment**
```bash
# 1. Navigate to backend directory
cd backend

# 2. Build and start services
docker-compose -f docker-compose.test.yml up -d

# 3. Check services status
docker-compose -f docker-compose.test.yml ps

# Expected output:
# NAME                   IMAGE             STATUS
# repochat-backend-test  backend_repochat  Up
# repochat-neo4j-test    neo4j:5.11        Up (healthy)
```

#### 3. **Verify Neo4j Connection**
```bash
# Check Neo4j logs
docker-compose -f docker-compose.test.yml logs neo4j

# Should see: "Remote interface available at http://localhost:7474/"

# Test browser interface
curl -f http://localhost:7474 || echo "Neo4j browser not ready"
```

#### 4. **Access Backend Container**
```bash
# Enter backend container
docker exec -it repochat-backend-test bash

# Verify Python environment
python --version  # Should be 3.12+
echo $PYTHONPATH   # Should be /app/src

# Test imports
python -c "from orchestrator.orchestrator_agent import OrchestratorAgent; print('✅ Imports OK')"
```

### 🎯 **EXECUTION METHODS**

#### **Method 1: Complete Test Suite**
```bash
# Inside backend container
cd /app
python run_comprehensive_tests.py
```

**Expected Output:**
```
🚀 Starting Comprehensive Manual Test Suite
📋 Testing Phase 1 & 2 with Spring PetClinic
============================================================

🔵 PHASE 1: DATA ACQUISITION TESTING
--------------------------------------------------

🧪 Testing: OrchestratorAgent Initialization
✅ PASS - orchestrator_init (1.23s)
    Agent ID: 12ab34cd

🧪 Testing: Git Operations - Spring PetClinic Clone
✅ PASS - git_operations (15.67s)
    Cloned to /tmp/spring-petclinic, 45 Java files

... (more test results)

📊 FINAL TEST RESULTS
============================================================
orchestrator_init         | ✅ PASS  |   1.23s | Agent ID: 12ab34cd
git_operations            | ✅ PASS  |  15.67s | Cloned to /tmp/spring-petclinic, 45 Java files
language_identification   | ✅ PASS  |   2.34s | Languages: ['java'], Java files: 45
...
```

#### **Method 2: Individual Test Components**
```bash
# Test individual phases
python -c "
from run_comprehensive_tests import TestRunner
runner = TestRunner()
runner.test_neo4j_connection()
runner.print_final_results()
"
```

#### **Method 3: Interactive Testing**
```python
# Start Python interactive session
python

# Import và test manually
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition

# Test specific component
orchestrator = OrchestratorAgent()
task = TaskDefinition(repository_url="https://github.com/spring-projects/spring-petclinic.git")
result = orchestrator.handle_scan_project_task(task)
print(f"Result: {result.detected_languages}")
```

### 🔍 **VERIFICATION STEPS**

#### **1. Phase 1 Verification**
```bash
# Check git clone worked
ls -la /tmp/repochat-test/
find /tmp -name "*spring-petclinic*" -type d

# Verify Java files detected
find /tmp -name "*.java" | head -10
```

#### **2. Phase 2 Verification - Neo4j Browser**

**Access Neo4j Browser**: `http://localhost:7474`
- **Username**: `neo4j`
- **Password**: `repochat123`

**Verification Queries:**
```cypher
// 1. Check total nodes và relationships
MATCH (n) RETURN count(n) as total_nodes
MATCH ()-[r]->() RETURN count(r) as total_relationships

// 2. View node types distribution
MATCH (n) 
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC

// 3. Find Spring PetClinic entities
MATCH (c:Class) 
WHERE c.name CONTAINS "Pet" OR c.name CONTAINS "Owner" OR c.name CONTAINS "Vet"
RETURN c.name, c.file_path
LIMIT 10

// 4. Check method calls
MATCH (m1:Method)-[:CALLS]->(m2:Method)
RETURN m1.name as caller, m2.name as callee
LIMIT 10

// 5. Find Spring Controllers
MATCH (c:Class) 
WHERE c.name ENDS WITH "Controller"
RETURN c.name as controller, c.file_path as file
ORDER BY c.name
```

**Expected Results:**
- **Total Nodes**: 200-500 nodes
- **Total Relationships**: 100-300 relationships  
- **Node Types**: Class, Method, Field, Parameter
- **Spring Components**: PetController, OwnerController, VetController, etc.

#### **3. Log Verification**
```bash
# Check application logs
tail -f /app/logs/repochat.log

# Check specific component logs
grep "CKG" /app/logs/repochat.log
grep "TEAM Data Acquisition" /app/logs/repochat.log
```

### 📊 **SUCCESS CRITERIA**

#### **Phase 1 Success Indicators**
| Test | Expected Result | Verification |
|------|----------------|--------------|
| **Git Clone** | Repository cloned, 40+ Java files | Check `/tmp/spring-petclinic` exists |
| **Language Detection** | Java detected as primary | `detected_languages` contains "java" |
| **Data Preparation** | ProjectDataContext created | Context has valid paths and metadata |

#### **Phase 2 Success Indicators**
| Test | Expected Result | Verification |
|------|----------------|--------------|
| **Neo4j Connection** | Connected successfully | Health check passes |
| **Java Parsing** | 40+ classes, 200+ methods parsed | Parser results statistics |
| **CKG Building** | 200+ nodes, 100+ relationships | Neo4j node/relationship counts |
| **CKG Querying** | Queries return valid results | Spring components found |

#### **Performance Benchmarks**
- **Repository Clone**: < 30 seconds
- **Language Detection**: < 5 seconds  
- **Java Parsing**: < 60 seconds
- **CKG Building**: < 120 seconds
- **Total Workflow**: < 300 seconds

### 🐛 **TROUBLESHOOTING**

#### **Common Issues & Solutions**

**1. Neo4j Connection Failed**
```bash
# Check Neo4j container
docker logs repochat-neo4j-test

# Restart if needed
docker-compose -f docker-compose.test.yml restart neo4j

# Wait for health check
docker-compose -f docker-compose.test.yml ps
```

**2. Git Clone Timeout**
```bash
# Check internet connection
curl -I https://github.com

# Try manual clone
git clone https://github.com/spring-projects/spring-petclinic.git /tmp/test-clone
```

**3. Import Errors**
```bash
# Check Python path
echo $PYTHONPATH

# Verify file structure
ls -la /app/src/orchestrator/
ls -la /app/src/teams/

# Test specific import
python -c "import sys; print(sys.path)"
```

**4. Memory Issues**
```bash
# Check container memory
docker stats repochat-backend-test repochat-neo4j-test

# Increase Neo4j memory if needed (edit docker-compose.test.yml)
NEO4J_dbms_memory_heap_max_size=4G
```

**5. Port Conflicts**
```bash
# Check port usage
netstat -tlnp | grep 7474
netstat -tlnp | grep 7687

# Kill conflicting processes
sudo fuser -k 7474/tcp
sudo fuser -k 7687/tcp
```

### 🧹 **CLEANUP**

#### **After Testing**
```bash
# Stop và remove containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (optional - clears Neo4j data)
docker-compose -f docker-compose.test.yml down -v

# Clean up test files
rm -rf /tmp/repochat-test/
rm -rf /tmp/*spring-petclinic*
```

#### **Reset for Fresh Test**
```bash
# Complete cleanup và restart
docker-compose -f docker-compose.test.yml down -v
docker system prune -f
docker-compose -f docker-compose.test.yml up -d

# Wait for services
sleep 30
docker-compose -f docker-compose.test.yml ps
```

### 📁 **TEST PROJECT DETAILS**

#### **Spring PetClinic Structure**
```
spring-petclinic/
├── src/main/java/
│   └── org/springframework/samples/petclinic/
│       ├── PetClinicApplication.java
│       ├── model/
│       │   ├── BaseEntity.java
│       │   ├── Pet.java
│       │   ├── Owner.java
│       │   └── Vet.java
│       ├── owner/
│       │   ├── OwnerController.java
│       │   └── OwnerRepository.java
│       ├── vet/
│       │   ├── VetController.java
│       │   └── VetRepository.java
│       └── web/
│           └── WelcomeController.java
├── src/test/java/
└── pom.xml
```

#### **Expected Parsing Results**
- **Classes**: ~45 classes
- **Methods**: ~200-300 methods
- **Spring Annotations**: @Controller, @Service, @Repository
- **Relationships**: Class inheritance, method calls, field dependencies

#### **Expected CKG Structure**
```cypher
// Sample graph structure
(PetClinicApplication:Class)-[:CONTAINS]->(main:Method)
(OwnerController:Class)-[:HAS_METHOD]->(findOwners:Method)
(Owner:Class)-[:HAS_FIELD]->(pets:Field)
(findOwners:Method)-[:CALLS]->(findByLastName:Method)
```

### 🎯 **NEXT STEPS**

Sau khi tất cả tests pass:

1. **Document Results**: Capture screenshots của Neo4j browser
2. **Performance Analysis**: Record timing metrics
3. **Custom Queries**: Experiment với domain-specific queries
4. **Scale Testing**: Test với larger projects
5. **Integration**: Connect với Phase 3 (Code Analysis)

**Success = All tests pass với Spring PetClinic project!** 🎉 