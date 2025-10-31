# Phase 4: API + Frontend Implementation Plan

**Project:** Independent Animated Film Financing Model v1
**Phase:** 4 - User-Facing Interface
**Date:** October 31, 2025
**Status:** In Development

---

## Executive Summary

Phase 4 creates a production-ready web application that exposes all three calculation engines through a modern REST API and interactive dashboard. This enables producers, investors, and financiers to leverage the sophisticated financing optimization capabilities through an intuitive interface.

**Key Deliverables:**
1. FastAPI REST API with comprehensive endpoints
2. Next.js dashboard with TypeScript
3. D3.js data visualizations
4. User authentication and project management
5. Real-time progress updates for long-running operations
6. Docker containerization for deployment
7. Comprehensive documentation

---

## Architecture Overview

### Technology Stack

**Backend:**
- **FastAPI** 0.104+ - Modern async Python web framework
- **PostgreSQL** 15+ - Production database
- **SQLAlchemy** 2.0+ - ORM with async support
- **Alembic** - Database migrations
- **Pydantic** v2 - Data validation (already in use)
- **python-jose** - JWT token handling
- **passlib** - Password hashing (bcrypt)
- **Celery** + **Redis** - Background task queue
- **pytest** + **httpx** - API testing

**Frontend:**
- **Next.js** 14+ (App Router) - React framework with SSR
- **TypeScript** 5+ - Type safety
- **Tailwind CSS** 3+ - Utility-first styling
- **shadcn/ui** - Component library
- **React Query** (TanStack Query) - Server state management
- **Zustand** - Client state management
- **D3.js** v7 - Custom visualizations
- **Recharts** - Standard charts
- **Zod** - Schema validation
- **Jest** + **React Testing Library** - Frontend testing

**Infrastructure:**
- **Docker** + **Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **Redis** - Caching and task queue
- **GitHub Actions** - CI/CD (future)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Next.js Frontend                          │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │  Auth Pages  │  Dashboard   │  Scenario    │            │
│  │              │              │  Builder     │            │
│  └──────────────┴──────────────┴──────────────┘            │
│  ┌──────────────────────────────────────────────┐          │
│  │        D3.js Visualizations                   │          │
│  │  - Sankey Diagrams (Waterfall)               │          │
│  │  - Tornado Charts (Sensitivity)              │          │
│  │  - Pareto Frontiers (Trade-offs)             │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API + WebSocket
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Routes                               │  │
│  │  /api/v1/auth         - Authentication               │  │
│  │  /api/v1/projects     - Project CRUD                 │  │
│  │  /api/v1/policies     - Tax policies                 │  │
│  │  /api/v1/incentives   - Engine 1                     │  │
│  │  /api/v1/waterfall    - Engine 2                     │  │
│  │  /api/v1/scenarios    - Engine 3                     │  │
│  │  /ws/progress         - WebSocket for real-time      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Business Logic (Engines)                    │  │
│  │  - Engine 1: Incentive Calculator                    │  │
│  │  - Engine 2: Waterfall Executor                      │  │
│  │  - Engine 3: Scenario Optimizer                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────┬────────────────────┘
                         │               │
                         │               │
         ┌───────────────▼──┐      ┌────▼──────────┐
         │   PostgreSQL DB  │      │ Redis Queue   │
         │   - Users        │      │ - Celery      │
         │   - Projects     │      │ - Cache       │
         │   - Scenarios    │      │ - Sessions    │
         └──────────────────┘      └───────────────┘
```

---

## Database Schema

### Core Entities

**1. users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    organization VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',  -- user, admin
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**2. projects**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    budget DECIMAL(15,2) NOT NULL,

    -- ProjectProfile data (JSONB for flexibility)
    profile JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

**3. scenarios**
```sql
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,

    -- Scenario type (template, optimized, custom)
    scenario_type VARCHAR(50) NOT NULL,
    template_name VARCHAR(100),

    -- Capital stack (JSONB)
    capital_stack JSONB NOT NULL,

    -- Evaluation results (JSONB)
    evaluation_results JSONB,

    -- Ranking
    rank INTEGER,
    score DECIMAL(5,2),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_project_id (project_id),
    INDEX idx_scenario_type (scenario_type)
);
```

**4. waterfall_structures**
```sql
CREATE TABLE waterfall_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,

    -- Waterfall definition (JSONB)
    structure JSONB NOT NULL,

    -- Metadata
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_project_id (project_id)
);
```

**5. jobs**
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Job details
    job_type VARCHAR(50) NOT NULL,  -- monte_carlo, optimization, evaluation
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed

    -- Progress tracking
    progress INTEGER DEFAULT 0,  -- 0-100
    total_steps INTEGER,
    current_step INTEGER DEFAULT 0,

    -- Results
    result JSONB,
    error TEXT,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**6. custom_policies** (optional - for user-uploaded policies)
```sql
CREATE TABLE custom_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Policy data (JSONB following IncentivePolicy schema)
    policy JSONB NOT NULL,

    -- Metadata
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_id (user_id)
);
```

---

## API Design

### Authentication Endpoints

**POST /api/v1/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "full_name": "John Producer",
  "organization": "Acme Animation Studios"
}

Response: 201
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Producer",
  "created_at": "2025-10-31T..."
}
```

**POST /api/v1/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "securePassword123!"
}

Response: 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**POST /api/v1/auth/refresh**
```json
Request:
{
  "refresh_token": "eyJ..."
}

Response: 200
{
  "access_token": "eyJ...",
  "expires_in": 3600
}
```

---

### Project Endpoints

**POST /api/v1/projects**
```json
Request:
{
  "name": "Dragon's Quest",
  "description": "CGI family feature",
  "budget": 30000000,
  "profile": {
    "project_type": "feature",
    "animation_technique": "cgi",
    "target_audience": "family",
    "runtime_minutes": 90,
    "production_jurisdictions": [
      {
        "jurisdiction": "Quebec",
        "percentage_of_budget": 55.0,
        "spend_amount": 16500000
      }
    ]
  }
}

Response: 201
{
  "id": "uuid",
  "name": "Dragon's Quest",
  ...
}
```

**GET /api/v1/projects**
```json
Response: 200
{
  "projects": [
    {
      "id": "uuid",
      "name": "Dragon's Quest",
      "budget": 30000000,
      "created_at": "2025-10-31T...",
      "scenarios_count": 7
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

**GET /api/v1/projects/{project_id}**
```json
Response: 200
{
  "id": "uuid",
  "name": "Dragon's Quest",
  "budget": 30000000,
  "profile": {...},
  "scenarios": [...],
  "created_at": "2025-10-31T..."
}
```

---

### Engine 1: Incentive Calculator Endpoints

**POST /api/v1/incentives/calculate**
```json
Request:
{
  "project_id": "uuid",
  "jurisdiction_spends": [
    {
      "jurisdiction": "Quebec",
      "policy_ids": ["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
      "qualified_spend": 16500000,
      "labor_spend": 12000000
    }
  ],
  "monetization_preferences": {
    "preferred_method": "direct_cash",
    "discount_rate": 12.0
  }
}

Response: 200
{
  "total_gross_credit": 11895000,
  "total_net_benefit": 9516000,
  "effective_rate": 39.65,
  "jurisdictions": [
    {
      "jurisdiction": "Quebec",
      "policies_applied": ["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
      "gross_credit": 6795000,
      "net_benefit": 5436000,
      "stacking_applied": true
    }
  ],
  "cash_flow_projection": {...}
}
```

**GET /api/v1/policies**
```json
Response: 200
{
  "policies": [
    {
      "policy_id": "CA-QC-PSTC-2025",
      "jurisdiction": "Quebec",
      "rate": 36.0,
      "type": "refundable",
      ...
    }
  ],
  "total": 15
}
```

**GET /api/v1/policies/{policy_id}**
```json
Response: 200
{
  "policy_id": "CA-QC-PSTC-2025",
  "jurisdiction": "Quebec",
  "rate": 36.0,
  "incentive_type": "refundable_tax_credit",
  "qpe_definition": {...},
  "cultural_test": null,
  ...
}
```

---

### Engine 2: Waterfall Execution Endpoints

**POST /api/v1/waterfall/execute**
```json
Request:
{
  "project_id": "uuid",
  "capital_stack_id": "uuid",  // From scenario
  "waterfall_structure_id": "uuid",
  "revenue_projection": {
    "total_ultimate_revenue": 75000000,
    "release_strategy": "wide_theatrical"
  },
  "run_monte_carlo": true,
  "num_simulations": 1000
}

Response: 202 Accepted
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Waterfall execution queued"
}
```

**GET /api/v1/waterfall/results/{job_id}**
```json
Response: 200
{
  "job_id": "uuid",
  "status": "completed",
  "result": {
    "stakeholder_analysis": {
      "stakeholders": [
        {
          "stakeholder_id": "equity_investors",
          "irr": 0.182,
          "npv": 2100000,
          "cash_on_cash": 1.38,
          "payback_years": 4.5
        }
      ]
    },
    "monte_carlo": {
      "equity_irr_p10": 0.085,
      "equity_irr_p50": 0.182,
      "equity_irr_p90": 0.321,
      "probability_of_recoupment": 0.873
    },
    "time_series_result": {...}
  }
}
```

---

### Engine 3: Scenario Optimizer Endpoints

**POST /api/v1/scenarios/generate**
```json
Request:
{
  "project_id": "uuid",
  "templates": ["debt_heavy", "equity_heavy", "balanced", "presale_focused", "incentive_maximized"],
  "include_optimized": true,
  "optimization_objectives": [
    {
      "objective": "MAXIMIZE_TAX_INCENTIVES",
      "weight": 0.6
    },
    {
      "objective": "MINIMIZE_COST_OF_CAPITAL",
      "weight": 0.4
    }
  ]
}

Response: 201
{
  "scenarios": [
    {
      "id": "uuid",
      "name": "debt_heavy_scenario",
      "scenario_type": "template",
      "capital_stack": {...}
    },
    ...
  ],
  "total": 7
}
```

**POST /api/v1/scenarios/evaluate**
```json
Request:
{
  "project_id": "uuid",
  "scenario_ids": ["uuid1", "uuid2", "uuid3"],
  "waterfall_structure_id": "uuid",
  "revenue_projection": {
    "total_ultimate_revenue": 75000000,
    "release_strategy": "wide_theatrical"
  },
  "run_monte_carlo": true,
  "num_simulations": 1000
}

Response: 202 Accepted
{
  "job_id": "uuid",
  "status": "pending",
  "estimated_duration_seconds": 180
}
```

**GET /api/v1/scenarios/evaluation/{job_id}**
```json
Response: 200
{
  "job_id": "uuid",
  "status": "completed",
  "evaluations": [
    {
      "scenario_id": "uuid1",
      "scenario_name": "incentive_maximized_scenario",
      "overall_score": 87.3,
      "equity_irr": 0.245,
      "tax_incentive_effective_rate": 25.0,
      "probability_of_recoupment": 0.89,
      "weighted_cost_of_capital": 11.2,
      "strengths": [...],
      "weaknesses": [...]
    }
  ]
}
```

**POST /api/v1/scenarios/compare**
```json
Request:
{
  "evaluation_job_id": "uuid",
  "stakeholder_perspective": "equity"  // or "producer", "lender", "balanced"
}

Response: 200
{
  "rankings": [
    {
      "rank": 1,
      "scenario_id": "uuid1",
      "scenario_name": "incentive_maximized_scenario",
      "weighted_score": 91.5,
      "percentile_rank": 100
    },
    ...
  ]
}
```

**POST /api/v1/scenarios/tradeoffs**
```json
Request:
{
  "evaluation_job_id": "uuid",
  "objective_pairs": [
    ["equity_irr", "probability_of_equity_recoupment"],
    ["tax_incentive_effective_rate", "equity_irr"]
  ]
}

Response: 200
{
  "pareto_frontiers": [
    {
      "objective_1_name": "equity_irr",
      "objective_2_name": "probability_of_equity_recoupment",
      "frontier_points": [
        {
          "scenario_id": "uuid1",
          "scenario_name": "incentive_maximized_scenario",
          "objective_1_value": 0.245,
          "objective_2_value": 0.89,
          "is_pareto_optimal": true
        },
        ...
      ],
      "trade_off_slope": 0.125
    }
  ],
  "recommendations": {
    "high_return_seeking": "uuid1",
    "risk_averse": "uuid2",
    "producer_focused": "uuid1",
    "cost_efficient": "uuid3",
    "balanced": "uuid1"
  }
}
```

---

### WebSocket for Real-Time Progress

**WS /ws/progress/{job_id}**

Connection established with job_id, server sends progress updates:

```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45,
  "current_step": 450,
  "total_steps": 1000,
  "message": "Running Monte Carlo simulation: scenario 450/1000"
}

{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "result": {...}
}
```

---

## Frontend Architecture

### Page Structure

```
/
├── / (landing page - public)
├── /login
├── /register
├── /dashboard
│   ├── /projects (list all projects)
│   ├── /projects/[id] (project detail)
│   │   ├── /scenarios (scenario management)
│   │   ├── /generate (scenario generation wizard)
│   │   ├── /evaluate (evaluation progress)
│   │   ├── /compare (comparison & ranking)
│   │   └── /visualize (interactive visualizations)
│   └── /settings (user settings)
└── /docs (documentation)
```

### Key Components

**1. Authentication Flow**
- Login/Register forms with validation
- JWT token storage (httpOnly cookies)
- Automatic token refresh
- Protected route middleware

**2. Project Management**
- Project list with search/filter
- Project creation wizard
- Budget allocation interface
- Jurisdiction selection map

**3. Scenario Generation**
- Template selection cards
- Custom allocation sliders
- Optimization objective selection
- Preview capital stack

**4. Evaluation Progress**
- Real-time progress bar (WebSocket)
- Job queue status
- Cancel operation button
- Estimated time remaining

**5. Comparison Dashboard**
- Scenario comparison table
- Sortable columns
- Stakeholder perspective toggle
- Export to Excel/PDF

**6. Visualizations**

**A. Sankey Diagram (Waterfall)**
```typescript
// Shows revenue flow through waterfall tiers
// Color-coded by stakeholder type
// Interactive hover for detailed breakdowns
// Animated flow transitions
```

**B. Tornado Chart (Sensitivity)**
```typescript
// Horizontal bar chart showing variable impact
// Sorted by impact magnitude
// Color gradient for positive/negative impact
// Click to drill down into scenario
```

**C. Pareto Frontier**
```typescript
// Scatter plot of 2 objectives
// Frontier line highlighting optimal scenarios
// Interactive points with scenario details
// Zoom and pan support
```

**D. IRR Distribution (Monte Carlo)**
```typescript
// Histogram showing P10/P50/P90
// Overlay normal distribution curve
// Confidence interval shading
// Percentile markers
```

---

## Key Features & Anticipating Issues

### 1. Authentication & Security

**Implementation:**
- JWT tokens with 1-hour expiry
- Refresh tokens with 7-day expiry
- Bcrypt password hashing (cost factor 12)
- Rate limiting: 5 login attempts per 15 minutes
- CORS configuration for specific origins
- HTTPS enforcement in production

**Issues Solved:**
- **Token expiry during long operations:** Automatic refresh before API calls
- **XSS attacks:** httpOnly cookies for token storage
- **CSRF attacks:** SameSite cookie attribute + CSRF tokens
- **Brute force:** Rate limiting with exponential backoff
- **Password security:** Minimum 8 characters, require uppercase/lowercase/numbers/symbols

### 2. Long-Running Operations

**Implementation:**
- Celery task queue with Redis broker
- WebSocket connections for real-time updates
- Job status polling fallback if WebSocket disconnects
- Graceful cancellation support

**Issues Solved:**
- **User leaves page:** Job continues in background, resume on return
- **Connection drops:** Automatic reconnection with exponential backoff
- **Server restart:** Jobs persist in database, resume after restart
- **Timeout concerns:** Set reasonable timeouts (10 min for Monte Carlo)

### 3. Performance Optimization

**Implementation:**
- Database indexing on frequently queried fields
- Redis caching for policy data (rarely changes)
- Pagination for project/scenario lists (20 per page)
- Lazy loading for large datasets
- Frontend code splitting and dynamic imports
- Image optimization (WebP format)
- API response compression (gzip)

**Issues Solved:**
- **Large result sets:** Cursor-based pagination
- **Slow policy queries:** Cache all policies at startup
- **Heavy visualizations:** Canvas rendering instead of SVG for >1000 points
- **Initial load time:** Skeleton screens, progressive loading

### 4. Data Validation

**Implementation:**
- Pydantic models for API request/response validation
- Zod schemas on frontend for form validation
- Database constraints (NOT NULL, UNIQUE, CHECK)
- Custom validators for business logic

**Issues Solved:**
- **Invalid budget:** Minimum $1M, maximum $1B
- **Invalid allocations:** Must sum to 100% (±1% tolerance)
- **Invalid dates:** Production dates must be in future
- **Circular dependencies:** Validate waterfall structure DAG

### 5. Error Handling

**Implementation:**
- Standardized error response format
- Error codes for client handling
- Detailed error messages in development
- Generic messages in production (security)
- Sentry integration for error tracking
- User-friendly error messages on frontend

**Error Response Format:**
```json
{
  "error": {
    "code": "INVALID_BUDGET",
    "message": "Project budget must be between $1,000,000 and $1,000,000,000",
    "details": {
      "provided": 500000,
      "min": 1000000,
      "max": 1000000000
    }
  }
}
```

### 6. File Uploads (Custom Policies)

**Implementation:**
- Maximum 5MB file size
- Allowed formats: JSON only
- Virus scanning (ClamAV in production)
- Schema validation against IncentivePolicy
- Storage in database (JSONB)

**Issues Solved:**
- **Large files:** Size limit + progress indicator
- **Invalid JSON:** Pre-parse validation with helpful error messages
- **Schema mismatch:** Detailed validation errors with field paths
- **Malicious content:** Sanitize all string fields

### 7. Concurrency & Race Conditions

**Implementation:**
- Database transactions for multi-step operations
- Optimistic locking (version column)
- Unique constraints on critical fields
- Atomic operations where possible

**Issues Solved:**
- **Simultaneous project creation:** Unique constraint on (user_id, project_name)
- **Concurrent scenario evaluation:** Queue jobs, process sequentially
- **Update conflicts:** Last-write-wins with timestamp tracking

### 8. Internationalization (Future)

**Preparation:**
- All user-facing strings in translation files
- Currency formatting based on locale
- Date/time formatting
- Number formatting (commas vs periods)

### 9. Accessibility

**Implementation:**
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Focus indicators
- ARIA labels on interactive elements

### 10. Testing Strategy

**Backend Tests:**
- Unit tests for each engine (already done)
- Integration tests for API endpoints
- End-to-end tests for critical flows
- Load testing (Apache Bench / Locust)
- Security testing (OWASP ZAP)

**Frontend Tests:**
- Unit tests for utility functions
- Component tests (React Testing Library)
- Integration tests (Playwright)
- Visual regression tests (Percy/Chromatic)

---

## Deployment Strategy

### Docker Configuration

**docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: filmfinance
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: filmfinance_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://filmfinance:${DB_PASSWORD}@postgres:5432/filmfinance_db
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://filmfinance:${DB_PASSWORD}@postgres:5432/filmfinance_db
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

### Environment Variables

**.env (development)**
```bash
# Database
DATABASE_URL=postgresql://filmfinance:devpassword@localhost:5432/filmfinance_db
DB_PASSWORD=devpassword

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Upload
MAX_UPLOAD_SIZE=5242880  # 5MB

# Monitoring
SENTRY_DSN=  # Add in production
```

---

## Success Criteria

**Functional Requirements:**
1. ✅ User can register, login, and manage account
2. ✅ User can create and manage projects
3. ✅ User can generate scenarios from all 5 templates
4. ✅ User can create custom optimized scenarios
5. ✅ User can evaluate scenarios with Monte Carlo
6. ✅ User can compare and rank scenarios
7. ✅ User can visualize trade-offs with Pareto frontiers
8. ✅ User can view Sankey diagrams for waterfall flows
9. ✅ User can export results to Excel/PDF
10. ✅ User receives real-time progress updates

**Quality Requirements:**
1. ✅ API response time <500ms for 95th percentile
2. ✅ Monte Carlo (1000 simulations) completes <3 minutes
3. ✅ Frontend initial load <2 seconds
4. ✅ Mobile responsive design
5. ✅ WCAG 2.1 AA accessibility compliance
6. ✅ 90%+ test coverage on critical paths
7. ✅ Zero security vulnerabilities (OWASP Top 10)
8. ✅ Uptime >99.9% in production

**Integration Requirements:**
1. ✅ All 3 engines accessible via API
2. ✅ Database transactions maintain data integrity
3. ✅ WebSocket real-time updates work reliably
4. ✅ Docker deployment works on any platform

---

## Timeline Estimate

**Phase 4A: Backend API (5-7 days)**
- Database setup and models (1 day)
- Authentication system (1 day)
- Engine 1 endpoints (1 day)
- Engine 2 endpoints (1 day)
- Engine 3 endpoints (1.5 days)
- WebSocket support (0.5 day)
- Testing and documentation (1 day)

**Phase 4B: Frontend (5-7 days)**
- Next.js setup and authentication (1 day)
- Project management UI (1 day)
- Scenario generation wizard (1.5 days)
- Comparison dashboard (1 day)
- D3.js visualizations (2 days)
- Testing and polish (1.5 days)

**Phase 4C: Deployment (2-3 days)**
- Docker configuration (1 day)
- Production environment setup (1 day)
- CI/CD pipeline (1 day)

**Total: 12-17 days** (approximately 2-3 weeks)

---

## Next Steps

1. ✅ Create this implementation plan
2. Set up FastAPI project structure
3. Implement database models and migrations
4. Build authentication system
5. Create API endpoints for all 3 engines
6. Set up Next.js frontend
7. Build UI components and pages
8. Implement D3.js visualizations
9. Add comprehensive tests
10. Deploy with Docker

---

**Document Status:** Complete
**Ready to Implement:** Yes
**Estimated Effort:** 100-120 hours
**Priority:** High
