# Film Financing Navigator - API

**Status:** Phase 4A - Foundation Complete
**Version:** 1.0.0
**Framework:** FastAPI 0.104+

## Overview

This is the REST API for the Film Financing Navigator, providing programmatic access to all three calculation engines:

- **Engine 1:** Tax Incentive Calculator
- **Engine 2:** Waterfall Execution Engine
- **Engine 3:** Scenario Generator & Optimizer

## Architecture

### Project Structure

```
backend/api/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/
│   │       ├── endpoints/      # Individual endpoint modules
│   │       │   ├── auth.py    # Authentication endpoints
│   │       │   ├── projects.py # Project management
│   │       │   ├── scenarios.py # Scenario generation
│   │       │   ├── incentives.py # Engine 1 endpoints
│   │       │   ├── waterfall.py  # Engine 2 endpoints
│   │       │   └── policies.py   # Policy management
│   │       └── api.py          # Main v1 router
│   ├── core/                   # Core utilities
│   │   ├── config.py          # Settings management ✅
│   │   ├── security.py        # Auth & security ✅
│   │   └── deps.py            # FastAPI dependencies
│   ├── db/                     # Database
│   │   ├── base.py            # Base models ✅
│   │   └── session.py         # Database session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User model ✅
│   │   ├── project.py         # Project model
│   │   ├── scenario.py        # Scenario model
│   │   ├── waterfall.py       # Waterfall structure model
│   │   └── job.py             # Background job model
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py            # User schemas ✅
│   │   ├── project.py         # Project schemas
│   │   ├── scenario.py        # Scenario schemas
│   │   └── common.py          # Shared schemas
│   ├── services/               # Business logic
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── project_service.py # Project management
│   │   └── engine_service.py  # Engine integration
│   ├── tasks/                  # Celery background tasks
│   │   ├── __init__.py
│   │   ├── monte_carlo.py     # Monte Carlo simulations
│   │   └── evaluation.py      # Scenario evaluation
│   └── main.py                # FastAPI app entry ✅
├── alembic/                    # Database migrations
├── tests/                      # API tests
├── requirements.txt            # Python dependencies ✅
├── .env.example               # Environment template ✅
├── Dockerfile                  # Container definition
└── README.md                   # This file

✅ = Completed in Phase 4A
```

### Technology Stack

- **FastAPI 0.104+** - Async web framework
- **SQLAlchemy 2.0+** - Async ORM
- **PostgreSQL 15+** - Production database
- **Redis** - Caching and task queue
- **Celery** - Background job processing
- **Pydantic v2** - Data validation
- **python-jose** - JWT tokens
- **passlib** - Password hashing

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Create virtual environment:**
```bash
cd backend/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Set up database:**
```bash
# Create database
createdb filmfinance_db

# Run migrations
alembic upgrade head
```

5. **Start Redis:**
```bash
redis-server
```

6. **Run application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Start Celery worker (separate terminal):**
```bash
celery -A app.tasks worker --loglevel=info
```

### Access API Documentation

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Implemented (Phase 4A)

- `GET /` - Service information
- `GET /health` - Health check

### To Implement (Phase 4B)

#### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /refresh` - Token refresh
- `GET /me` - Current user profile
- `PUT /me` - Update profile
- `POST /change-password` - Change password

#### Projects (`/api/v1/projects`)
- `GET /projects` - List user's projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

#### Policies (`/api/v1/policies`)
- `GET /policies` - List all tax policies
- `GET /policies/{policy_id}` - Get policy details
- `GET /policies/search` - Search policies
- `POST /policies/custom` - Upload custom policy

#### Engine 1: Incentives (`/api/v1/incentives`)
- `POST /incentives/calculate` - Calculate incentives
- `POST /incentives/cash-flow` - Generate cash flow projection
- `POST /incentives/compare-monetization` - Compare strategies

#### Engine 2: Waterfall (`/api/v1/waterfall`)
- `POST /waterfall/execute` - Execute waterfall (async)
- `GET /waterfall/results/{job_id}` - Get waterfall results
- `POST /waterfall/monte-carlo` - Run Monte Carlo (async)
- `POST /waterfall/sensitivity` - Sensitivity analysis

#### Engine 3: Scenarios (`/api/v1/scenarios`)
- `POST /scenarios/generate` - Generate scenarios
- `POST /scenarios/optimize` - Optimize capital stack
- `POST /scenarios/evaluate` - Evaluate scenarios (async)
- `GET /scenarios/evaluation/{job_id}` - Get evaluation results
- `POST /scenarios/compare` - Compare scenarios
- `POST /scenarios/tradeoffs` - Trade-off analysis

#### WebSocket (`/ws`)
- `WS /ws/progress/{job_id}` - Real-time job progress

## Implementing New Endpoints

### Step-by-Step Guide

#### 1. Create Pydantic Schemas

Create request/response schemas in `app/schemas/`:

```python
# app/schemas/project.py
from pydantic import BaseModel
from decimal import Decimal

class ProjectCreate(BaseModel):
    name: str
    budget: Decimal
    description: str | None = None

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    budget: Decimal
    user_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
```

#### 2. Create Database Model

Create SQLAlchemy model in `app/models/`:

```python
# app/models/project.py
from sqlalchemy import String, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin

class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255))
    budget: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    description: Mapped[str | None] = mapped_column(Text)

    # Relationships
    user = relationship("User", back_populates="projects")
```

#### 3. Create Service Layer

Business logic in `app/services/`:

```python
# app/services/project_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.schemas.project import ProjectCreate

async def create_project(
    db: AsyncSession,
    user_id: UUID,
    project_data: ProjectCreate
) -> Project:
    """Create new project."""
    project = Project(
        user_id=user_id,
        **project_data.model_dump()
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project
```

#### 4. Create API Endpoint

Create endpoint in `app/api/v1/endpoints/`:

```python
# app/api/v1/endpoints/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services import project_service

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new project."""
    project = await project_service.create_project(
        db,
        current_user.id,
        project_data
    )
    return project
```

#### 5. Register Router

Add to `app/api/v1/api.py`:

```python
from fastapi import APIRouter
from app.api.v1.endpoints import projects

api_router = APIRouter()
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
```

#### 6. Create Migration

```bash
alembic revision --autogenerate -m "Add projects table"
alembic upgrade head
```

#### 7. Write Tests

```python
# tests/api/test_projects.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "budget": 30000000,
            "description": "CGI Feature"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"
```

## Engine Integration

### Calling Engine 1 (Incentive Calculator)

```python
# In endpoint or service
from backend.engines.incentive_calculator import IncentiveCalculator, JurisdictionSpend

calculator = IncentiveCalculator(policy_registry)

result = calculator.calculate_multi_jurisdiction(
    total_budget=Decimal("30000000"),
    jurisdiction_spends=[
        JurisdictionSpend(
            jurisdiction="Quebec",
            policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
            qualified_spend=Decimal("16500000"),
            labor_spend=Decimal("12000000")
        )
    ]
)

return result
```

### Calling Engine 2 (Waterfall Executor)

```python
from backend.engines.waterfall_executor import (
    WaterfallExecutor,
    RevenueProjector,
    StakeholderAnalyzer
)

# Project revenue
projector = RevenueProjector()
projection = projector.project(
    total_ultimate_revenue=Decimal("75000000"),
    release_strategy="wide_theatrical"
)

# Execute waterfall
executor = WaterfallExecutor(waterfall_structure)
result = executor.execute_over_time(projection)

# Analyze returns
analyzer = StakeholderAnalyzer(capital_stack)
analysis = analyzer.analyze(result)

return analysis
```

### Calling Engine 3 (Scenario Optimizer)

```python
from backend.engines.scenario_optimizer import (
    ScenarioGenerator,
    CapitalStackOptimizer,
    ScenarioEvaluator
)

# Generate scenarios
generator = ScenarioGenerator()
scenarios = generator.generate_multiple_scenarios(Decimal("30000000"))

# Evaluate
evaluator = ScenarioEvaluator()
evaluations = [
    evaluator.evaluate(stack, waterfall, run_monte_carlo=True)
    for stack in scenarios
]

return evaluations
```

## Background Jobs (Celery)

### Creating a Background Task

```python
# app/tasks/monte_carlo.py
from celery import Task
from app.tasks import celery_app

@celery_app.task(bind=True)
def run_monte_carlo(
    self: Task,
    scenario_id: str,
    num_simulations: int = 1000
):
    """Run Monte Carlo simulation in background."""

    # Update progress
    for i in range(num_simulations):
        self.update_state(
            state='PROGRESS',
            meta={'current': i, 'total': num_simulations}
        )

        # Run simulation step
        # ...

    return {'result': 'completed'}
```

### Calling from Endpoint

```python
@router.post("/monte-carlo")
async def run_monte_carlo_endpoint(
    scenario_id: UUID,
    num_simulations: int = 1000
):
    """Queue Monte Carlo simulation."""
    from app.tasks.monte_carlo import run_monte_carlo

    task = run_monte_carlo.delay(str(scenario_id), num_simulations)

    return {
        "job_id": task.id,
        "status": "queued"
    }
```

## WebSocket for Real-Time Progress

```python
# app/api/v1/endpoints/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from app.tasks import celery_app

@router.websocket("/ws/progress/{job_id}")
async def progress_websocket(websocket: WebSocket, job_id: str):
    """Stream job progress via WebSocket."""
    await websocket.accept()

    try:
        while True:
            task = celery_app.AsyncResult(job_id)

            if task.state == 'PROGRESS':
                await websocket.send_json({
                    "status": "running",
                    "progress": task.info.get('current', 0),
                    "total": task.info.get('total', 100)
                })
            elif task.state == 'SUCCESS':
                await websocket.send_json({
                    "status": "completed",
                    "result": task.result
                })
                break
            elif task.state == 'FAILURE':
                await websocket.send_json({
                    "status": "failed",
                    "error": str(task.info)
                })
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
```

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/api/test_auth.py

# Specific test
pytest tests/api/test_auth.py::test_register_user
```

### Test Structure

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client: AsyncClient):
    # Register and login
    # Return {"Authorization": f"Bearer {token}"}
    pass
```

## Deployment

### Docker

```bash
# Build
docker build -t filmfinance-api .

# Run
docker run -p 8000:8000 --env-file .env filmfinance-api
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Next Steps (Phase 4B)

1. **Complete Database Models** - Implement Project, Scenario, WaterfallStructure, Job models
2. **Implement All API Endpoints** - Auth, Projects, Scenarios, Engines 1-3
3. **Add Background Job Processing** - Celery tasks for Monte Carlo, evaluation
4. **Implement WebSocket** - Real-time progress updates
5. **Add Comprehensive Tests** - Unit, integration, end-to-end
6. **Build Frontend** - Next.js dashboard with D3.js visualizations

## Contributing

See [PHASE_4_IMPLEMENTATION_PLAN.md](../../docs/PHASE_4_IMPLEMENTATION_PLAN.md) for complete architecture and detailed implementation guide.

## License

Proprietary - All Rights Reserved
