# Gemini Architecture Analysis Archive

**Date:** November 2025
**Purpose:** Preserve the detailed architectural analysis from Gemini for reference

---

## Original Architecture Prompt Summary

The original prompt to Gemini outlined:

### Strategic Context
- **Studio**: Modern Magic (post-Spider-Verse animation studio)
- **Capital**: ~$25M company-level pool + future vehicles (slate financing, SPVs, output deals)
- **Tool Purpose**: Internal decision-making, deal design, team education

### Core Goals
1. More projects made per year
2. Retain ownership and creative control
3. Reduce effective cost
4. Innovate in financing/distribution

### Domain Requirements
The system must model:
- Incentives (tax credits, grants, subsidies)
- Capital stack (equity, loans, pre-sales, MGs)
- Waterfalls & backend (recoupment, definitions, cross-collateralization)
- IP & rights (ownership, licenses, reversions)
- Distribution (streamers, theatrical, windows)
- Process & friction (approvals, complexity)

---

## Gemini's Executive Summary (Key Points)

### Biggest Strengths Identified
1. Strategic alignment - explicitly optimizing for ownership/control, not just IRR
2. DealBlock abstraction - powerful for composability and comparison
3. Pragmatic stage awareness - lightweight metadata vs. heavy state machine
4. Focus on trust - versioning and golden scenarios from the start

### Most Important Risks/Gaps
1. **Ontology Brittleness**: DealBlock + RulesEngine must accurately translate contracts to waterfall logic
2. **Optimization Usability**: Weighted-sum optimization can be opaque
3. **False Precision**: System must guard against false sense of certainty

### Recommended Changes Before v1
1. Introduce DefinitionBlocks for Gross/Net definitions
2. Shift to constraint-based optimization
3. Model critical clauses explicitly (MFN, reversion, exclusivity)
4. Prioritize sensitivity analysis
5. Defer automated slate optimization

---

## Gemini's Prioritized Change List

| Priority | Area | Recommendation | Phase |
|----------|------|----------------|-------|
| H | Domain | DefinitionBlock for Gross/Net | v1 |
| H | Optimization | Constraint-based + Pareto | v1 |
| H | Domain | MFN, Reversion, Exclusivity fields | v1 |
| H | Trust | Basic Sensitivity Analysis | v1 |
| M | Slate | Defer automated SlateOptimizer | v1.1 |
| M | Trust | Explainability Traces | v1.1 |
| M | Strategy | Strategic Optionality metric | v1.1 |
| M | Engine | WaterfallInstructions abstraction | v1.1 |
| L | UX | Friction score visualization | v1 |
| L | Stage | Lightweight LifecyclePlan | Later |

---

## Question-by-Question Answers

### A. Strategic Alignment

**A1: Does architecture push toward goals?**
- Yes, strongly aligned due to OwnershipControlScorer integration
- Risk: If scoring is simplistic or weights favor financial returns

**A2: Missing metrics?**
- "Strategic Optionality" underdeveloped
- Should quantify value of keeping future paths open

### B. Domain Modelling

**B1: DealBlock robustness?**
- Sound for common patterns via templates
- Robustness depends on handling Gross/Net definitions

**B2: Schema refinement?**
- Strong normalization of Rights, Cashflows, Control Points
- DefinitionBlocks for financial definitions
- Map every field to EducationTopic for Tutor mode

**B3: Missing clause categories?**
- MFN (Most Favored Nations)
- Reversion Triggers
- Exclusivity Radiuses/Holdbacks
- Change of Control/Assignment
- Audit Rights

### C. Engines & Optimization

**C1: Engine separation?**
- Sound and logical
- RulesEngine handles complex translation

**C2: Multi-objective function?**
- Weighted sum poorly posed for strategic decisions
- Prefer constraint-based or Pareto visualization

**C3: Failure modes?**
- Cross-collateralization complexity
- Incentive stacking/timing
- Gross/Net definition errors

### D. Stage-Based Reasoning

**D1: Metadata vs state machine?**
- Right balance for v1
- Avoids workflow engine complexity

**D2: LifecyclePlan concept?**
- Wait, add later if usage demands

**D3: Stage-specific support?**
- Architecture supports via Scenario.horizon
- RulesEngine needs inter-stage awareness

### E. Slate & Capital

**E1: CapitalProgram flexibility?**
- Solid foundation
- Can capture pools, funds, output deals

**E2: SlateOptimizer improvements?**
- Risk of combinatorial explosion
- Use heuristics/phased optimization
- Model covenants explicitly

### F. Robustness & Trust

**F1: Versioning/golden scenarios sufficient?**
- Necessary but not sufficient
- Need sensitivity analysis, explainability, backtesting

**F2: Additional features?**
- Sensitivity Analysis (crucial)
- Explainability Traces
- Backtesting Framework

### G. Implementation

**G1: Buildable by small team?**
- Yes, with tight scope management

**G2: Phase 1 scope?**
- Core scenario modeling, basic DealBlocks
- Defer optimizers

**G3: Over-engineering?**
- ScenarioOptimizer, SlateOptimizer

**G4: Brittleness risks?**
- RulesEngine most likely area
- Use declarative approach where possible

### H. Red Team

**H1: Failure modes?**
- GIGO from ontology gaps
- Incorrect complex clause handling
- Impractical "clever" structures
- False precision

**H2: Guardrails?**
- Friction visualization
- Mandatory assumptions review
- Explainability
- Sensitivity visualization

---

## Gemini's Second Opinion (Sanity Check)

### Validated
- Domain modeling sound with DefinitionBlocks
- Engine boundaries logical
- Feasibility confirmed for small team
- WaterfallInstructions abstraction crucial

### Gaps Identified
- AssumptionSet needs explicit modeling
- RulesEngine needs formal definition
- Time-varying terms in DealBlocks

### Top 5 Improvements (Second Round)

1. **AssumptionSet as first-class entity** - Manage revenue curves, discount rates
2. **Formalize RulesEngine** - Clear schema for WaterfallInstructions
3. **Time-varying terms** - Fees that change post-breakeven
4. **Clause Impact Preview** - Show score deltas when editing
5. **Bandwidth Cost in CapitalProgram** - Not just financial capital

### Phase 1 Scope Check
- **Appropriately scoped**: Yes, if managed tightly
- **Cuts recommended**:
  1. Defer Slate features entirely
  2. Simplify sensitivity to Low/Med/High presets
  3. Model only internal MM capital pool

---

## Integration Into Current Plan

### Adopted Immediately
- DealBlock abstraction ✅
- OwnershipControlScorer ✅
- Explicit scope fencing ✅
- Quality gates ✅

### Adopted with Modification
- DefinitionBlocks → Deferred (current waterfall works)
- Constraint-based optimization → Add as filter layer
- RulesEngine → Start with config files, not DSL

### Deferred to Phase 2+
- AssumptionSet formal modeling
- SlateAnalyzer/Optimizer
- CapitalPrograms
- Stage metadata
- Backtesting framework

---

## Key Insights Preserved

### On Deal Types
> "Deal Type is King: A single `deal_type` field drives 80% of the schema logic."

### On Control Scoring
> "The real value of DealBlock is capturing non-financial deal terms (creative control, sequel rights) that your current schema misses."

### On Waterfall Mapping
> "DealBlock should EXTEND your existing waterfall, not replace it. Focus on capturing the DEAL TERMS that populate waterfall parameters."

### On Practical Constraints
> "Don't model every possible contract clause. Model what affects: Financial flows, Control/approval rights, Feasibility."

---

*This document preserved for architectural reference and future iterations.*
