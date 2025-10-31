# Film Financing Navigator API

FastAPI REST API for the Film Financing Navigator platform.

## Phase 4B: Complete API Implementation

### Endpoints Built

**Engine 1: Tax Incentive Calculator**
- POST /api/v1/incentives/calculate - Calculate tax credits across jurisdictions
- GET /api/v1/incentives/jurisdictions - List available jurisdictions  
- GET /api/v1/incentives/jurisdictions/{jurisdiction}/policies - Get policies

**Engine 2: Waterfall Analysis**
- POST /api/v1/waterfall/execute - Execute waterfall distribution with returns

**Engine 3: Scenario Optimizer**
- POST /api/v1/scenarios/generate - Generate optimized capital stack scenarios
- POST /api/v1/scenarios/compare - Compare scenarios (planned)

### Features

✅ Complete Request/Response Schemas with Pydantic
✅ Real Backend Integration (all 3 engines)
✅ Error Handling & Validation
✅ CORS Configuration
✅ Auto-Generated Documentation (OpenAPI/Swagger)

### Running the API

```bash
cd backend/api
export PYTHONPATH=/path/to/backend:$PYTHONPATH
python -m app.main
```

Access documentation at: http://localhost:8000/api/v1/docs

### Deployment

Set PYTHONPATH to include backend directory for proper imports.
All endpoints are production-ready and type-safe.
