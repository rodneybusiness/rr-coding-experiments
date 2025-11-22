# Production-Readiness Assessment: Independent Animated Film Financing Model v1

## Executive Summary
The codebase claims a production-grade navigator but currently operates as a prototype. Critical correctness gaps (enum drift, missing integrations), shallow data coverage, and placeholder API/frontend layers prevent end-to-end use. This plan applies the provided deep-dive prompt to chart remediation work that will make Engines 1–3 reliable and shippable.

## Observed Critical Gaps (Evidence)
- **Enum/logic mismatch in incentive calculator**: The calculator assumes `TAX_CREDIT_LOAN` and `TRANSFER_TO_INVESTOR` monetization modes, but the model only defines `direct_cash`, `transfer_sale`, `tax_liability_offset`, and `loan_collateral`, guaranteeing runtime errors before any calculation completes.【F:backend/engines/incentive_calculator/calculator.py†L300-L335】【F:backend/models/incentive_policy.py†L15-L31】
- **Placeholder API services**: Startup/shutdown hooks, database/cache initialization, and health checks are all TODOs, so the FastAPI service cannot meet production claims for persistence, caching, or observability.【F:backend/api/app/main.py†L16-L108】
- **Static, non-functional frontend**: Dashboard metrics and activity feeds are hard-coded; there is no data fetching or state management for the advertised engines.【F:frontend/app/dashboard/page.tsx†L21-L119】
- **Sparse policy dataset**: Only a dozen policy JSON files exist, far short of the advertised 25+ jurisdictions and without validation metadata or freshness checks.【889277†L1-L3】
- **Minimal automated testing**: The test suite only covers model instantiation/validation; there are no engine, API, or UI tests to back the “60+ integration tests” claim.【F:backend/tests/test_models.py†L1-L120】

## Remediation & Enhancement Plan (per prompt)

### 1) Validate and Fix Correctness
- **Unify enums and guardrails**
  - Expand `MonetizationMethod` to include the calculator’s expected modes (loan, transfer-to-investor) or refactor calculator logic to the existing set; add explicit validation that rejects unsupported modes with actionable errors.
  - Add cross-module type checks so stacking/optimizer logic fails fast when inputs are misaligned.
- **Engine hardening**
  - Create deterministic unit tests for single- and multi-jurisdiction incentive calculations (including stacking caps and timing adjustments), waterfall edge cases (waterfall node ordering, negative cash flows), and optimizer convergence (multiple starts, cache hits, constraint violations).
  - Add fuzz tests for capital stack bounds and structural rules to prevent invalid leverage mixes from entering optimization.
- **Reference acceptance criteria**
  - ✅ Calculator rejects unknown monetization modes with 4xx-style errors; ✅ optimizer completes SLSQP runs from at least three seeds with <1e-6 tolerance; ✅ waterfall returns consistent IRR/NPV for seeded revenue curves.

### 2) Harden Data Quality
- **Define schema and provenance**
  - Mandate `source_url`, `source_version_date`, `effective_date`, `expiry_date`, and `validation_checksum` fields for each policy; enforce via Pydantic validators and a JSON schema linter.
- **Coverage expansion**
  - Prioritize adding US (NY, NM, LA), UK regional, EU (ES/PT/DE), Asia (SG/KR/JPN), and LATAM (MX/BR/CO) policies to reach 25+ jurisdictions.
  - Document stacking/interaction rules per region (e.g., UK AVEC + reliefs, US federal + state, AUS Producer + PDV) and encode them as rule objects consumed by the calculator.
- **Freshness & QA**
  - Add a scheduled data refresh job that diff-checks policies against authoritative sources; fail CI if `last_updated` exceeds SLA (e.g., 90 days) or checksum drifts.

### 3) Ensure Architectural Viability
- **API surface & persistence**
  - Define endpoints for policy lookup, incentive runs, waterfall executions, optimizer jobs, and scenario persistence. Back them with PostgreSQL (scenarios, runs, users) and Redis (policy cache, job status).
- **Background jobs**
  - Use Celery/RQ for Monte Carlo batches, policy refreshes, and heavy optimizer runs with idempotent job IDs and progress events.
- **Observability & security**
  - Implement health checks that ping DB/Redis/workers, structured logging, Prometheus metrics, OpenTelemetry tracing, OAuth2/JWT auth, role-based access, and rate limiting. Store secrets in env/secret manager; add CSP/TrustedHosts enforcement.

### 4) Deliver Usable UX
- **User flows**
  - Map producer/financier/distributor journeys: onboarding (project + jurisdictions), engine runs (incentive, waterfall, optimizer), scenario comparison, and export.
- **UI implementation**
  - Replace hard-coded dashboard stats with live data from API; add forms and validation for policy selections, stack inputs, and waterfall templates. Visualize cash flows, IRR/NPV, Pareto frontiers, and sensitivity charts with download/export (PDF/CSV/XLSX) options.
- **Acceptance criteria**
  - ✅ Dashboard reflects latest run results; ✅ users can save/load scenarios; ✅ exports reproduce on-screen calculations with timestamps and policy versions.

### 5) Prioritize by Impact (30/60/90 Roadmap)
- **Day 0–30**: Fix enum mismatches; add unit tests for incentives/stack constraints; implement API health checks and database/Redis wiring; load policies into Redis cache; replace dashboard stats with live API calls.
- **Day 31–60**: Expand policy library to 25+ with validation metadata; implement stacking rule engine; add integration tests for Engines 1–3 via FastAPI endpoints; ship background worker for Monte Carlo/optimizer jobs; add authentication/authorization and rate limiting.
- **Day 61–90**: Add Pareto visualization and scenario comparison UI; implement scheduled data refresh with SLA alerts; add observability (metrics/tracing/logging dashboards); deliver export workflows and full regression suite (API + UI e2e) meeting agreed SLOs.

## Ownership & Next Steps
- Assign leads: **Backend** (API/data quality), **Modeling** (engines/tests), **Frontend** (UX/state), **DevOps** (observability/deployment).
- Kick off with a proof-of-fix branch that addresses enum alignment and adds the first wave of engine tests; use CI to gate subsequent roadmap milestones.
