# RepoChat Phase 1-3 Testing Infrastructure

## 🎯 Overview

Complete testing infrastructure cho RepoChat Phase 1-3 với real OpenAI API integration và real repository testing. Infrastructure này cung cấp automated setup, comprehensive testing suite, và detailed result analysis.

## 📁 Testing Files Structure

```
backend/
├── 🧪 Testing Infrastructure
│   ├── comprehensive_phase_1_3_manual_test.py   # Main test suite
│   ├── PHASE_1_3_TESTING_GUIDE.md              # Detailed testing guide
│   ├── TESTING_INFRASTRUCTURE_README.md         # This file
│   ├── setup_test_environment.sh                # Automated setup script
│   ├── run_tests.sh                            # Quick test runner
│   └── env_example.txt                         # Environment configuration example
│
├── 📊 Test Results & Logs
│   ├── test_results/                           # JSON test results
│   ├── logs/                                   # Detailed test logs
│   └── temp/                                   # Temporary repositories
│
├── 🔧 Configuration
│   ├── .env                                    # Environment variables (create from example)
│   └── requirements.txt                        # Python dependencies
│
└── 📚 Documentation
    ├── docs/architecture_overview_phase_1_3.md
    ├── docs/data_flow_architecture_phase_1_3.md
    └── docs/sequence_diagrams_phase_1_3.md
```

## 🚀 Quick Start

### 1. Automated Setup (Recommended)

```bash
# Navigate to backend directory
cd backend

# Run automated setup script
./setup_test_environment.sh

# Setup will:
# ✅ Check prerequisites (Python, Git, Docker)
# ✅ Create virtual environment
# ✅ Install dependencies
# ✅ Setup Neo4j database (Docker)
# ✅ Create .env configuration file
# ✅ Test all connections
```

### 2. Configure Environment

Edit `.env` file với your actual values:

```bash
# Edit environment configuration
nano .env

# Required: Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Update other settings as needed
NEO4J_PASSWORD=your-preferred-password
```

### 3. Run Tests

```bash
# Quick test scenarios
./run_tests.sh 1    # Quick test (small repo)
./run_tests.sh 2    # Java repository test
./run_tests.sh 3    # Python repository test
./run_tests.sh 4    # Full LLM test (requires API key)

# Custom repository test
./run_tests.sh https://github.com/your-org/your-repo.git

# Direct comprehensive test
python comprehensive_phase_1_3_manual_test.py --openai-test
```

## 🧪 Test Suite Components

### Main Test Suite: `comprehensive_phase_1_3_manual_test.py`

Comprehensive testing for all Phase 1-3 functionality:

#### Phase 1: Data Acquisition & CKG Operations
- ✅ **Repository Cloning**: Git operations với multiple repositories
- ✅ **Language Detection**: Multi-language identification
- ✅ **Data Preparation**: Project context creation
- ✅ **Code Parsing**: Multi-language AST parsing
- ✅ **Neo4j Integration**: CKG construction và queries
- ✅ **Graph Operations**: Node/relationship creation

#### Phase 2: Code Analysis & LLM Services
- ✅ **Architectural Analysis**: Circular dependency detection
- ✅ **PR Impact Analysis**: Change impact assessment
- ✅ **Static Analysis Integration**: Placeholder functionality
- ✅ **LLM Gateway**: Request routing và processing
- ✅ **Team LLM Services**: Provider abstraction
- ✅ **Analysis Enhancement**: LLM-powered insights

#### Phase 3: Orchestrator Integration
- ✅ **Task Definition**: Standardized task specs
- ✅ **Orchestrator Execution**: End-to-end coordination
- ✅ **Component Integration**: Cross-phase communication
- ✅ **Error Handling**: Graceful failure recovery
- ✅ **Result Aggregation**: Comprehensive reporting

### Test Scenarios

#### 1. Small Repository Test
```bash
./run_tests.sh 1
# Repository: Hello-World (GitHub)
# Expected: <10s execution, basic functionality verification
```

#### 2. Java Repository Test  
```bash
./run_tests.sh 2
# Repository: Spring PetClinic
# Expected: Java AST parsing, Spring patterns detection
```

#### 3. Python Repository Test
```bash
./run_tests.sh 3
# Repository: Flask framework
# Expected: Python AST parsing, Flask patterns detection
```

#### 4. LLM Integration Test
```bash
./run_tests.sh 4
# Includes: Real OpenAI API calls, enhanced analysis
# Required: OPENAI_API_KEY in .env
```

#### 5. Performance Test
```bash
./run_tests.sh 5
# Multiple repositories, performance benchmarking
# Includes: Timing analysis, resource usage monitoring
```

## 📊 Test Results Analysis

### JSON Results Structure

```json
{
  "test_suite": "Comprehensive Phase 1-3 Testing",
  "start_time": "2024-12-28T10:00:00Z",
  "repo_url": "https://github.com/spring-projects/spring-petclinic.git",
  "config": {
    "has_openai_key": true,
    "has_neo4j_config": true
  },
  "phases": [
    {
      "phase": "Phase 1 - Data Acquisition",
      "success": true,
      "tests": [
        {
          "test_name": "Repository Cloning",
          "success": true,
          "duration_ms": 1500,
          "details": {...}
        }
      ]
    }
  ],
  "summary": {
    "total_phases": 5,
    "total_tests": 18,
    "successful_tests": 17,
    "success_rate": 94.4,
    "overall_success": true
  }
}
```

### Result Analysis Commands

```bash
# View test summary
cat test_results/comprehensive_test_results_*.json | jq '.summary'

# Check success rate
cat test_results/comprehensive_test_results_*.json | jq '.summary.success_rate'

# View failed tests
cat test_results/comprehensive_test_results_*.json | jq '.phases[].tests[] | select(.success == false)'

# Performance analysis
cat test_results/comprehensive_test_results_*.json | jq '.phases[].tests[] | {name: .test_name, duration: .duration_ms}'
```

## 🔧 Environment Configuration

### Required Environment Variables

```env
# OpenAI Configuration (Required for LLM tests)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.1

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=repochat123

# Git Configuration (Optional)
GITHUB_TOKEN=ghp_your-token-here

# Testing Configuration
TEST_REPO_URL=https://github.com/spring-projects/spring-petclinic.git
LOG_LEVEL=DEBUG
```

### Dependencies

```bash
# Core dependencies (from requirements.txt)
fastapi>=0.68.0
pydantic>=1.8.0
neo4j>=5.0.0
openai>=1.0.0

# Testing dependencies (installed by setup script)
python-dotenv
pytest-asyncio
psutil  # For performance monitoring
```

## 🔍 Manual Testing Procedures

### Individual Component Testing

#### Test Git Operations
```bash
cd backend
python -c "
import asyncio
import sys
sys.path.append('src')
from teams.data_acquisition.git_operations_module import GitOperationsModule

async def test():
    git_ops = GitOperationsModule()
    result = await git_ops.clone_repository('https://github.com/octocat/Hello-World.git')
    print(f'Clone result: {result}')

asyncio.run(test())
"
```

#### Test Language Detection
```bash
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.append('src')
from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule

async def test():
    lang_id = LanguageIdentifierModule()
    test_path = Path('temp/Hello-World')
    if test_path.exists():
        result = await lang_id.analyze_project_languages(test_path)
        print(f'Detected languages: {result}')

asyncio.run(test())
"
```

#### Test Neo4j Connection
```bash
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'repochat123'))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    print('Neo4j connection:', result.single()['test'])
driver.close()
"
```

#### Test OpenAI API
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    response = openai.Model.list()
    print('OpenAI API connection successful')
except Exception as e:
    print(f'API connection failed: {e}')
"
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Neo4j Connection Failed
```bash
# Check Neo4j status
docker ps | grep neo4j

# Restart Neo4j
docker restart neo4j-repochat

# Check logs
docker logs neo4j-repochat
```

#### 2. OpenAI API Issues
```bash
# Verify API key format
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('OPENAI_API_KEY')
print(f'Key valid: {key.startswith(\"sk-\") if key else False}')
"
```

#### 3. Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Repository Cloning Issues
```bash
# Test manual clone
git clone https://github.com/octocat/Hello-World.git temp/test

# Check network
ping github.com

# For private repos, verify token
echo $GITHUB_TOKEN
```

### Performance Issues

#### Large Repository Handling
```bash
# Use smaller repositories for testing
TEST_REPO=https://github.com/octocat/Hello-World.git

# Increase timeouts
export GIT_CLONE_TIMEOUT=600
export PARSING_TIMEOUT=1200
```

#### Memory Usage Monitoring
```bash
# Monitor during tests
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

| Operation | Small Repo | Medium Repo | Large Repo |
|-----------|------------|-------------|------------|
| Git Clone | <10s | 10-30s | 30-120s |
| Language Detection | <1s | 1-5s | 5-15s |
| Code Parsing | <5s | 5-30s | 30-300s |
| CKG Construction | <5s | 5-60s | 60-600s |
| Architectural Analysis | <3s | 3-15s | 15-120s |
| LLM Request | 2-10s | 2-10s | 2-10s |

### Repository Size Categories

- **Small**: <100 files (Hello-World)
- **Medium**: 100-1000 files (Spring PetClinic)
- **Large**: >1000 files (VS Code, Linux Kernel)

## ✅ Success Criteria

### Overall Success Metrics
- ✅ **>90% test success rate**
- ✅ **All core functionality working**
- ✅ **Performance within expected ranges**
- ✅ **Error handling graceful**
- ✅ **Real OpenAI API integration**

### Phase-Specific Success Criteria

#### Phase 1 Success
- Repository cloning successful
- Languages detected correctly
- Code entities parsed và extracted
- Neo4j connection established
- CKG construction completed

#### Phase 2 Success
- Architectural analysis produces findings
- PR impact analysis working
- LLM requests processed successfully
- Static analysis integration functional

#### Phase 3 Success
- Orchestrator coordinates all phases
- Task definitions processed correctly
- End-to-end workflow functional
- Error handling working properly

## 🔄 CI/CD Integration

### GitHub Actions Integration (Future)

```yaml
name: RepoChat Phase 1-3 Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:latest
        env:
          NEO4J_AUTH: neo4j/test123
        ports:
          - 7687:7687
          - 7474:7474
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install python-dotenv pytest-asyncio
    
    - name: Run tests
      env:
        NEO4J_URI: bolt://localhost:7687
        NEO4J_USERNAME: neo4j
        NEO4J_PASSWORD: test123
      run: |
        cd backend
        python comprehensive_phase_1_3_manual_test.py --repo-url https://github.com/octocat/Hello-World.git
```

## 📞 Support & Next Steps

### For Issues
1. **Check logs**: Review detailed test logs
2. **Verify configuration**: Ensure all env vars set
3. **Test components individually**: Isolate issues
4. **Check dependencies**: Ensure services running

### Phase 4 Preparation
Testing infrastructure đã sẵn sàng cho Phase 4 CLI development:
- ✅ Complete testing framework
- ✅ Environment automation
- ✅ Performance benchmarking
- ✅ Real API integration
- ✅ Comprehensive documentation

### Future Enhancements
- Integration với CI/CD pipelines
- Automated performance regression testing
- Test report generation và visualization
- Multi-environment testing (dev, staging, prod)

---

**🎯 RepoChat Phase 1-3 Testing Infrastructure Complete!**

Comprehensive testing solution với automated setup, extensive test coverage, và production-ready monitoring. Ready for Phase 4 CLI development! 🚀 