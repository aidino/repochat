# 🐳 RepoChat Docker Quick Reference

## 🚀 Essential Commands

### Development
```bash
# Start development environment
./scripts/dev-docker.sh start

# Check status
./scripts/dev-docker.sh status

# View logs  
./scripts/dev-docker.sh logs

# Stop services
./scripts/dev-docker.sh stop
```

### Production
```bash
# Deploy production
./scripts/prod-docker.sh deploy

# Check production status
./scripts/prod-docker.sh status

# Stop production
./scripts/prod-docker.sh stop
```

## 🌐 Service URLs

### Development
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000  
- **Neo4j**: http://localhost:7474

### Production  
- **Frontend**: http://localhost
- **Backend**: http://localhost/api
- **Neo4j**: http://localhost:7474

## 🔧 Manual Commands

```bash
# Build specific service
docker-compose build frontend

# Start specific service
docker-compose up frontend -d

# View logs for specific service
docker-compose logs -f frontend

# Execute into container
docker-compose exec frontend /bin/sh

# Stop all services
docker-compose down

# Complete cleanup
docker-compose down -v --rmi all
```

## 🛠️ Troubleshooting

```bash
# Check ports
sudo netstat -tlnp | grep :3000

# Fix permissions  
chmod +x scripts/*.sh

# Clean rebuild
./scripts/dev-docker.sh clean
./scripts/dev-docker.sh build

# Docker system cleanup
docker system prune -a
```

## 📁 Important Files

- `docker-compose.yml` - Main configuration
- `frontend/Dockerfile` - Frontend container  
- `frontend/nginx.conf` - Production web server
- `scripts/dev-docker.sh` - Development automation
- `scripts/prod-docker.sh` - Production automation
- `DOCKER_SETUP_GUIDE.md` - Complete documentation

---

*For detailed documentation, see `DOCKER_SETUP_GUIDE.md`* 