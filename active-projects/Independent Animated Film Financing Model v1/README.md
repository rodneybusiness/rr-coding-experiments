# Independent Animated Film Financing Model v1

## Project Vision

To build an exceptional, A+ financial simulation model and user interface that allows producers, financiers, and studios to clearly visualize, understand, and optimize the various pathways for developing, financing, producing, and distributing an animated feature film or series.

## The Core Objective

The central question this tool answers:
> For a specific animated project, what combination of development → financing → production structure → distribution path maximizes the balance of **Creative Control**, **Expected Financial Returns (IRR/NPV)**, and **Risk-Mitigation**, tailored to specific stakeholders?

## Key Features

1. **Exhaustive Pathway Modeling** - Modular coverage of all financing pathways
2. **Accurate Policy Layer** - Dynamic, jurisdiction-aware tax incentive modeling
3. **Industry-Standard Financial Logic** - Fully parametric recoupment waterfalls
4. **Risk & Uncertainty Modeling** - Hybrid Decision Tree and Monte Carlo simulation
5. **Stakeholder-Specific Views** - Intuitive dashboards for Producers, Investors, and Distributors

## Technical Stack

- **Back-End**: Python (Pandas, NumPy, SciPy)
- **Simulation**: PyMC (Bayesian), OR-Tools (Optimization)
- **API**: FastAPI
- **Database**: PostgreSQL + Neo4j (optional)
- **Front-End**: Next.js + TypeScript
- **Visualization**: D3.js / Recharts

## Project Structure

```
.
├── backend/
│   ├── models/          # Pydantic data schemas
│   ├── engines/         # Waterfall and incentive calculators
│   ├── data/
│   │   ├── policies/    # Tax credit and incentive data
│   │   └── market/      # Market rate cards
│   └── tests/           # Unit and integration tests
├── frontend/            # Next.js UI
├── docs/
│   ├── ontology/        # Core ontology JSON
│   └── prompts/         # AI agent prompts
└── README.md
```

## Project Roadmap

### Phase 1: Ontology Definition ✅ COMPLETED
- Comprehensive Animation Financing Ontology

### Phase 2: Modeling Engine Development ✅ COMPLETED
- ✅ Core Data Schemas (Pydantic)
- ✅ Engine 1: Tax Incentive Calculator
- ✅ Engine 2: Waterfall Executor with Monte Carlo
- ✅ Engine 3: Scenario Optimizer
- ✅ S-curve Investment Drawdown Model

### Phase 3: Retrieval & Facts Pipeline ✅ COMPLETED
- ✅ Market Rate Card (curated)
- ✅ 25+ Jurisdiction Tax Incentive Policies
- ✅ Policy loader and validation

### Phase 4: Front-End UI/UX ✅ COMPLETED
- ✅ Phase 4A: Beautiful Next.js 14 UI with Tailwind CSS
- ✅ Phase 4B: Complete FastAPI REST API
- ✅ Phase 4C: Full API Integration (All 3 Engines)
- ✅ Production-ready Docker deployment

### Phase 5: Testing & Validation ✅ COMPLETED
- ✅ 60+ Integration tests passing
- ✅ Expert code review (8.2/10 quality score)
- ✅ TypeScript compilation: 0 errors
- ✅ Production readiness verified

## Getting Started

### 🐳 Docker Deployment (Recommended)

The fastest way to get started:

```bash
# 1. Install and set up
make install

# 2. Start all services
make up

# 3. Check health
./docker-healthcheck.sh
```

**Access the application:**
- 🎨 **Frontend UI:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

For detailed Docker deployment guide, see **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)**

### 📦 Manual Installation (Alternative)

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (for production)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

#### Development
```bash
# Terminal 1: Run backend
cd backend
uvicorn api.app.main:app --reload --port 8000

# Terminal 2: Run frontend
cd frontend
npm run dev
```

## Features

### 🎯 Three Powerful Engines

1. **Tax Incentive Calculator (Engine 1)**
   - Calculate tax credits across 25+ jurisdictions
   - Multi-jurisdiction stacking scenarios
   - Cash flow projection (8 quarters)
   - Monetization analysis (Direct, Loan, Broker)

2. **Waterfall Executor (Engine 2)**
   - Industry-standard recoupment waterfall
   - Stakeholder return analysis (IRR, NPV, Cash-on-Cash)
   - Monte Carlo simulation (P10/P50/P90)
   - Revenue projection across release windows

3. **Scenario Optimizer (Engine 3)**
   - Generate optimized capital stack scenarios
   - Multi-objective optimization (IRR, Risk, Tax Rate)
   - Pareto frontier analysis
   - Interactive scenario comparison

### 🚀 Production Ready

- ✅ Full-stack application (FastAPI + Next.js)
- ✅ Docker deployment with docker-compose
- ✅ PostgreSQL database with health checks
- ✅ Redis caching for performance
- ✅ Comprehensive error handling
- ✅ TypeScript type safety (0 errors)
- ✅ 60+ integration tests
- ✅ Expert code review validated

## Contributing

This is a research and development project. For questions or collaboration inquiries, please open an issue.

## License

TBD

## Version

v1.0.0 - Initial Implementation (October 2025)
