# Film Financing Navigator: Master Architecture Plan

**Version:** 2.0
**Date:** November 2025
**Status:** Phase 1 Active Development

---

## Executive Summary

This document captures the strategic architecture plan for evolving the Film Financing Navigator from a production-ready financial modeling tool into a comprehensive deal structuring and decision system for Modern Magic.

### Strategic Goals
1. **More projects made** - Increase throughput of greenlight-able projects
2. **Higher ownership & control** - Minimize "quiet IP dispossession"
3. **Lower effective cost** - Maximize soft money, smart capital stacking
4. **Innovative structures** - Enable novel financing/distribution arrangements

### Current State (v1.0 - Complete)
- ✅ **Engine 1**: Tax Incentive Calculator (16 jurisdictions)
- ✅ **Engine 2**: Waterfall Executor (Monte Carlo, IRR/NPV)
- ✅ **Engine 3**: Scenario Optimizer (Multi-objective, Pareto frontier)
- ✅ Full-stack application (FastAPI + Next.js)
- ✅ 100% backend test coverage (29/29 tests)

### Target State (v2.0 - In Progress)
- 🔄 **DealBlocks**: Composable deal structure abstraction
- 🔄 **OwnershipControlScorer**: Strategic scoring beyond financials
- ⏳ **CapitalPrograms**: Company-level capital management
- ⏳ **SlateAnalyzer**: Portfolio-level decisions
- ⏳ **Stage Awareness**: Lifecycle decision points

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FILM FINANCING NAVIGATOR                      │
├─────────────────────────────────────────────────────────────────┤
│  FRONTEND (Next.js 14 + TypeScript + Tailwind)                  │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐           │
│  │Dashboard│Incentive│Waterfall│Scenarios│DealBlock│           │
│  │         │   UI    │   UI    │   UI    │   UI    │           │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘           │
├─────────────────────────────────────────────────────────────────┤
│  API LAYER (FastAPI + Pydantic v2)                              │
│  /api/v1/incentives | /waterfall | /scenarios | /deals          │
├─────────────────────────────────────────────────────────────────┤
│  DOMAIN SERVICES                                                 │
│  ┌──────────────┬──────────────┬──────────────┐                 │
│  │ DealTerms    │ Scenario     │ Capital      │                 │
│  │ Service      │ Service      │ Service      │                 │
│  └──────────────┴──────────────┴──────────────┘                 │
├─────────────────────────────────────────────────────────────────┤
│  CALCULATION ENGINES                                             │
│  ┌───────────┬───────────┬───────────┬───────────────────┐      │
│  │ Incentive │ Waterfall │ Scenario  │ Ownership/Control │      │
│  │ Engine    │ Engine    │ Optimizer │ Scorer            │      │
│  └───────────┴───────────┴───────────┴───────────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│  DATA MODELS (Pydantic)                                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │ Financial   │ DealBlock   │ Capital     │ Ownership   │      │
│  │ Instruments │ + Clauses   │ Stack       │ Structure   │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                      │
│  Postgres + Redis + Policy JSON Store                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Completion (Current)

### 1A. Complete API Integration
**Status:** Ready to implement
**Effort:** 2-3 hours
**Scope:** Wire Engine 2 & 3 frontend to real backend endpoints

### 1B. DealBlock Domain Model
**Status:** Specification complete
**Effort:** 1-2 weeks
**Scope:** Composable deal structure abstraction

#### Core DealBlock Schema
```python
class DealBlock(BaseModel):
    # Identification
    deal_id: str
    deal_type: DealType  # equity, presale, license, cost_plus, etc.

    # Financial Terms
    amount: Decimal
    payment_schedule: Dict[str, Decimal]
    recoupment_priority: RecoupmentPriority
    backend_participation_pct: Optional[Decimal]

    # Rights & Control
    territories: List[str]
    rights_windows: List[str]
    creative_approvals: Dict[str, str]  # What requires approval, by whom

    # Special Provisions (affect optimization)
    mfn_clause: bool
    reversion_triggers: Optional[Dict]
    sequel_rights_holder: Optional[str]

    # Methods
    def to_waterfall_nodes(self) -> List[WaterfallNode]
    def calculate_control_impact(self) -> ControlImpact
```

#### Deal Types to Support (MVP)
| Type | Financial Impact | Control Impact |
|------|-----------------|----------------|
| `EQUITY_INVESTMENT` | Ownership %, premium, backend | Board seats, approvals |
| `PRESALE_MG` | MG amount, overage split | Delivery requirements |
| `STREAMER_LICENSE` | License fee, term | Territory restrictions |
| `STREAMER_ORIGINAL` | Cost-plus | Full creative control loss |
| `THEATRICAL_DISTRIBUTION` | Fees, P&A | Marketing approval |
| `GAP_FINANCING` | Loan terms | Collateral requirements |

### 1C. OwnershipControlScorer Engine
**Status:** Specification complete
**Effort:** 1 week
**Scope:** Strategic scoring beyond IRR/NPV

#### Scoring Dimensions
| Score | Range | Description |
|-------|-------|-------------|
| `ownership_score` | 0-100 | How much IP/rights retained |
| `control_score` | 0-100 | Creative control retained |
| `optionality_score` | 0-100 | Future flexibility preserved |
| `friction_score` | 0-100 | Deal complexity/execution risk |

#### Key Inputs
- DealBlocks attached to scenario
- Capital stack composition
- Rights allocation matrix
- Approval chains

#### Key Outputs
- Aggregate scores with explainability traces
- Clause-by-clause impact breakdown
- Recommendations for improving scores

---

## Phase 2: Company-Level & Portfolio (Deferred)

### 2A. CapitalPrograms
Model company-level capital vehicles:
- Internal MM investment pool (~$25M)
- External funds and vehicles
- Output deals and commitments
- Bandwidth constraints

### 2B. SlateAnalyzer
Portfolio-level analysis:
- Manual slate construction
- Capital utilization by program
- Ownership-weighted portfolio metrics
- Constraint validation

### 2C. Lifecycle Metadata
Stage-aware decision making:
- `Project.current_stage`: LifecycleStage enum
- `Scenario.decision_stage`: When this structure applies
- `Scenario.horizon`: Time span covered

---

## Phase 3: Advanced Features (Future)

- **DefinitionBlocks**: Explicit Gross/Net/AGR definitions
- **SlateOptimizer**: Automated portfolio optimization
- **Education/Tutor Mode**: Contextual explanations
- **RulesEngine DSL**: Declarative business rules
- **Database Persistence**: Project save/load

---

## Scope Discipline

### Explicit "NOT IN PHASE 1" List

| Deferred Item | Reason | Target Phase |
|---------------|--------|--------------|
| DefinitionBlocks | Current waterfall works | 2+ |
| CapitalPrograms | Need DealBlocks working first | 2 |
| SlateOptimizer | Need single-project solid | 2+ |
| Stage/Lifecycle metadata | Nice-to-have | 2 |
| Education/Tutor mode | Polish, not foundation | 3 |
| RulesEngine DSL | Start with simple config | 2+ |
| Database persistence | In-memory fine for now | 2 |

### Quality Gates

Every component must pass:
1. **Unit tests**: 90%+ coverage on core logic
2. **Type safety**: No TypeScript/Pydantic errors
3. **Integration**: Works with existing engines
4. **Documentation**: Clear docstrings and examples
5. **Code review**: Follows established patterns

---

## Implementation Patterns

### Backend (Python)
- **Models**: Pydantic v2 BaseModel with Field validators
- **Engines**: Classes with dataclass I/O + `to_dict()` methods
- **APIs**: FastAPI routers with request/response schemas
- **Tests**: pytest with class-based organization

### Frontend (TypeScript)
- **State**: React hooks (useState)
- **API**: Axios via services.ts
- **Types**: Mirror backend schemas exactly
- **UI**: shadcn/ui components (Card, Button, Input)

### Data Flow
```
DealBlock (Model)
    ↓
API Schema (Pydantic)
    ↓
REST Endpoint
    ↓
Frontend Service (Axios)
    ↓
TypeScript Interface
    ↓
React Component
```

---

## Risk Mitigation

### Top 5 Risks

1. **DealBlock Ontology Brittleness**
   - *Risk*: Schema can't capture real deal complexity
   - *Mitigation*: Start with 5 common patterns, expand based on usage

2. **Waterfall Translation Errors**
   - *Risk*: DealBlock → Waterfall mapping incorrect
   - *Mitigation*: Golden scenarios with known outcomes

3. **Optimization Produces Impractical Structures**
   - *Risk*: "Clever but un-producible" suggestions
   - *Mitigation*: Friction score prominently displayed

4. **False Precision in Scoring**
   - *Risk*: Users over-trust point estimates
   - *Mitigation*: Sensitivity analysis, range displays

5. **Scope Creep**
   - *Risk*: Plan grows beyond team capacity
   - *Mitigation*: Explicit scope fence, phase gates

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Engine 2 & 3 frontend hits real API
- [ ] DealBlock model with 6 deal types
- [ ] OwnershipControlScorer with 4 score dimensions
- [ ] All tests passing (target: 50+ new tests)
- [ ] Documentation complete

### v2.0 Complete When:
- [ ] Phase 1 complete
- [ ] CapitalPrograms modeled
- [ ] SlateAnalyzer functional
- [ ] Stage metadata on Projects/Scenarios
- [ ] End-to-end workflow validated with real scenarios

---

## Appendix: Gemini Architecture Review Summary

### Key Recommendations Adopted
1. ✅ Introduce DealBlock abstraction
2. ✅ Add OwnershipControlScorer
3. ✅ Defer automated optimization
4. ✅ Explicit scope fencing
5. ✅ Quality gates and golden scenarios

### Recommendations Deferred
1. ⏳ DefinitionBlocks (v2+)
2. ⏳ Full RulesEngine abstraction (v2+)
3. ⏳ Constraint-based optimization (v1.1)
4. ⏳ SlateOptimizer automation (v2+)

### Architecture Validation
- Monolith approach: ✅ Approved for small team
- Tech stack: ✅ FastAPI + Next.js appropriate
- Engine separation: ✅ Sound and maintainable
- Data model: ✅ Pydantic v2 patterns good

---

*Document maintained as source of truth for project direction.*
