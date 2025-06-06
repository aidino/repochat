# 🚀 RepoChat Multi-Agent System - Manual Test Guide

**Hướng dẫn đầy đủ để test hệ thống multi-agent với Docker environment**

---

## 📋 **Mục lục**

1. [Cài đặt Môi trường](#1-cài-đặt-môi-trường)
2. [Cấu hình Environment](#2-cấu-hình-environment)
3. [Khởi động Docker Services](#3-khởi-động-docker-services)
4. [Test Các Phase](#4-test-các-phase)
5. [Kiểm tra Logs & Results](#5-kiểm-tra-logs--results)
6. [Troubleshooting](#6-troubleshooting)

---

## 🛠️ **1. Cài đặt Môi trường**

### **Prerequisites**

```bash
# Kiểm tra Docker và Docker Compose
docker --version
docker-compose --version

# Yêu cầu tối thiểu:
# - Docker Engine 20.10+
# - Docker Compose 2.0+
# - 8GB RAM available
# - 20GB disk space
```

### **Cài đặt Dependencies**

```bash
# Clone repository
git clone <repository-url>
cd repochat

# Tạo thư mục logs và temp
mkdir -p logs temp data

# Set permissions
chmod 755 logs temp data
```

---

## ⚙️ **2. Cấu hình Environment**

### **Tạo .env file**

```bash
# Tạo .env từ template
cp .env.template .env
```

### **Cấu hình .env**

```env
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
ENVIRONMENT=development
LOGGING_LEVEL=DEBUG
LOG_FILE_PATH=./logs/repochat.log

# Multi-Agent Configuration
MULTI_AGENT_MODE=enabled
GOOGLE_ADK_ENABLED=true
A2A_PROTOCOL_ENABLED=true
MIGRATION_MANAGER_ENABLED=true

# API Configuration
API_GATEWAY_PORT=8001
MONITORING_PORT=8002
MAIN_API_PORT=8000

# Security Configuration
API_KEY_PUBLIC=rca_public_key_123
API_KEY_ENTERPRISE=rca_enterprise_key_456

# External Services (Optional)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_genai_key_here

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TOP_P=1.0
OLLAMA_TOP_K=40
OLLAMA_REPEAT_PENALTY=1.1

# Testing Configuration
TEST_MODE=enabled
MOCK_EXTERNAL_AGENTS=true
```

### **Tạo Environment Files**

```bash
# Tạo .env.development
cat > .env.development << EOF
ENVIRONMENT=development
LOGGING_LEVEL=DEBUG
MULTI_AGENT_MODE=enabled
TEST_MODE=enabled
MOCK_EXTERNAL_AGENTS=true
EOF

# Tạo .env.testing
cat > .env.testing << EOF
ENVIRONMENT=testing
LOGGING_LEVEL=INFO
MULTI_AGENT_MODE=enabled
TEST_MODE=enabled
MOCK_EXTERNAL_AGENTS=true
NEO4J_DATABASE=test_db
EOF
```

---

## 🐳 **3. Khởi động Docker Services**

### **Khởi động Multi-Agent Environment**

```bash
# Build và start tất cả services
docker-compose -f docker-compose.multiagent.yml up --build -d

# Kiểm tra status của services
docker-compose -f docker-compose.multiagent.yml ps

# Xem logs real-time
docker-compose -f docker-compose.multiagent.yml logs -f
```

### **Kiểm tra Health Check**

```bash
# Kiểm tra Neo4j
curl -u neo4j:password123 http://localhost:7474/db/data/

# Kiểm tra Redis
redis-cli ping

# Kiểm tra Main API
curl http://localhost:8000/health

# Kiểm tra API Gateway
curl http://localhost:8001/health

# Kiểm tra Monitoring
curl http://localhost:8002/health
```

### **Ports Mapping**

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Neo4j Browser | 7474 | http://localhost:7474 | Database UI |
| Neo4j Bolt | 7687 | bolt://localhost:7687 | Database Connection |
| Redis | 6379 | redis://localhost:6379 | Cache/Session |
| Main API | 8000 | http://localhost:8000 | Core RepoChat API |
| API Gateway | 8001 | http://localhost:8001 | External Agent API |
| Monitoring | 8002 | http://localhost:8002 | System Monitoring |

---

## 🧪 **4. Test Các Phase**

### **Phase 1: Dependencies Test**

```bash
# Test Google ADK installation
docker exec repochat-backend-multiagent python -c "
try:
    import google_adk
    print('✅ Google ADK imported successfully')
except ImportError as e:
    print(f'❌ Google ADK import error: {e}')
"

# Test A2A SDK
docker exec repochat-backend-multiagent python -c "
try:
    import a2a_sdk
    print('✅ A2A SDK imported successfully')
except ImportError as e:
    print(f'❌ A2A SDK import error: {e}')
"

# Test Circuit Breaker
docker exec repochat-backend-multiagent python -c "
try:
    import tenacity
    import circuit_breaker
    print('✅ Circuit breaker libraries available')
except ImportError as e:
    print(f'❌ Circuit breaker import error: {e}')
"

# Test LLM Providers
docker exec repochat-backend-multiagent python -c "
from teams.llm_services.models import LLMProviderType
print('Available LLM Providers:')
for provider in LLMProviderType:
    print(f'  ✅ {provider.name}: {provider.value}')
"

# Test Ollama Provider
docker exec repochat-backend-multiagent python -c "
try:
    from teams.llm_services.ollama_provider import is_ollama_available
    print(f'Ollama available: {is_ollama_available()}')
except ImportError as e:
    print(f'❌ Ollama provider error: {e}')
"
```

### **Phase 2: Migration Manager Test**

```bash
# Test Migration Manager
docker exec repochat-backend-multiagent python -c "
import sys
sys.path.append('/app/src')
import asyncio
from teams.shared.simple_phase3_test import test_phase3_components

async def test():
    result = await test_phase3_components()
    return result

result = asyncio.run(test())
print(f'Migration Test Result: {result[\"success\"]}')
"

# Test trực tiếp với script
docker exec repochat-backend-multiagent python /app/src/orchestrator/simple_migration_test.py
```

### **Phase 3: External Agent Integration Test**

```bash
# Test External Agent Registry
curl -X GET http://localhost:8001/agents \
  -H "Authorization: Bearer rca_public_key_123"

# Test Agent Registration
curl -X POST http://localhost:8001/agents/register \
  -H "Authorization: Bearer rca_enterprise_key_456" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-crewai-agent",
    "name": "Test CrewAI Agent",
    "agent_type": "crewai",
    "version": "1.0.0",
    "description": "Test agent for validation",
    "capabilities": [{
      "name": "test_execution",
      "description": "Execute test tasks",
      "input_schema": {"type": "object"},
      "output_schema": {"type": "object"},
      "tags": ["test"]
    }]
  }'

# Test Agent Execution
curl -X POST http://localhost:8001/agents/test-crewai-agent/execute \
  -H "Authorization: Bearer rca_public_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test task execution",
    "target": "sample_code.py"
  }'
```

### **End-to-End Integration Test**

```bash
# Chạy comprehensive test
docker exec repochat-backend-multiagent python /app/src/teams/shared/simple_phase3_test.py

# Test với real repository
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/octocat/Hello-World.git",
    "enable_multiagent": true,
    "migration_phase": "canary"
  }'
```

---

## 📊 **5. Kiểm tra Logs & Results**

### **Xem Application Logs**

```bash
# Main application logs
docker logs repochat-backend-multiagent -f

# Specific log files
docker exec repochat-backend-multiagent tail -f /app/logs/repochat.log

# Multi-agent specific logs
docker exec repochat-backend-multiagent tail -f /app/logs/multiagent.log

# Migration logs
docker exec repochat-backend-multiagent tail -f /app/logs/migration.log
```

### **Database Validation**

```bash
# Connect to Neo4j và check data
docker exec repochat-neo4j-multiagent cypher-shell -u neo4j -p password123 "
MATCH (n) RETURN labels(n), count(n) ORDER BY labels(n);
"

# Check migration status
docker exec repochat-neo4j-multiagent cypher-shell -u neo4j -p password123 "
MATCH (m:MigrationStatus) RETURN m;
"
```

### **API Monitoring**

```bash
# Check API Gateway metrics
curl http://localhost:8001/metrics \
  -H "Authorization: Bearer rca_public_key_123"

# Check system health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check Redis status
docker exec repochat-redis-multiagent redis-cli info replication
```

### **Performance Monitoring**

```bash
# Monitor resource usage
docker stats repochat-backend-multiagent

# Check container health
docker inspect repochat-backend-multiagent | grep -A 5 "Health"

# Monitor network traffic
docker exec repochat-backend-multiagent netstat -tuln
```

---

## ✅ **Kết quả Mong đợi**

### **Phase 1 Success Indicators**

```
✅ Google ADK imported successfully
✅ A2A SDK imported successfully  
✅ Circuit breaker libraries available
✅ Requirements.txt dependencies installed
```

### **Phase 2 Success Indicators**

```
🚀 Testing Simple Migration Manager...
📋 Test 1: Baseline Phase ✅ 100% success rate
📈 Test 2: Canary Phase ✅ Traffic splitting functional
🔧 Test 3: Circuit Breaker ✅ CLOSED (healthy)
🔄 Test 4: Phase Progression ✅ Complete migration
✅ Final Results: Migration completed, circuit breaker functional
```

### **Phase 3 Success Indicators**

```
🚀 Testing Phase 3: Advanced Features
📋 Test 1: External Agent Registry ✅ (2 agents registered)
📋 Test 2: Agent Task Execution ✅ (CrewAI + Custom agents working)
📋 Test 3: API Gateway ✅ (localhost:8001 initialized)
📋 Test 4: API Endpoints ✅ (3/3 endpoints functional)
📋 Test 5: Security Features ✅ (Authentication + authorization)

🎯 Overall Status: ✅ PASSED
🚀 Phase 3 Advanced Features: VALIDATED ✅
```

### **API Response Examples**

**Health Check Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-02T10:30:00Z",
  "services": {
    "neo4j": "connected",
    "redis": "connected",
    "multiagent": "enabled"
  }
}
```

**Agent List Response:**
```json
{
  "agents": [
    {
      "agent_id": "crewai-analyst",
      "name": "CrewAI Code Analyst", 
      "type": "crewai",
      "capabilities": ["code_analysis"]
    }
  ],
  "total_count": 1
}
```

---

## 🔧 **6. Troubleshooting**

### **Common Issues & Solutions**

#### **Docker Services Not Starting**

```bash
# Check Docker daemon
sudo systemctl status docker

# Restart Docker services
docker-compose -f docker-compose.multiagent.yml down
docker-compose -f docker-compose.multiagent.yml up --build -d

# Clean up and rebuild
docker system prune -f
docker-compose -f docker-compose.multiagent.yml build --no-cache
```

#### **Neo4j Connection Issues**

```bash
# Check Neo4j logs
docker logs repochat-neo4j-multiagent

# Reset Neo4j password
docker exec repochat-neo4j-multiagent cypher-shell -u neo4j -p neo4j "
ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'password123';
"

# Test connection
docker exec repochat-backend-multiagent python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'password123'))
print('Neo4j connection: OK')
driver.close()
"
```

#### **API Gateway Authentication Issues**

```bash
# Check API keys
docker exec repochat-backend-multiagent python -c "
import sys
sys.path.append('/app/src')
from teams.shared.api_gateway import SecurityManager
sm = SecurityManager()
print(f'API Keys available: {len(sm.api_keys)}')
for key in list(sm.api_keys.keys())[:2]:
    print(f'Key: {key[:10]}...')
"

# Test authentication manually
curl -v http://localhost:8001/health \
  -H "Authorization: Bearer rca_public_key_123"
```

#### **Migration Manager Issues**

```bash
# Check migration status
docker exec repochat-backend-multiagent python -c "
import sys
sys.path.append('/app/src')
from orchestrator.migration_manager import MigrationPhase
print('Migration phases available:', [p.value for p in MigrationPhase])
"

# Reset migration state
curl -X POST http://localhost:8000/admin/reset-migration \
  -H "Authorization: Bearer rca_enterprise_key_456"
```

#### **Memory/Performance Issues**

```bash
# Check resource usage
docker stats --no-stream

# Increase memory limits in docker-compose.yml
# Add under backend service:
# deploy:
#   resources:
#     limits:
#       memory: 4G
#     reservations:
#       memory: 2G
```

### **Log Analysis Commands**

```bash
# Filter ERROR logs
docker logs repochat-backend-multiagent 2>&1 | grep ERROR

# Filter Multi-Agent logs
docker logs repochat-backend-multiagent 2>&1 | grep "multi.*agent"

# Performance metrics
docker logs repochat-backend-multiagent 2>&1 | grep "duration\|performance\|time"

# Security events
docker logs repochat-backend-multiagent 2>&1 | grep "auth\|security\|unauthorized"
```

### **Emergency Commands**

```bash
# Stop all services immediately
docker-compose -f docker-compose.multiagent.yml down --remove-orphans

# Complete cleanup
docker-compose -f docker-compose.multiagent.yml down -v
docker system prune -af

# Backup important data
docker exec repochat-neo4j-multiagent neo4j-admin dump --database=neo4j --to=/data/backup.dump

# Restore from backup
docker exec repochat-neo4j-multiagent neo4j-admin load --from=/data/backup.dump --database=neo4j --force
```

---

## 🎯 **Test Checklist**

### **Pre-Test Checklist**
- [ ] Docker và Docker Compose installed
- [ ] .env file configured
- [ ] Ports 7474, 7687, 6379, 8000, 8001, 8002 available
- [ ] At least 8GB RAM available
- [ ] Internet connection for dependency downloads

### **Phase 1 Tests**
- [ ] Google ADK import successful
- [ ] A2A SDK import successful
- [ ] Circuit breaker libraries available
- [ ] All requirements.txt dependencies installed

### **Phase 2 Tests**
- [ ] Migration Manager initializes
- [ ] Traffic splitting works (baseline → canary → partial → majority → complete)
- [ ] Circuit breaker functions correctly
- [ ] Metrics collection operational
- [ ] Rollback capability tested

### **Phase 3 Tests**
- [ ] External agent registry functional
- [ ] CrewAI agent registration successful
- [ ] Custom agent registration successful
- [ ] Agent task execution working
- [ ] API Gateway authentication working
- [ ] Security validation passing

### **Integration Tests**
- [ ] End-to-end repository scanning with multi-agent
- [ ] API Gateway → Migration Manager → Agents workflow
- [ ] Error handling và recovery procedures
- [ ] Performance benchmarks within acceptable range

---

## 📝 **Notes**

- **Testing Duration**: Complete test suite takes ~15-20 minutes
- **Resource Requirements**: 8GB RAM, 4 CPU cores recommended
- **Network**: Docker internal networking required
- **Persistence**: Data persists in Docker volumes between restarts
- **Logs**: Available in ./logs/ directory và Docker logs
- **Cleanup**: Use cleanup commands to free resources after testing

---

**🎉 Successful completion of all tests indicates the RepoChat Multi-Agent System is production-ready!** 