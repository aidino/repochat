# 🐳 RepoChat Docker Setup Guide

Hướng dẫn chi tiết về việc setup và sử dụng Docker Compose cho RepoChat project.

## 📋 Yêu Cầu Hệ Thống

- Docker Engine 20.10+
- Docker Compose 1.29+
- RAM tối thiểu: 4GB (khuyến nghị: 8GB+)
- Disk trống: 5GB+

## 🚀 Quick Start

### Development Environment

```bash
# 1. Clone repository và setup
git clone <repo-url>
cd repochat

# 2. Copy environment file
cp env.template .env
# Chỉnh sửa .env file với API keys của bạn

# 3. Khởi chạy development environment
./scripts/dev-docker.sh start
```

### Production Deployment

```bash
# 1. Setup environment
cp env.template .env
# Cấu hình production values trong .env

# 2. Deploy production stack
./scripts/prod-docker.sh deploy
```

## 📁 Cấu Trúc Docker

### Services Overview

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| `frontend` | 3000 | Vue.js UI (dev) / Nginx (prod) | HTTP probe |
| `backend` | 8000 | FastAPI Python app | Python import test |
| `neo4j` | 7474, 7687 | Graph database | Cypher query |

### Docker Files

```
repochat/
├── docker-compose.yml          # Main compose configuration
├── frontend/
│   ├── Dockerfile             # Multi-stage build
│   ├── nginx.conf             # Production nginx config
│   ├── docker-entrypoint.sh   # Container startup script
│   └── .dockerignore          # Build exclusions
├── backend/
│   └── Dockerfile             # Python backend
└── scripts/
    ├── dev-docker.sh          # Development commands
    └── prod-docker.sh         # Production commands
```

## 🔧 Development Environment

### Khởi Chạy Development

```bash
# Khởi chạy tất cả services
./scripts/dev-docker.sh start

# Chỉ build images
./scripts/dev-docker.sh build

# Xem status
./scripts/dev-docker.sh status

# Xem logs
./scripts/dev-docker.sh logs

# Restart services
./scripts/dev-docker.sh restart

# Dừng services
./scripts/dev-docker.sh stop

# Cleanup hoàn toàn
./scripts/dev-docker.sh clean
```

### Development Features

- **Hot Reload**: Frontend tự động reload khi code thay đổi
- **Volume Mounts**: Source code được mount vào containers
- **Debug Ports**: Backend expose port 5678 cho VS Code debugging
- **Live Logs**: Theo dõi logs real-time

### URLs trong Development

- Frontend (Vue.js): http://localhost:3000
- Backend (FastAPI): http://localhost:8000
- Neo4j Browser: http://localhost:7474
- Neo4j Credentials: `neo4j/repochat123`

## 🏭 Production Environment

### Production Deployment

```bash
# Deploy production stack
./scripts/prod-docker.sh deploy

# Chỉ build production images
./scripts/prod-docker.sh build

# Xem production status
./scripts/prod-docker.sh status

# Xem production logs
./scripts/prod-docker.sh logs

# Restart production services
./scripts/prod-docker.sh restart

# Stop production
./scripts/prod-docker.sh stop

# Clean production environment
./scripts/prod-docker.sh clean
```

### Production Features

- **Optimized Builds**: Multi-stage builds với smaller images
- **Nginx Proxy**: Frontend served qua nginx với compression
- **API Proxy**: Frontend calls backend qua nginx proxy
- **Security Headers**: Standard security headers
- **Health Checks**: Proper health monitoring
- **Auto Restart**: Services tự động restart khi crash

### URLs trong Production

- Frontend: http://localhost
- Backend API (via proxy): http://localhost/api
- Backend Direct: http://localhost:8000
- Neo4j Browser: http://localhost:7474

## 🔧 Cấu Hình Chi Tiết

### Environment Variables

Tạo `.env` file từ `env.template`:

```bash
# API Keys
OPENAI_API_KEY=your_openai_key_here

# Environment
ENVIRONMENT=development  # hoặc production

# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=repochat123

# Logging
LOG_LEVEL=DEBUG  # development: DEBUG, production: INFO
```

### Networking

Services giao tiếp qua internal network `repochat-network`:

- Subnet: `172.20.0.0/16`
- Frontend → Backend: `http://backend:8000`
- Backend → Neo4j: `bolt://neo4j:7687`

### Volumes

**Development:**
- Source code mounted for hot reload
- Persistent volumes cho dependencies

**Production:**
- Chỉ mount cần thiết (logs, temp)
- Built assets được copy vào images

### Health Checks

Tất cả services có health checks:
- **Frontend**: HTTP GET request
- **Backend**: Python import test
- **Neo4j**: Cypher query test

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Kiểm tra port đang sử dụng
sudo netstat -tlnp | grep :3000

# Dừng service đang chạy hoặc thay đổi port
docker-compose down
```

#### 2. Build Errors

```bash
# Clean build không cache
./scripts/dev-docker.sh clean
./scripts/dev-docker.sh build

# Hoặc
docker system prune -a
```

#### 3. Permission Issues

```bash
# Fix script permissions
chmod +x scripts/*.sh frontend/*.sh

# Fix file ownership (nếu cần)
sudo chown -R $USER:$USER .
```

#### 4. Memory Issues

```bash
# Kiểm tra Docker memory usage
docker stats

# Tăng Docker memory limit trong Docker Desktop
# Settings → Resources → Memory
```

#### 5. Frontend Not Loading

```bash
# Kiểm tra frontend logs
docker-compose logs frontend

# Rebuild frontend container
docker-compose build frontend --no-cache
docker-compose up frontend
```

#### 6. Backend Connection Issues

```bash
# Kiểm tra backend health
curl http://localhost:8000/health

# Kiểm tra Neo4j connection
docker-compose logs backend | grep -i neo4j
```

### Debug Commands

```bash
# Exec vào container
docker-compose exec frontend /bin/sh
docker-compose exec backend /bin/bash

# Xem container logs
docker-compose logs -f [service_name]

# Kiểm tra network
docker network ls
docker network inspect repochat_repochat-network

# Kiểm tra volumes
docker volume ls
docker volume inspect repochat_frontend_node_modules
```

## 📊 Monitoring & Logs

### Log Management

```bash
# Theo dõi tất cả logs
docker-compose logs -f

# Logs cho service cụ thể
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f neo4j

# Logs với timestamp
docker-compose logs -f -t

# Chỉ logs gần đây
docker-compose logs --tail=50 -f
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Container processes
docker-compose top

# System info
docker system df
docker system info
```

## 🔄 Updates & Maintenance

### Updating Services

```bash
# Update một service specific
docker-compose build frontend --no-cache
docker-compose up -d frontend

# Update tất cả
./scripts/dev-docker.sh clean
./scripts/dev-docker.sh build
./scripts/dev-docker.sh start
```

### Backup & Restore

```bash
# Backup Neo4j data
docker-compose exec neo4j neo4j-admin dump --to=/tmp/backup.dump
docker cp $(docker-compose ps -q neo4j):/tmp/backup.dump ./backup.dump

# Restore Neo4j data
docker cp ./backup.dump $(docker-compose ps -q neo4j):/tmp/backup.dump
docker-compose exec neo4j neo4j-admin load --from=/tmp/backup.dump
```

## 🎯 Best Practices

### Development

1. **Use Hot Reload**: Luôn dùng development mode cho faster iteration
2. **Check Logs**: Theo dõi logs để debug issues nhanh chóng
3. **Resource Management**: Monitor memory/CPU usage
4. **Clean Builds**: Thỉnh thoảng clean build để tránh cache issues

### Production

1. **Environment Separation**: Luôn dùng separate .env cho production
2. **Security**: Đảm bảo API keys được bảo mật
3. **Monitoring**: Setup proper monitoring và alerting
4. **Backups**: Regular backup của Neo4j data
5. **SSL/TLS**: Sử dụng HTTPS trong production thực tế

### Performance

1. **Image Size**: Sử dụng multi-stage builds để minimize image size
2. **Caching**: Leverage Docker layer caching
3. **Resource Limits**: Set proper resource limits cho containers
4. **Health Checks**: Implement comprehensive health checks

## 📞 Support

Nếu gặp vấn đề, check theo thứ tự:

1. **Logs**: `docker-compose logs -f`
2. **Status**: `./scripts/dev-docker.sh status`
3. **Rebuild**: `./scripts/dev-docker.sh clean && ./scripts/dev-docker.sh start`
4. **Documentation**: Kiểm tra lại guide này
5. **Issues**: Tạo GitHub issue nếu vẫn không resolve được

---

*Happy Dockerizing! 🐳* 