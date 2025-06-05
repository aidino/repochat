# RepoChat Phase 1-3 Comprehensive Testing Guide

## 🎯 Overview

Hướng dẫn testing toàn diện cho RepoChat Phase 1-3 với real OpenAI API và real repositories. Guide này bao gồm environment setup, manual testing procedures, và automated test execution.

## 📋 Table of Contents

1. [Environment Setup](#environment-setup)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Manual Testing Procedures](#manual-testing-procedures)
5. [Automated Testing](#automated-testing)
6. [Test Scenarios](#test-scenarios)
7. [Troubleshooting](#troubleshooting)

## 🛠️ Environment Setup

### Prerequisites

#### 1. System Requirements
```bash
# Python 3.8+
python --version

# Git installed
git --version

# Docker (optional, for Neo4j)
docker --version
```

#### 2. Python Dependencies
```bash
# Install required packages
cd backend
pip install -r requirements.txt

# Additional packages for testing
pip install python-dotenv pytest-asyncio
```

#### 3. Neo4j Database Setup

**Option A: Docker (Recommended)**
```bash
# Start Neo4j with Docker
docker run \
    --name neo4j-repochat \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/repochat123 \
    neo4j:latest

# Verify Neo4j is running
curl -u neo4j:repochat123 http://localhost:7474/db/data/
```

**Option B: Local Installation**
```bash
# Download and install Neo4j
# https://neo4j.com/download/

# Start Neo4j
neo4j start

# Access Neo4j Browser: http://localhost:7474
# Default credentials: neo4j/neo4j (change on first login)
```

## ⚙️ Configuration

### 1. Create Environment File

Tạo file `.env` trong backend folder:

```bash
cd backend
cp .env.example .env  # If exists, or create new file
```

### 2. Environment Variables

**`.env` file configuration:**

```env
# =============================================================================
# OPENAI CONFIGURATION (REQUIRED FOR LLM TESTING)
# =============================================================================
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Organization ID if you have one
OPENAI_ORG_ID=org-your-org-id-here

# Model configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.1

# =============================================================================
# NEO4J CONFIGURATION
# =============================================================================
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=repochat123
NEO4J_DATABASE=repochat

# =============================================================================
# GIT CONFIGURATION (OPTIONAL)
# =============================================================================
# For private repositories (optional)
GITHUB_TOKEN=ghp_your-github-token-here

# Git user info
GIT_USERNAME=your-github-username
GIT_EMAIL=your-email@example.com

# =============================================================================
# TESTING CONFIGURATION
# =============================================================================
# Test repositories
TEST_REPO_URL=https://github.com/spring-projects/spring-petclinic.git
TEST_REPO_SMALL=https://github.com/octocat/Hello-World.git
TEST_REPO_PYTHON=https://github.com/pallets/flask.git
TEST_REPO_MULTI=https://github.com/microsoft/vscode.git

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/repochat_test.log

# Performance settings
GIT_CLONE_TIMEOUT=300
PARSING_TIMEOUT=600
LLM_REQUEST_TIMEOUT=60
NEO4J_QUERY_TIMEOUT=30
```

### 3. Verify Configuration

```bash
# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'repochat123'))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    print('Neo4j connection:', result.single()['test'])
driver.close()
"

# Test OpenAI API (if configured)
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print('OpenAI API Key configured:', bool(api_key and api_key.startswith('sk-')))
"
```

## 🧪 Manual Testing Procedures

### Phase 1: Data Acquisition & CKG Operations

#### Test 1.1: Repository Cloning
```bash
cd backend
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.data_acquisition.git_operations_module import GitOperationsModule

async def test():
    git_ops = GitOperationsModule()
    result = await git_ops.clone_repository('https://github.com/spring-projects/spring-petclinic.git')
    print(f'Clone result: {result}')
    print(f'Path exists: {result.exists() if result else False}')

asyncio.run(test())
"
```

#### Test 1.2: Language Detection
```bash
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.append('src')
from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule

async def test():
    lang_id = LanguageIdentifierModule()
    # Use path from previous test
    test_path = Path('temp/spring-petclinic')  # Adjust path as needed
    if test_path.exists():
        result = await lang_id.analyze_project_languages(test_path)
        print(f'Detected languages: {result}')
    else:
        print('No cloned repository found. Run clone test first.')

asyncio.run(test())
"
```

#### Test 1.3: Code Parsing
```bash
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule
from data_models.project_data_context import ProjectDataContext

async def test():
    parser = CodeParserCoordinatorModule()
    context = ProjectDataContext(
        cloned_code_path='temp/spring-petclinic',
        detected_languages=['java'],
        repository_url='https://github.com/spring-projects/spring-petclinic.git'
    )
    
    entities = await parser.parse_project(context)
    print(f'Parsed {len(entities)} entities')
    for entity in entities[:5]:  # Show first 5
        print(f'  - {entity.entity_type.value}: {entity.name}')

asyncio.run(test())
"
```

#### Test 1.4: Neo4j Integration
```bash
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule

async def test():
    neo4j = Neo4jConnectionModule(
        uri='bolt://localhost:7687',
        username='neo4j',
        password='repochat123'
    )
    
    result = await neo4j.test_connection()
    print(f'Neo4j connection: {result}')
    
    if result:
        # Test basic query
        with neo4j.driver.session() as session:
            result = session.run('MATCH (n) RETURN count(n) as node_count')
            count = result.single()['node_count']
            print(f'Total nodes in database: {count}')

asyncio.run(test())
"
```

### Phase 2: Code Analysis & LLM Services

#### Test 2.1: Architectural Analysis
```bash
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from data_models.project_data_context import ProjectDataContext

async def test():
    analyzer = ArchitecturalAnalyzerModule()
    context = ProjectDataContext(
        cloned_code_path='temp/spring-petclinic',
        detected_languages=['java'],
        repository_url='https://github.com/spring-projects/spring-petclinic.git'
    )
    
    result = await analyzer.analyze_project_architecture(context)
    print(f'Analysis completed: {result is not None}')
    if result:
        print(f'Found {len(result.findings)} findings')
        for finding in result.findings[:3]:  # Show first 3
            print(f'  - {finding.finding_type.value}: {finding.description[:100]}...')

asyncio.run(test())
"
```

#### Test 2.2: LLM Services (requires OpenAI API key)
```bash
python -c "
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()
sys.path.append('src')

if os.getenv('OPENAI_API_KEY'):
    from teams.llm_services.llm_gateway_module import LLMGatewayModule
    from data_models.llm_models import LLMServiceRequest
    
    async def test():
        gateway = LLMGatewayModule()
        
        request = LLMServiceRequest(
            request_id='test-123',
            prompt='Analyze this Java class structure: public class Example { private String name; public String getName() { return name; } }',
            context={'language': 'java', 'purpose': 'code_review'},
            max_tokens=200,
            temperature=0.1
        )
        
        result = await gateway.process_request(request)
        print(f'LLM request processed: {result is not None}')
        if result:
            print(f'Response content: {result.content[:200]}...')
    
    asyncio.run(test())
else:
    print('OpenAI API key not configured. Skipping LLM test.')
"
```

### Phase 3: Orchestrator Integration

#### Test 3.1: End-to-End Orchestration
```bash
python -c "
import asyncio
import sys
sys.path.append('src')
from orchestrator.orchestrator_agent import OrchestratorAgent
from data_models.task_definition import TaskDefinition

async def test():
    orchestrator = OrchestratorAgent()
    
    task = TaskDefinition(
        task_id='test-e2e-123',
        task_type='repository_analysis',
        repository_url='https://github.com/octocat/Hello-World.git',  # Small repo
        user_id='test-user',
        llm_config={'model': 'gpt-4', 'temperature': 0.1},
        metadata={'test_mode': True}
    )
    
    result = await orchestrator.execute_task(task)
    print(f'Orchestration completed: {result is not None}')
    if result:
        print(f'Result type: {type(result)}')
        print(f'Result length: {len(result) if hasattr(result, \"__len__\") else \"N/A\"}')

asyncio.run(test())
"
```

## 🤖 Automated Testing

### Run Comprehensive Test Suite

```bash
cd backend
python comprehensive_phase_1_3_manual_test.py
```

### Test with Different Repositories

```bash
# Test with Spring PetClinic (Java)
python comprehensive_phase_1_3_manual_test.py --repo-url https://github.com/spring-projects/spring-petclinic.git

# Test with Flask (Python)
python comprehensive_phase_1_3_manual_test.py --repo-url https://github.com/pallets/flask.git

# Test with small repository
python comprehensive_phase_1_3_manual_test.py --repo-url https://github.com/octocat/Hello-World.git

# Include LLM tests (requires OpenAI API key)
python comprehensive_phase_1_3_manual_test.py --openai-test --repo-url https://github.com/spring-projects/spring-petclinic.git

# Save results to specific file
python comprehensive_phase_1_3_manual_test.py --output my_test_results.json
```

### Test Results Analysis

```bash
# View test results
cat test_results/comprehensive_test_results_*.json | jq '.summary'

# Check success rate
cat test_results/comprehensive_test_results_*.json | jq '.summary.success_rate'

# View failed tests
cat test_results/comprehensive_test_results_*.json | jq '.phases[].tests[] | select(.success == false)'
```

## 📊 Test Scenarios

### Scenario 1: Java Repository Analysis
```bash
# Test với Spring PetClinic
TEST_REPO=https://github.com/spring-projects/spring-petclinic.git
python comprehensive_phase_1_3_manual_test.py --repo-url $TEST_REPO --openai-test

# Expected results:
# - Java language detection
# - AST parsing of Java files
# - CKG construction with Java entities
# - Architectural analysis findings
# - LLM-enhanced code insights
```

### Scenario 2: Python Repository Analysis
```bash
# Test với Flask
TEST_REPO=https://github.com/pallets/flask.git
python comprehensive_phase_1_3_manual_test.py --repo-url $TEST_REPO --openai-test

# Expected results:
# - Python language detection
# - AST parsing of Python files
# - Function and class extraction
# - Architectural patterns detection
```

### Scenario 3: Multi-Language Repository
```bash
# Test với VS Code (TypeScript, JavaScript, etc.)
TEST_REPO=https://github.com/microsoft/vscode.git
python comprehensive_phase_1_3_manual_test.py --repo-url $TEST_REPO

# Expected results:
# - Multiple languages detected
# - Mixed parsing strategies
# - Complex architectural analysis
# Note: Large repository - may take longer
```

### Scenario 4: PR Impact Analysis
```bash
# Test PR impact analysis with sample data
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.code_analysis.pr_impact_analyzer_module import PRImpactAnalyzerModule
from data_models.project_data_context import ProjectDataContext, PRDiffInfo

async def test():
    analyzer = PRImpactAnalyzerModule()
    
    pr_diff = PRDiffInfo(
        pr_id='test-pr-456',
        pr_url='https://github.com/test/repo/pull/456',
        base_branch='main',
        head_branch='feature/new-feature',
        raw_diff='sample diff content',
        changed_files=['src/main/Controller.java', 'src/main/Service.java'],
        file_changes={
            'src/main/Controller.java': 'modified',
            'src/main/Service.java': 'added'
        },
        function_changes=['getUserById', 'createUser', 'validateUser']
    )
    
    context = ProjectDataContext(
        cloned_code_path='temp/spring-petclinic',
        detected_languages=['java'],
        repository_url='https://github.com/spring-projects/spring-petclinic.git',
        pr_diff_info=pr_diff
    )
    
    result = await analyzer.analyze_pr_impact(context)
    print(f'PR Impact Analysis completed: {result is not None}')
    if result:
        print(f'Impact findings: {len(result.findings)}')
        for finding in result.findings:
            print(f'  - {finding.finding_type.value}: {finding.description}')

asyncio.run(test())
"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Neo4j Connection Failed
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j-repochat

# Restart Neo4j
docker restart neo4j-repochat

# Test connection manually
python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'repochat123'))
    with driver.session() as session:
        result = session.run('RETURN 1')
        print('Connection successful')
    driver.close()
except Exception as e:
    print(f'Connection failed: {e}')
"
```

#### 2. OpenAI API Issues
```bash
# Verify API key format
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('OPENAI_API_KEY')
if key:
    print(f'API key starts correctly: {key.startswith(\"sk-\")}')
    print(f'API key length: {len(key)}')
else:
    print('No API key found')
"

# Test API connection
python -c "
import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
try:
    response = openai.Model.list()
    print('OpenAI API connection successful')
    print(f'Available models: {len(response[\"data\"])}')
except Exception as e:
    print(f'API connection failed: {e}')
"
```

#### 3. Repository Cloning Issues
```bash
# Check Git configuration
git config --list | grep user

# Test manual clone
git clone https://github.com/octocat/Hello-World.git temp/test-clone

# Check network connectivity
ping github.com

# For private repos, check token
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
print(f'GitHub token configured: {bool(token)}')
"
```

#### 4. Python Import Issues
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if src directory in path
python -c "
import sys
import os
src_path = os.path.join(os.getcwd(), 'src')
print(f'Src path: {src_path}')
print(f'Src exists: {os.path.exists(src_path)}')
print(f'Src in sys.path: {src_path in sys.path}')
"

# Install missing dependencies
pip install -r requirements.txt
```

### Performance Issues

#### 1. Large Repository Handling
```bash
# Use smaller repositories for testing
TEST_REPO=https://github.com/octocat/Hello-World.git

# Increase timeouts in .env
echo "GIT_CLONE_TIMEOUT=600" >> .env
echo "PARSING_TIMEOUT=1200" >> .env
```

#### 2. Memory Usage
```bash
# Monitor memory usage during tests
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Cleanup temp directories
rm -rf temp/*
```

### Log Analysis

#### 1. Check Test Logs
```bash
# View latest test log
tail -f logs/comprehensive_test_*.log

# Filter for errors
grep -i error logs/comprehensive_test_*.log

# Check performance metrics
grep -i "duration_ms" logs/comprehensive_test_*.log
```

#### 2. Component-Specific Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check specific component logs
grep "GitOperationsModule" logs/comprehensive_test_*.log
grep "LLMGatewayModule" logs/comprehensive_test_*.log
grep "ArchitecturalAnalyzerModule" logs/comprehensive_test_*.log
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

| Operation | Small Repo (<100 files) | Medium Repo (100-1000 files) | Large Repo (>1000 files) |
|-----------|-------------------------|-------------------------------|---------------------------|
| Git Clone | <10s | 10-30s | 30-120s |
| Language Detection | <1s | 1-5s | 5-15s |
| Code Parsing | <5s | 5-30s | 30-300s |
| CKG Construction | <5s | 5-60s | 60-600s |
| Architectural Analysis | <3s | 3-15s | 15-120s |
| LLM Request | 2-10s | 2-10s | 2-10s |

### Performance Testing

```bash
# Run performance benchmark
python -c "
import time
import asyncio
import sys
sys.path.append('src')

async def benchmark():
    print('=== RepoChat Performance Benchmark ===')
    
    # Test with different repo sizes
    repos = [
        ('Small', 'https://github.com/octocat/Hello-World.git'),
        ('Medium', 'https://github.com/spring-projects/spring-petclinic.git'),
    ]
    
    for size, repo_url in repos:
        print(f'\nTesting {size} repository: {repo_url}')
        start_time = time.time()
        
        # Add actual performance testing here
        # This is a placeholder for demonstration
        
        end_time = time.time()
        print(f'{size} repo processing time: {end_time - start_time:.2f}s')

asyncio.run(benchmark())
"
```

## ✅ Success Criteria

### Phase 1 Success Criteria
- ✅ Repository cloning successful
- ✅ Languages detected correctly
- ✅ Code entities parsed and extracted
- ✅ Neo4j connection established
- ✅ CKG construction completed
- ✅ Basic graph queries working

### Phase 2 Success Criteria
- ✅ Architectural analysis produces findings
- ✅ PR impact analysis working
- ✅ LLM requests processed successfully
- ✅ Static analysis integration functional
- ✅ Analysis results properly formatted

### Phase 3 Success Criteria
- ✅ Orchestrator coordinates all phases
- ✅ Task definitions processed correctly
- ✅ End-to-end workflow functional
- ✅ Error handling working properly
- ✅ Results aggregated correctly

### Overall Success Criteria
- ✅ >90% test success rate
- ✅ All core functionality working
- ✅ Performance within expected ranges
- ✅ Error handling graceful
- ✅ Documentation complete

---

## 📞 Support

For issues with this testing guide:

1. **Check logs**: Review test logs for specific error messages
2. **Verify configuration**: Ensure all environment variables are set
3. **Test components individually**: Use manual test procedures to isolate issues
4. **Check dependencies**: Ensure all required services are running
5. **Review documentation**: Check Phase 1-3 architecture documentation

**Happy Testing! 🚀** 