# Film Financing Navigator - Docker Management Makefile

.PHONY: help build up down logs restart clean test backup restore

# Default target
help:
	@echo "Film Financing Navigator - Docker Commands"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build      - Build all Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - Follow logs from all services"
	@echo "  make logs-backend  - Follow backend logs only"
	@echo "  make logs-frontend - Follow frontend logs only"
	@echo "  make ps         - Show service status"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-up    - Start production services"
	@echo "  make prod-down  - Stop production services"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-shell   - Open PostgreSQL shell"
	@echo "  make backup     - Backup database"
	@echo "  make restore    - Restore database from backup"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean      - Remove containers and networks"
	@echo "  make clean-all  - Remove containers, networks, and volumes (⚠️  deletes data)"
	@echo "  make test       - Run backend tests"
	@echo "  make rebuild    - Full rebuild (clean + build + up)"
	@echo ""

# ================================
# Development Commands
# ================================

build:
	@echo "🔨 Building Docker images..."
	docker-compose build

up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

down:
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped"

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted"

logs:
	@echo "📋 Following logs (Ctrl+C to exit)..."
	docker-compose logs -f

logs-backend:
	@echo "📋 Following backend logs (Ctrl+C to exit)..."
	docker-compose logs -f backend

logs-frontend:
	@echo "📋 Following frontend logs (Ctrl+C to exit)..."
	docker-compose logs -f frontend

ps:
	@echo "📊 Service status:"
	docker-compose ps

# ================================
# Production Commands
# ================================

prod-build:
	@echo "🔨 Building production Docker images..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "🚀 Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production services started!"

prod-down:
	@echo "🛑 Stopping production services..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production services stopped"

prod-logs:
	@echo "📋 Following production logs (Ctrl+C to exit)..."
	docker-compose -f docker-compose.prod.yml logs -f

# ================================
# Database Commands
# ================================

db-shell:
	@echo "🗄️  Opening PostgreSQL shell..."
	docker-compose exec db psql -U filmfinance -d filmfinance

backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U filmfinance filmfinance > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

restore:
	@echo "⚠️  This will restore the database from the most recent backup"
	@read -p "Continue? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		LATEST=$$(ls -t backups/*.sql | head -1); \
		echo "📥 Restoring from $$LATEST..."; \
		cat $$LATEST | docker-compose exec -T db psql -U filmfinance -d filmfinance; \
		echo "✅ Database restored"; \
	fi

# ================================
# Testing Commands
# ================================

test:
	@echo "🧪 Running backend tests..."
	docker-compose exec backend pytest -v

test-coverage:
	@echo "🧪 Running tests with coverage..."
	docker-compose exec backend pytest --cov=. --cov-report=html

# ================================
# Maintenance Commands
# ================================

clean:
	@echo "🧹 Cleaning up containers and networks..."
	docker-compose down
	@echo "✅ Cleanup complete"

clean-all:
	@echo "⚠️  This will delete all data including database and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✅ Full cleanup complete"; \
	fi

rebuild: clean build up
	@echo "✅ Rebuild complete"

update:
	@echo "🔄 Pulling latest code and rebuilding..."
	git pull
	docker-compose down
	docker-compose up -d --build
	@echo "✅ Update complete"

# ================================
# Development Utilities
# ================================

shell-backend:
	@echo "🐚 Opening backend shell..."
	docker-compose exec backend bash

shell-frontend:
	@echo "🐚 Opening frontend shell..."
	docker-compose exec frontend sh

install:
	@echo "📦 Initial setup..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and update the SECRET_KEY and passwords!"; \
	fi
	@echo "Building Docker images..."
	$(MAKE) build
	@echo "Starting services..."
	$(MAKE) up
	@echo ""
	@echo "✅ Installation complete!"
	@echo "📝 Next steps:"
	@echo "   1. Edit .env and update SECRET_KEY and passwords"
	@echo "   2. Run 'make restart' to apply changes"
	@echo "   3. Visit http://localhost:3000"
