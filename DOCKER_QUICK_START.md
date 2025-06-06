# 🐳 RepoChat v1.0 - Docker Quick Start

## ⚡ One-Minute Setup

```bash
# 1. Clone và setup
git clone <repo-url> && cd repochat
cp env.template .env

# 2. Start all services
./start-docker.sh -d

# 3. Verify everything works
./test-docker.sh

# 🎉 Done! Open http://localhost:3000
```

## 🔧 Essential Commands

### Start/Stop
```bash
./start-docker.sh -d       # Start detached
./stop-docker.sh           # Stop services
./stop-docker.sh -c        # Stop + cleanup
```

### Development
```bash
docker-compose logs -f     # View logs
docker-compose ps          # Service status
docker-compose restart     # Restart all
```

### Troubleshooting
```bash
./test-docker.sh           # Run health checks
docker-compose down && docker-compose up -d  # Full restart
docker system prune        # Clean unused resources
```

## 🌐 Service URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Neo4j**: http://localhost:7474 (neo4j/repochat123)

## 📝 Environment Setup

Edit `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## 🆘 Help

- **Full Documentation**: `DOCKER_SETUP_COMPLETE.md`
- **Script Help**: `./start-docker.sh -h`
- **Issues**: Check logs with `docker-compose logs -f` 