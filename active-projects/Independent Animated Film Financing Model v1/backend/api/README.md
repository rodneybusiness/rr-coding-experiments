# Film Financing Navigator API

FastAPI REST API for the Film Financing Navigator platform.

**Last Updated**: November 25, 2025

## API Implementation

### Endpoints

**Engine 1: Tax Incentive Calculator**
- `POST /api/v1/incentives/calculate` - Calculate tax credits across jurisdictions
- `GET /api/v1/incentives/jurisdictions` - List available jurisdictions
- `GET /api/v1/incentives/jurisdictions/{jurisdiction}/policies` - Get policies

**Engine 2: Waterfall Analysis**
- `POST /api/v1/waterfall/execute` - Execute waterfall distribution with returns

**Engine 3: Scenario Optimizer**
- `POST /api/v1/scenarios/generate` - Generate optimized capital stack scenarios
- `POST /api/v1/scenarios/compare` - Compare scenarios

**Engine 4: Ownership & Control Scoring** (NEW)
- `POST /api/v1/deals` - Create and validate DealBlocks
- `POST /api/v1/ownership/score` - Score deal blocks on 4 dimensions
- `POST /api/v1/ownership/compare` - Compare multiple scenarios
- `GET /api/v1/ownership/weights` - Get default scoring weights
- `GET /api/v1/ownership/dimensions` - Get dimension information for UI tooltips

### Features

✅ Complete Request/Response Schemas with Pydantic
✅ Real Backend Integration (all 4 engines)
✅ Error Handling & Validation
✅ CORS Configuration
✅ Auto-Generated Documentation (OpenAPI/Swagger)
✅ DealBlock model with 6 deal types
✅ 4-dimension ownership/control scoring

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

### Test Coverage

- 124 backend tests passing
- 87 core tests + 37 integration tests
