# Docker Deployment Guide

Complete guide for deploying the Film Financing Navigator platform using Docker and Docker Compose.

## 🐳 Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- 4GB+ RAM recommended
- 10GB+ disk space

Verify installation:
```bash
docker --version
docker-compose --version
```

## 📦 Quick Start

### 1. Clone and Navigate
```bash
cd "Independent Animated Film Financing Model v1"
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**IMPORTANT:** Update these values in `.env`:
- `SECRET_KEY` - Generate a secure random key
- `POSTGRES_PASSWORD` - Use a strong password
- `BACKEND_CORS_ORIGINS` - Add your production domain
- `NEXT_PUBLIC_API_URL` - Update to your production API URL

### 3. Build and Start
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🏗️ Architecture

The deployment includes 4 services:

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Frontend (Next.js) - Port 3000                 │
│  ├─ Beautiful UI for all 3 engines              │
│  └─ Tax Incentives, Waterfall, Scenarios        │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│  Backend (FastAPI) - Port 8000                  │
│  ├─ Engine 1: Tax Incentive Calculator          │
│  ├─ Engine 2: Waterfall Executor                │
│  ├─ Engine 3: Scenario Optimizer                │
│  └─ REST API with auto-generated docs           │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│              │  │              │
│  PostgreSQL  │  │    Redis     │
│  Port 5432   │  │  Port 6379   │
│              │  │              │
└──────────────┘  └──────────────┘
```

## 🔧 Configuration

### Environment Variables

**Database:**
- `POSTGRES_USER` - Database username (default: filmfinance)
- `POSTGRES_PASSWORD` - Database password (⚠️ change in production!)
- `POSTGRES_DB` - Database name (default: filmfinance)
- `POSTGRES_PORT` - Database port (default: 5432)

**Backend API:**
- `BACKEND_PORT` - API port (default: 8000)
- `SECRET_KEY` - Encryption key (⚠️ must change!)
- `BACKEND_CORS_ORIGINS` - Allowed frontend origins
- `ENVIRONMENT` - Environment name (production/staging/development)
- `DEBUG` - Debug mode (false in production)
- `RATE_LIMIT_PER_MINUTE` - API rate limit (default: 60)

**Frontend:**
- `FRONTEND_PORT` - UI port (default: 3000)
- `NEXT_PUBLIC_API_URL` - Backend API URL

**Redis (Optional but recommended):**
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_URL` - Redis connection string

### Generate Secure Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

## 🚀 Deployment Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with rebuild
docker-compose up -d --build
```

### Stop Services
```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (⚠️ deletes data!)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Health checks
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000/
```

### Execute Commands
```bash
# Backend shell
docker-compose exec backend bash

# Run database migrations
docker-compose exec backend python -m alembic upgrade head

# Run tests
docker-compose exec backend pytest

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec db psql -U filmfinance -d filmfinance
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# View updated logs
docker-compose logs -f
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U filmfinance filmfinance > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U filmfinance -d filmfinance
```

### View Volumes
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect independent-animated-film-financing-model-v1_postgres_data
```

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

**Common issues:**
1. Port already in use → Change port in `.env`
2. Out of memory → Increase Docker memory limit
3. Database connection failed → Check `DATABASE_URL` in `.env`

### Reset Everything
```bash
# ⚠️ WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Issues
```bash
# Check database is running
docker-compose ps db

# Test database connection
docker-compose exec db psql -U filmfinance -d filmfinance -c "SELECT 1"

# Check database logs
docker-compose logs db
```

### Frontend Can't Reach Backend
```bash
# Check backend health
curl http://localhost:8000/health

# Check CORS settings in .env
# BACKEND_CORS_ORIGINS must include frontend URL

# Check network connectivity
docker-compose exec frontend ping backend
```

## 📊 Performance Tuning

### Production Optimizations

**1. Resource Limits:**
```yaml
# Add to docker-compose.yml under each service
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

**2. Enable Redis Caching:**
Already included! Redis is running on port 6379.

**3. Database Connection Pooling:**
Configure in backend `.env`:
```
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

**4. Frontend Build Optimization:**
Already using multi-stage build with standalone output.

## 🔒 Security Best Practices

### Before Production Deployment:

1. ✅ **Change default passwords**
   - Update `POSTGRES_PASSWORD`
   - Generate new `SECRET_KEY`

2. ✅ **Configure CORS properly**
   - Update `BACKEND_CORS_ORIGINS` with actual domain
   - Remove `localhost` origins

3. ✅ **Disable debug mode**
   - Set `DEBUG=false`

4. ✅ **Use HTTPS**
   - Deploy behind reverse proxy (nginx/Caddy)
   - Configure SSL certificates

5. ✅ **Network isolation**
   - Services already on isolated network
   - Only expose necessary ports

6. ✅ **Regular backups**
   - Automate database backups
   - Store backups securely off-server

7. ✅ **Update regularly**
   - Keep Docker images updated
   - Monitor security advisories

## 🌐 Production Deployment

### Recommended Stack:
```
Internet
   ↓
Nginx/Caddy (Reverse Proxy + SSL)
   ↓
Docker Compose Services
```

### Sample Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
```

## 📈 Monitoring

### Health Checks

All services include health checks:
```bash
# Check all services
docker-compose ps

# Manual health checks
curl http://localhost:8000/health  # Backend
curl http://localhost:3000/        # Frontend
docker-compose exec db pg_isready  # Database
docker-compose exec redis redis-cli ping  # Redis
```

### Logs
```bash
# Follow all logs
docker-compose logs -f

# Export logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

## 🎯 Next Steps

1. ✅ Configure environment variables
2. ✅ Start services with `docker-compose up -d`
3. ✅ Test all three engines (Incentives, Waterfall, Scenarios)
4. ✅ Set up SSL certificates
5. ✅ Configure domain DNS
6. ✅ Set up automated backups
7. ✅ Configure monitoring/alerts

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health checks: `docker-compose ps`
- Check this guide: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

---

**Version:** 1.0
**Last Updated:** 2025-10-31
**Platform:** Film Financing Navigator
