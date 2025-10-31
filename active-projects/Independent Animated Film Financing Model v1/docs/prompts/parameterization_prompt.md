# Parameterization Prompt - Data Acquisition

## Role
You are the "Council of Animation Industry Veterans" (Veteran Producer, Entertainment Lawyer, Film Financier, Distribution Executive).

## Objective
Populate the Animation Financing Navigator's initial database with A+, accurate, and realistic quantitative parameters, ranges, and policy details, reflecting the current market (Late 2025). This data forms the core "weights" of the simulation engine.

## Task
Provide the detailed parameters organized into the following sections. Use external research/RAG to ensure up-to-date information. For every data point, provide a **"Range" (Low-Base-High)** and **"Key Assumptions/Citations."**

---

## 1. FINANCING INSTRUMENT PARAMETERS

Provide current market rates, fees, and typical terms.

### A. DEBT
- **Senior Production Loans**
  - Interest Rates (%)
  - Origination/Commitment Fees (%)
  - Advance Rate against collateral (%)

- **Tax Credit Loans**
  - Interest Rates (%)
  - Advance Rate (% of certified credit)
  - Fees

- **Gap Financing**
  - Interest Rates (%)
  - Advance Rate (% of unsold territory value)
  - Fees

- **Supergap/Mezzanine**
  - Interest Rates (%)
  - Risk premium vs. senior debt
  - Typical collateral

- **Bridge Financing**
  - Interest Rates (%)
  - Term length
  - Fees

### B. EQUITY & PARTICIPATION
- **Investor Premium ranges** (% ROI expectations)
- **Typical "Net Profit" definitions** and participation percentages
- **Equity recoupment priority** (e.g., after debt, before producer participation)

### C. ANCILLARY SERVICES
- **Completion Bond**
  - Fees (% of budget)
  - Contingency requirements (% of budget)

- **CAMA fees** (% or flat fee)

- **E&O Insurance premiums** (% of budget or flat fee)

---

## 2. DISTRIBUTION AND SALES PARAMETERS

Provide typical fees, expense structures, and deal terms.

### A. SALES AGENTS
- **Commission Rates** (% of MGs and overages)
- **Expense Caps** (% of revenue or flat fee)
- **Typical market fees** (festival attendance, materials)

### B. DISTRIBUTORS (Theatrical/VOD)
- **Distribution Fees by Window**:
  - Theatrical (%)
  - PVOD/EST (%)
  - SVOD (%)
  - AVOD/FAST (%)
  - Television (%)

- **P&A Recoupment structure**
  - Typical P&A budget ranges
  - Recoupment multiplier (e.g., 110%, 120%)

### C. STREAMER DEALS (SVOD/AVOD)
- **Cost-Plus Premium/Overhead percentages**
  - Typical range for Netflix, Amazon, Apple, etc.

- **Licensing Model assumptions**
  - Flat fee ranges by budget tier
  - Performance-based models (rare but emerging)

---

## 3. INCENTIVE POLICY CURATION (THE POLICY LAYER)

Detail the precise mechanics for the following key jurisdictions:

### For EACH Jurisdiction (UK, Ireland, Canada [Federal + Key Provinces], USA [Georgia, California]):

#### A. HEADLINE RATE(S) AND INSTRUMENT TYPE
- Percentage rate
- Type: Tax credit (refundable/transferable/non-refundable), Grant, Rebate

#### B. BASE (QAPE DEFINITION)
- What spend qualifies?
- What is excluded?
- Minimum spend requirements
- Cultural/content tests

#### C. CAPS
- Per-project caps
- Annual program caps
- Per-applicant caps

#### D. MONETIZATION & TIMING
- **Transfer discount rates** (if transferable)
- **Time from audit to cash receipt**
- **Financing options** (loans against credits)

#### E. NET-OF-TAX IMPACT
- Is the incentive taxable income?
- Effective net benefit calculation
- Tax treatment in jurisdiction

#### F. KEY ELIGIBILITY REQUIREMENTS
- Cultural tests (e.g., points systems)
- SPV requirements
- Residency requirements
- Labor requirements (% local crew)
- Spend requirements (% in jurisdiction)

---

## Jurisdictions to Detail

1. **United Kingdom** - Audio-Visual Expenditure Credit (AVEC)
2. **Ireland** - Section 481
3. **Canada** - Federal (CPTC) + Quebec (PSTC) + Ontario (OCASE)
4. **USA** - Georgia (GEFA) + California (Film & TV Tax Credit Program)

---

## Output Format

For each parameter, provide:
```json
{
  "parameter_name": "...",
  "low": ...,
  "base": ...,
  "high": ...,
  "units": "% or $",
  "assumptions": "...",
  "citations": "...",
  "last_updated": "2025-10-31"
}
```
