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

// Engine 5: Capital Programs

export type ProgramType =
  | 'internal_pool'
  | 'external_fund'
  | 'private_equity'
  | 'family_office'
  | 'output_deal'
  | 'first_look'
  | 'overhead_deal'
  | 'spv'
  | 'tax_credit_fund'
  | 'international_copro'
  | 'government_fund';

export type ProgramStatus =
  | 'prospective'
  | 'in_negotiation'
  | 'active'
  | 'fully_deployed'
  | 'winding_down'
  | 'closed';

export type AllocationStatus =
  | 'pending'
  | 'approved'
  | 'committed'
  | 'funded'
  | 'recouped'
  | 'written_off';

export interface CapitalSourceInput {
  source_name: string;
  source_type?: string;
  committed_amount: number;
  drawn_amount?: number;
  currency?: string;
  interest_rate?: number;
  management_fee_pct?: number;
  carry_percentage?: number;
  hurdle_rate?: number;
  geographic_restrictions?: string[];
  genre_restrictions?: string[];
  budget_range_min?: number;
  budget_range_max?: number;
  commitment_date?: string;
  expiry_date?: string;
  notes?: string;
}

export interface CapitalSourceResponse {
  source_id: string;
  source_name: string;
  source_type: string;
  committed_amount: number;
  drawn_amount: number;
  available_amount: number;
  utilization_rate: number;
  currency: string;
  interest_rate?: number;
  management_fee_pct?: number;
  carry_percentage?: number;
  hurdle_rate?: number;
  geographic_restrictions: string[];
  genre_restrictions: string[];
  budget_range_min?: number;
  budget_range_max?: number;
  commitment_date?: string;
  expiry_date?: string;
  notes?: string;
}

export interface CapitalProgramConstraintsInput {
  max_single_project_pct?: number;
  max_single_counterparty_pct?: number;
  min_project_budget?: number;
  max_project_budget?: number;
  required_jurisdictions?: string[];
  prohibited_jurisdictions?: string[];
  required_genres?: string[];
  prohibited_genres?: string[];
  prohibited_ratings?: string[];
  target_num_projects?: number;
  target_avg_budget?: number;
  target_portfolio_irr?: number;
  target_multiple?: number;
  max_development_pct?: number;
  max_first_time_director_pct?: number;
  target_deployment_years?: number;
  min_reserve_pct?: number;
}

export interface CapitalProgramInput {
  program_name: string;
  program_type: ProgramType;
  description?: string;
  target_size: number;
  currency?: string;
  sources?: CapitalSourceInput[];
  constraints?: CapitalProgramConstraintsInput;
  manager_name?: string;
  management_fee_pct?: number;
  carry_percentage?: number;
  hurdle_rate?: number;
  vintage_year?: number;
  investment_period_years?: number;
  fund_term_years?: number;
  extension_years?: number;
  formation_date?: string;
  first_close_date?: string;
  final_close_date?: string;
  notes?: string;
}

export interface CapitalDeploymentResponse {
  deployment_id: string;
  program_id: string;
  source_id?: string;
  project_id: string;
  project_name: string;
  allocated_amount: number;
  funded_amount: number;
  recouped_amount: number;
  profit_distributed: number;
  outstanding_amount: number;
  total_return: number;
  multiple?: number;
  currency: string;
  status: AllocationStatus;
  equity_percentage?: number;
  recoupment_priority: number;
  backend_participation_pct?: number;
  allocation_date: string;
  funding_date?: string;
  expected_recoupment_date?: string;
  notes?: string;
}

export interface CapitalProgramMetrics {
  total_committed: number;
  total_drawn: number;
  total_available: number;
  total_allocated: number;
  total_funded: number;
  total_recouped: number;
  total_profit: number;
  commitment_progress: number;
  deployment_rate: number;
  num_active_projects: number;
  portfolio_multiple?: number;
  reserve_amount: number;
  deployable_capital: number;
}

export interface CapitalProgramResponse {
  program_id: string;
  program_name: string;
  program_type: ProgramType;
  status: ProgramStatus;
  description?: string;
  target_size: number;
  currency: string;
  sources: CapitalSourceResponse[];
  deployments: CapitalDeploymentResponse[];
  constraints: Record<string, any>;
  manager_name?: string;
  management_fee_pct?: number;
  carry_percentage?: number;
  hurdle_rate?: number;
  vintage_year?: number;
  investment_period_years: number;
  fund_term_years: number;
  extension_years: number;
  formation_date?: string;
  first_close_date?: string;
  final_close_date?: string;
  notes?: string;
  metrics: CapitalProgramMetrics;
}

export interface CapitalProgramListResponse {
  programs: CapitalProgramResponse[];
  total_count: number;
}

export interface AllocationRequestInput {
  project_id: string;
  project_name: string;
  requested_amount: number;
  project_budget: number;
  jurisdiction?: string;
  genre?: string;
  rating?: string;
  is_development?: boolean;
  is_first_time_director?: boolean;
  counterparty_name?: string;
  equity_percentage?: number;
  recoupment_priority?: number;
  backend_participation_pct?: number;
  source_id?: string;
}

export interface ConstraintViolation {
  constraint_name: string;
  constraint_type: string;
  current_value: string;
  limit_value: string;
  description: string;
  is_blocking: boolean;
}

export interface AllocationResultResponse {
  success: boolean;
  allocation_id?: string;
  deployment?: CapitalDeploymentResponse;
  violations: ConstraintViolation[];
  warnings: string[];
  selected_source_id?: string;
  source_selection_reason?: string;
  recommendations: string[];
}

export interface PortfolioMetricsResponse {
  size_metrics: Record<string, any>;
  project_metrics: Record<string, any>;
  concentration_metrics: Record<string, any>;
  performance_metrics: Record<string, any>;
  risk_metrics: Record<string, any>;
  constraint_compliance: Record<string, any>;
}

export interface ProgramTypeInfo {
  type: string;
  label: string;
  description: string;
}

export interface ProgramTypesResponse {
  types: ProgramTypeInfo[];
}

// Project Profile Types

export interface ProjectProfileInput {
  project_name: string;
  project_budget: number;
  genre?: string;
  jurisdiction?: string;
  rating?: string;
  is_development?: boolean;
  is_first_time_director?: boolean;
  expected_revenue?: number;
  production_start_date?: string;
  expected_release_date?: string;
  description?: string;
  notes?: string;
}

export interface ProjectProfileResponse {
  project_id: string;
  project_name: string;
  project_budget: number;
  genre?: string;
  jurisdiction?: string;
  rating?: string;
  is_development: boolean;
  is_first_time_director: boolean;
  expected_revenue?: number;
  production_start_date?: string;
  expected_release_date?: string;
  description?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  capital_deployments: CapitalDeploymentResponse[];
  total_funding: number;
  funding_gap: number;
}

export interface ProjectListResponse {
  projects: ProjectProfileResponse[];
  total_count: number;
}

// Dashboard Types

export interface DashboardMetrics {
  total_projects: number;
  total_budget: number;
  total_tax_incentives: number;
  average_capture_rate: number;
  scenarios_generated: number;
  active_capital_programs: number;
  total_committed_capital: number;
  total_deployed_capital: number;
  projects_in_development: number;
  projects_in_production: number;
}

export interface RecentActivity {
  project: string;
  action: string;
  time: string;
  activity_type: 'scenario' | 'incentive' | 'waterfall' | 'deal' | 'capital' | 'project';
}

export interface DashboardResponse {
  metrics: DashboardMetrics;
  recent_activity: RecentActivity[];
}
