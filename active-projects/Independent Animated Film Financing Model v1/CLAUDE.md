# Film Financing Navigator - Project Context

## Overview
Production-ready financial modeling platform for animated film financing, being extended with strategic deal modeling capabilities.

**Current Phase:** Phase 1 - Foundation Completion
**Status:** ✅ COMPLETE (87 tests passing)

## Architecture

### Tech Stack
- **Backend:** Python 3.11 + FastAPI + Pydantic v2
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **Data:** In-memory (Postgres planned for Phase 2)
- **Testing:** pytest (backend), Jest (frontend)

### Key Directories
```
backend/
├── engines/           # 3 calculation engines
│   ├── incentive_calculator/
│   ├── waterfall_executor/
│   └── scenario_optimizer/
├── models/            # Pydantic data models
├── api/               # FastAPI application
├── data/policies/     # Tax incentive JSON files
└── tests/

frontend/
├── app/dashboard/     # Next.js pages
├── components/        # React components
└── lib/api/           # API client + types

docs/
├── MASTER_PLAN.md     # Strategic architecture plan
└── architecture/      # Detailed specs
```

## Development Standards

### Python Backend
```python
# Models: Pydantic v2 with Field validators
class MyModel(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount in USD")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return v

# Engines: dataclasses with to_dict()
@dataclass
class EngineResult:
    value: Decimal

    def to_dict(self) -> Dict:
        return {"value": str(self.value)}
```

### TypeScript Frontend
```typescript
// Types mirror backend exactly
interface MyModel {
    amount: number;  // Decimal → number
}

// API calls with error handling
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Testing
- Backend: pytest with class-based organization
- Target: 90%+ coverage on core logic
- Golden scenarios for engine validation

## Current Work: Phase 1 COMPLETE ✅

### Completed
- ✅ 3 calculation engines (Incentive, Waterfall, Scenario)
- ✅ Full-stack application
- ✅ 16 tax incentive jurisdictions
- ✅ Master plan documentation
- ✅ DealBlock specification + implementation (39 tests)
- ✅ OwnershipControlScorer specification + implementation (34 tests)
- ✅ Skills and commands configured
- ✅ API endpoints: `/deals`, `/ownership`
- ✅ Integration testing passed

### Ready for Phase 2
- ⏳ CapitalPrograms (company-level capital management)
- ⏳ SlateAnalyzer (portfolio-level decisions)
- ⏳ Stage Awareness (lifecycle decision points)
- ⏳ Database persistence (Postgres)

## Scope Boundaries

### In Scope (Phase 1)
- DealBlock with 6 deal types
- OwnershipControlScorer with 4 dimensions
- API integration completion
- Comprehensive tests

### Out of Scope (Deferred)
- DefinitionBlocks (Gross/Net abstractions)
- CapitalPrograms (company-level capital)
- SlateOptimizer (portfolio optimization)
- Database persistence
- Authentication

## Commands

### Running the Project
```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend
cd frontend && npm run dev

# Full stack (Docker)
make up
```

### Custom Commands
- `/run-tests [backend|frontend|all]` - Run tests
- `/validate-phase [1]` - Check phase completion

## Key Files for New Development

### When Adding a New Model
1. `backend/models/<name>.py` - Pydantic model
2. `backend/models/__init__.py` - Export it
3. `backend/api/app/schemas/<name>.py` - API schema
4. `backend/api/app/api/v1/endpoints/<name>.py` - Endpoints
5. `frontend/lib/api/types.ts` - TypeScript interface
6. `backend/tests/test_<name>.py` - Tests

### When Adding a New Engine
1. `backend/engines/<name>/` - Engine directory
2. Core calculation class with dataclass I/O
3. `to_dict()` methods for serialization
4. Integration with existing engines if needed

## Quality Gates

Before marking any task complete:
- [ ] All tests pass
- [ ] No TypeScript errors
- [ ] Docstrings on public methods
- [ ] Field validators on constrained fields
- [ ] to_dict() on engine outputs
- [ ] Error handling is specific

## Reference Documents

- `docs/MASTER_PLAN.md` - Full architecture plan
- `docs/architecture/DEALBLOCK_SPECIFICATION.md` - DealBlock spec
- `docs/architecture/OWNERSHIP_CONTROL_SCORER_SPECIFICATION.md` - Scorer spec
- `docs/architecture/GEMINI_ANALYSIS_ARCHIVE.md` - External review archive
