// Engine 1: Tax Incentives

export interface JurisdictionSpendInput {
  jurisdiction: string;
  qualified_spend: number;
  labor_spend: number;
}

export interface IncentiveCalculationRequest {
  project_id: string;
  project_name: string;
  total_budget: number;
  jurisdiction_spends: JurisdictionSpendInput[];
}

export interface PolicyCredit {
  policy_id: string;
  name: string;
  credit_amount: number;
  credit_rate: number;
  qualified_base: number;
}

export interface JurisdictionBreakdown {
  jurisdiction: string;
  gross_credit: number;
  net_benefit: number;
  effective_rate: number;
  policies: PolicyCredit[];
}

export interface CashFlowQuarter {
  quarter: number;
  amount: number;
}

export interface IncentiveCalculationResponse {
  project_id: string;
  project_name: string;
  total_budget: number;
  total_gross_credit: number;
  total_net_benefit: number;
  effective_rate: number;
  jurisdiction_breakdown: JurisdictionBreakdown[];
  cash_flow_projection: CashFlowQuarter[];
  monetization_options: {
    direct_receipt: number;
    bank_loan: number;
    broker_sale: number;
  };
}

// Engine 2: Waterfall

export interface WaterfallExecutionRequest {
  project_id: string;
  capital_stack_id: string;
  waterfall_id: string;
  total_revenue: number;
  release_strategy: string;
  run_monte_carlo: boolean;
  monte_carlo_iterations: number;
}

export interface StakeholderReturn {
  stakeholder_id: string;
  stakeholder_name: string;
  stakeholder_type: string;
  invested: number;
  received: number;
  profit: number;
  cash_on_cash: number | null;
  irr: number | null;
}

export interface QuarterlyDistribution {
  quarter: number;
  distributions: Record<string, number>;
}

export interface RevenueWindow {
  window: string;
  revenue: number;
  percentage: number;
}

export interface MonteCarloPercentiles {
  p10: number;
  p50: number;
  p90: number;
}

export interface MonteCarloResults {
  equity_irr: MonteCarloPercentiles;
  probability_of_recoupment: Record<string, number>;
}

export interface WaterfallExecutionResponse {
  project_id: string;
  total_revenue: number;
  total_distributed: number;
  total_recouped: number;
  stakeholder_returns: StakeholderReturn[];
  distribution_timeline: QuarterlyDistribution[];
  revenue_by_window: RevenueWindow[];
  monte_carlo_results: MonteCarloResults | null;
}

// Engine 3: Scenarios

export interface ObjectiveWeights {
  equity_irr: number;
  cost_of_capital: number;
  tax_incentive_capture: number;
  risk_minimization: number;
}

export interface ScenarioGenerationRequest {
  project_id: string;
  project_name: string;
  project_budget: number;
  waterfall_id: string;
  objective_weights?: ObjectiveWeights;
  num_scenarios: number;
}

export interface CapitalStructure {
  senior_debt: number;
  gap_financing: number;
  mezzanine_debt: number;
  equity: number;
  tax_incentives: number;
  presales: number;
  grants: number;
}

export interface ScenarioMetrics {
  equity_irr: number;
  cost_of_capital: number;
  tax_incentive_rate: number;
  risk_score: number;
  debt_coverage_ratio: number;
  probability_of_recoupment: number;
  total_debt: number;
  total_equity: number;
  debt_to_equity_ratio: number | null;
}

export interface Scenario {
  scenario_id: string;
  scenario_name: string;
  optimization_score: number;
  capital_structure: CapitalStructure;
  metrics: ScenarioMetrics;
  strengths: string[];
  weaknesses: string[];
  validation_passed: boolean;
  validation_errors: string[];
}

export interface ScenarioGenerationResponse {
  project_id: string;
  project_name: string;
  project_budget: number;
  scenarios: Scenario[];
  best_scenario_id: string;
}

// Engine 4: Deal Blocks & Ownership Scoring

export interface DealBlockInput {
  deal_name: string;
  deal_type: string;
  status?: string;
  counterparty_name: string;
  counterparty_type?: string;
  amount: number;
  currency?: string;
  recoupment_priority?: number;
  is_recoupable?: boolean;
  interest_rate?: number;
  premium_percentage?: number;
  backend_participation_pct?: number;
  origination_fee_pct?: number;
  distribution_fee_pct?: number;
  sales_commission_pct?: number;
  territories?: string[];
  is_worldwide?: boolean;
  rights_windows?: string[];
  term_years?: number;
  exclusivity?: boolean;
  holdback_days?: number;
  ownership_percentage?: number;
  approval_rights_granted?: string[];
  has_board_seat?: boolean;
  has_veto_rights?: boolean;
  veto_scope?: string;
  ip_ownership?: string;
  mfn_clause?: boolean;
  mfn_scope?: string;
  reversion_trigger_years?: number;
  reversion_trigger_condition?: string;
  sequel_rights_holder?: string;
  sequel_participation_pct?: number;
  cross_collateralized?: boolean;
  cross_collateral_scope?: string;
  probability_of_closing?: number;
  complexity_score?: number;
  notes?: string;
}

export interface DealBlockResponse {
  deal_id: string;
  deal_name: string;
  deal_type: string;
  status: string;
  counterparty_name: string;
  counterparty_type: string;
  amount: number;
  currency: string;
  net_amount: number;
  expected_value: number;
  control_impact_score: number;
  ownership_impact_score: number;
  optionality_score: number;
  territories: string[];
  rights_windows: string[];
  term_years: number | null;
  mfn_clause: boolean;
  probability_of_closing: number;
  complexity_score: number;
}

export interface DealBlockListResponse {
  deals: DealBlockResponse[];
  total_count: number;
}

export interface DealBlockCreateRequest {
  project_id: string;
  deal: DealBlockInput;
}

// Ownership Scoring

export interface ScoreWeights {
  ownership: number;
  control: number;
  optionality: number;
  friction: number;
}

export interface ControlImpact {
  source: string;
  dimension: string;
  impact: number;
  explanation: string;
}

export interface ScoringFlags {
  has_mfn_risk: boolean;
  has_control_concentration: boolean;
  has_reversion_opportunity: boolean;
}

export interface OwnershipScoreRequest {
  deal_blocks: DealBlockInput[];
  weights?: ScoreWeights;
}

export interface OwnershipScoreResponse {
  ownership_score: number;
  control_score: number;
  optionality_score: number;
  friction_score: number;
  composite_score: number;
  impacts: ControlImpact[];
  deal_impacts: Record<string, Record<string, number>>;
  recommendations: string[];
  flags: ScoringFlags;
}

export interface DealTemplate {
  template_name: string;
  deal_type: string;
  description: string;
  default_values: Record<string, any>;
}
