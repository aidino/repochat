# 🐳 RepoChat v1.0 - Docker Setup Hoàn Chỉnh

## 📋 Tổng Quan

RepoChat v1.0 sử dụng Docker Compose để triển khai hệ thống multi-agent với các services:

- **Frontend**: Vue.js 3 application (Port 3000/5173)
- **Backend**: Python FastAPI application (Port 8000) 
- **Neo4j**: Code Knowledge Graph database (Port 7474/7687)
- **Redis**: Caching và session storage (Port 6379)
- **Monitoring**: Prometheus + Grafana (Production)

## 🚀 Khởi Động Nhanh

### 1. Cài Đặt Dependencies

```bash
# Cài đặt Docker và Docker Compose
# macOS
brew install docker docker-compose

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Windows
# Download Docker Desktop từ https://docker.com
```

### 2. Setup Môi Trường

```bash
# Clone repository
git clone <your-repo-url>
cd repochat

# Copy và cấu hình environment
cp env.template .env

# Chỉnh sửa .env với API keys của bạn
nano .env
```

### 3. Khởi Động Development Environment

```bash
# Option 1: Sử dụng script tiện lợi
./start-docker.sh -d

# Option 2: Docker Compose trực tiếp
docker-compose up -d
```

### 4. Kiểm Tra Services

```bash
# Xem status tất cả services
docker-compose ps

# Xem logs
docker-compose logs -f
```

## 🔧 Scripts Quản Lý

### `start-docker.sh` - Script Khởi Động

```bash
# Development mode (default)
./start-docker.sh

# Detached mode (chạy nền)
./start-docker.sh -d

# Production mode
./start-docker.sh -p -d

# Chỉ khởi động một số services
./start-docker.sh -s "neo4j backend"

# Xem help
./start-docker.sh -h
```

### `stop-docker.sh` - Script Dừng

```bash
# Dừng tất cả services
./stop-docker.sh

# Dừng và cleanup containers
./stop-docker.sh -c

# Dừng và xóa toàn bộ data (CẢNH BÁO!)
./stop-docker.sh -v

# Dừng chỉ một số services
./stop-docker.sh -s "frontend"
```

## 🌐 Endpoints Và Interfaces

### Development Environment

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| Neo4j Browser | http://localhost:7474 | neo4j/repochat123 |
| Redis | localhost:6379 | - |

### Production Environment

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:80 | - |
| Backend API | http://localhost:8000 | - |
| Neo4j Browser | http://localhost:7474 | neo4j/repochat123 |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin/admin123 |

## ⚙️ Cấu Hình Environment

### Các Environment Variables Quan Trọng

```bash
# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=repochat123

# LLM Services (Optional)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_genai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Production Security
REDIS_PASSWORD=your_redis_password
GRAFANA_PASSWORD=your_grafana_password
```

## 🏗️ Docker Compose Files

### `docker-compose.yml` - Base Configuration

Chứa cấu hình cơ bản cho development environment:
- Service definitions
- Volume mounts cho hot reloading
- Development ports và environment variables
- Health checks và dependencies

### `docker-compose.prod.yml` - Production Overrides

Cấu hình cho production environment:
- Resource limits và reservations
- Security optimizations
- Monitoring services (Prometheus/Grafana)
- Production-ready health checks

## 📊 Monitoring Và Logs

### Xem Logs

```bash
# Tất cả services
docker-compose logs -f

# Service cụ thể
docker-compose logs -f backend
docker-compose logs -f neo4j

# Logs với timestamps
docker-compose logs -f -t
```

### Health Checks

```bash
# Kiểm tra health tất cả services
docker-compose ps

# Health check chi tiết
docker inspect repochat-backend | grep -A 10 Health
```

### Resource Monitoring

```bash
# Resource usage
docker stats

# Container processes
docker-compose top
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Kiểm tra ports đang sử dụng
lsof -i :3000
lsof -i :8000
lsof -i :7474

# Dừng services sử dụng ports
sudo kill -9 <PID>
```

#### 2. Permission Issues
```bash
# Fix permissions cho data directories
sudo chown -R $USER:$USER data/ logs/ temp/

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
```

#### 3. Memory Issues
```bash
# Tăng Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > 8GB+

# Clean up unused images/containers
docker system prune -a
```

#### 4. Neo4j Connection Issues
```bash
# Kiểm tra Neo4j logs
docker-compose logs neo4j

# Connect trực tiếp
docker exec -it repochat-neo4j cypher-shell -u neo4j -p repochat123
```

### Service-Specific Debugging

#### Backend Issues
```bash
# Enter backend container
docker exec -it repochat-backend bash

# Check Python environment
python -c "import sys; print(sys.path)"

# Test import
python -c "from src.orchestrator.orchestrator_agent import OrchestratorAgent"
```

#### Frontend Issues
```bash
# Enter frontend container
docker exec -it repochat-frontend sh

# Check Node environment
node --version
npm --version

# Rebuild node_modules
rm -rf node_modules && npm install
```

## 🚀 Production Deployment

### Production Checklist

1. **Security**
   - [ ] Change default passwords trong .env
   - [ ] Configure HTTPS certificates
   - [ ] Setup firewall rules
   - [ ] Enable authentication

2. **Performance**
   - [ ] Configure resource limits
   - [ ] Setup monitoring alerts
   - [ ] Optimize database settings
   - [ ] Enable caching

3. **Backup**
   - [ ] Schedule Neo4j backups
   - [ ] Backup application data
   - [ ] Document recovery procedures

### Production Deployment Commands

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use script
./start-docker.sh -p -d
```

### SSL/HTTPS Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/repochat.key \
  -out nginx/ssl/repochat.crt

# Production: Use Let's Encrypt or commercial certificates
```

## 📝 Maintenance

### Regular Maintenance Tasks

```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune

# Backup Neo4j data
docker exec repochat-neo4j neo4j-admin backup --backup-dir=/backups

# Update dependencies
docker-compose build --no-cache
```

### Data Backup Và Restore

```bash
# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh <backup-file>
```

## 🎯 Next Steps

1. **Cấu hình API Keys** trong file `.env`
2. **Test các endpoints** bằng Frontend interface
3. **Setup monitoring** với Prometheus/Grafana
4. **Configure backup strategy** cho production
5. **Review security settings** trước khi deploy

## 📚 Tài Liệu Tham Khảo

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Neo4j Docker Guide](https://neo4j.com/docs/operations-manual/current/docker/)
- [Vue.js Docker Deployment](https://vuejs.org/guide/extras/deployment.html)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

---

**Lưu ý**: File này được tạo tự động cho RepoChat v1.0 Docker setup. Cập nhật theo nhu cầu dự án của bạn. 