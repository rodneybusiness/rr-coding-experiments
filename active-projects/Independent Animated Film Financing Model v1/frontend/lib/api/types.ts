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
