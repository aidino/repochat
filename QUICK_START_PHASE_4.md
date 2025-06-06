# ⚡ RepoChat Phase 4 - Quick Start Guide

**Setup nhanh trong 5 phút để test các tính năng Phase 4**

## 🚀 Bước 1: Setup môi trường

```bash
# Clone và setup
git clone <repository_url>
cd repochat

# Copy environment file  
cp env.example .env

# Thêm OpenAI API key vào .env
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

## 🔧 Bước 2: Start services

```bash
# Start với Docker Compose
docker-compose up -d

# Wait for services to be ready (~30s)
docker-compose logs -f backend | grep "Orchestrator Agent initialization completed"
```

## ✅ Bước 3: Verify setup

```bash
# Test 1: Check system status
docker-compose exec backend python repochat_cli.py status

# Test 2: Check help
docker-compose exec backend python repochat_cli.py --help
```

## 🧪 Bước 4: Test Phase 4 features

### Test CLI Scan Project (Task 4.1)
```bash
docker-compose exec backend python repochat_cli.py scan-project https://github.com/spring-projects/spring-petclinic.git -v
```

### Test CLI Review PR (Task 4.2)  
```bash
docker-compose exec backend python repochat_cli.py review-pr https://github.com/spring-projects/spring-petclinic.git 123 -v
```

### Test Finding Aggregator (Task 4.4)
```bash
docker-compose exec backend python -m pytest tests/test_task_4_4_finding_aggregator.py -v
```

### Test Phase 3 Foundation
```bash
docker-compose exec backend python tests/phase_3_specific/phase_3_completion_test.py
```

## 📊 Expected Results

### ✅ Successful Output Examples

**System Status:**
```
🟢 RepoChat System Status
========================
✅ Orchestrator Agent: Initialized
✅ Data Acquisition: Ready
✅ CKG Operations: Ready
```

**Scan Project:**
```
🚀 Bắt đầu quét dự án...
✅ Quét dự án hoàn thành thành công!
⏱️  Thời gian thực hiện: 5.23s
```

**Review PR:**
```
🔍 Bắt đầu review Pull Request #123...
✅ Review Pull Request hoàn thành thành công!
⏱️  Thời gian thực hiện: 4.87s
```

## 🔍 Quick Troubleshooting

### Issue: OpenAI API Error
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-...

# Restart containers
docker-compose restart backend
```

### Issue: Neo4j Connection Failed
```bash
# Check Neo4j status
docker-compose ps neo4j
# Should show: Up (healthy)

# Manual connection test
docker-compose exec neo4j cypher-shell -u neo4j -p repochat123 'RETURN 1'
```

### Issue: Module Import Error
```bash
# Check Python path
docker-compose exec backend echo $PYTHONPATH
# Should show: /app/src

# Run with explicit path
docker-compose exec backend bash -c "cd /app && PYTHONPATH=/app/src python repochat_cli.py --help"
```

## 🎯 Phase 4 Status Summary

| Feature | Status | Testing |
|---------|--------|---------|
| CLI Interface | ✅ Ready | Available |
| Scan Project | ✅ Ready | Available |
| Review PR | ✅ Ready | Available |
| Finding Aggregator | ✅ Ready | Available |
| Report Generation | 🚧 WIP | Not Ready |
| Q&A System | 🚧 WIP | Not Ready |

## 📝 Useful Commands

```bash
# View real-time logs
docker-compose logs -f backend

# Monitor resource usage  
docker stats

# Access Neo4j browser
# URL: http://localhost:7474
# Login: neo4j / repochat123

# Quick cleanup
docker-compose down && docker-compose up -d
```

## 🎉 Success Criteria

- ✅ All commands run without errors
- ✅ Response times < 10s for small projects
- ✅ Neo4j accessible at localhost:7474
- ✅ Phase 3 completion test = 100% pass rate

**🚀 Ready to continue Phase 4 development!** 