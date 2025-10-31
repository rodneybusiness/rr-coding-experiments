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

### Phase 2: Modeling Engine Development 🔄 IN PROGRESS
- Define Core Data Schemas (Pydantic)
- Develop Waterfall Engine
- Implement Incentive Net Benefit Calculator
- Develop Uncertainty layer

### Phase 3: Retrieval & Facts Pipeline 🔄 IN PROGRESS
- Curate Market Rate Card
- Curate Incentive Policy details

### Phase 4: Front-End UI/UX 📋 PENDING
- Dashboard development
- Visualization components
- User workflows

### Phase 5: Calibration & Validation 📋 PENDING
- Expert review
- Model calibration
- Case study validation

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (for production)

### Installation
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

### Development
```bash
# Run backend
cd backend
uvicorn main:app --reload

# Run frontend
cd frontend
npm run dev
```

## Current Sprint Tasks

1. **Implement Core Data Schemas** - Pydantic models for all entities
2. **Curate Policy Layer Data** - UK, Ireland, Canada, USA incentives
3. **Curate Market Rate Card** - Current market rates and fees
4. **Implement Incentive Calculator** - Net benefit calculations
5. **Implement Waterfall Engine** - IPA/CAMA logic

## Contributing

This is a research and development project. For questions or collaboration inquiries, please open an issue.

## License

TBD

## Version

v1.0.0 - Initial Implementation (October 2025)
