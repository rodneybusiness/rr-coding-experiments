#!/bin/bash
# Docker Health Check Script for Film Financing Navigator

set -e

echo "🏥 Film Financing Navigator - Health Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

# Function to check service
check_service() {
    local service=$1
    local url=$2
    local expected=$3

    echo -n "Checking $service... "

    if curl -f -s -o /dev/null "$url"; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}✗ UNHEALTHY${NC}"
        OVERALL_STATUS=1
        return 1
    fi
}

# Function to check Docker service
check_docker_service() {
    local service=$1

    echo -n "Checking Docker service '$service'... "

    if docker-compose ps | grep -q "$service.*running"; then
        echo -e "${GREEN}✓ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        OVERALL_STATUS=1
        return 1
    fi
}

echo "1. Checking Docker Services"
echo "----------------------------"
check_docker_service "backend"
check_docker_service "frontend"
check_docker_service "db"
check_docker_service "redis"
echo ""

echo "2. Checking HTTP Endpoints"
echo "----------------------------"
check_service "Backend API Health" "http://localhost:8000/health" "200"
check_service "Backend API Docs" "http://localhost:8000/docs" "200"
check_service "Frontend UI" "http://localhost:3000/" "200"
echo ""

echo "3. Checking Database Connection"
echo "--------------------------------"
if docker-compose exec -T db psql -U filmfinance -d filmfinance -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "Database connection... ${GREEN}✓ CONNECTED${NC}"
else
    echo -e "Database connection... ${RED}✗ FAILED${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "4. Checking Redis Connection"
echo "-----------------------------"
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "Redis connection... ${GREEN}✓ CONNECTED${NC}"
else
    echo -e "Redis connection... ${RED}✗ FAILED${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "5. Service Resource Usage"
echo "-------------------------"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    $(docker-compose ps -q) 2>/dev/null || echo "Could not retrieve stats"
echo ""

echo "=========================================="
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All health checks passed!${NC}"
    echo ""
    echo "Application URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}✗ Some health checks failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker-compose logs -f"
    echo "  2. Check status: docker-compose ps"
    echo "  3. Restart services: docker-compose restart"
    exit 1
fi
