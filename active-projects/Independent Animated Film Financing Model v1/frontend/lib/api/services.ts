import { apiClient } from './client';
import type {
  IncentiveCalculationRequest,
  IncentiveCalculationResponse,
  WaterfallExecutionRequest,
  WaterfallExecutionResponse,
  ScenarioGenerationRequest,
  ScenarioGenerationResponse,
  DealBlockInput,
  DealBlockResponse,
  DealBlockListResponse,
  DealBlockCreateRequest,
  OwnershipScoreRequest,
  OwnershipScoreResponse,
  DealTemplate,
  CapitalProgramInput,
  CapitalProgramResponse,
  CapitalProgramListResponse,
  CapitalSourceInput,
  CapitalSourceResponse,
  AllocationRequestInput,
  AllocationResultResponse,
  PortfolioMetricsResponse,
  ProgramTypesResponse,
} from './types';

// Engine 1: Tax Incentives

export const calculateIncentives = async (
  request: IncentiveCalculationRequest
): Promise<IncentiveCalculationResponse> => {
  const response = await apiClient.post<IncentiveCalculationResponse>(
    '/api/v1/incentives/calculate',
    request
  );
  return response.data;
};

export const getJurisdictions = async (): Promise<string[]> => {
  const response = await apiClient.get<string[]>('/api/v1/incentives/jurisdictions');
  return response.data;
};

export const getJurisdictionPolicies = async (jurisdiction: string): Promise<any[]> => {
  const response = await apiClient.get(
    `/api/v1/incentives/jurisdictions/${encodeURIComponent(jurisdiction)}/policies`
  );
  return response.data;
};

// Engine 2: Waterfall

export const executeWaterfall = async (
  request: WaterfallExecutionRequest
): Promise<WaterfallExecutionResponse> => {
  const response = await apiClient.post<WaterfallExecutionResponse>(
    '/api/v1/waterfall/execute',
    request
  );
  return response.data;
};

// Engine 3: Scenarios

export const generateScenarios = async (
  request: ScenarioGenerationRequest
): Promise<ScenarioGenerationResponse> => {
  const response = await apiClient.post<ScenarioGenerationResponse>(
    '/api/v1/scenarios/generate',
    request
  );
  return response.data;
};

// Health check

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Engine 4: Deal Blocks

export const createDeal = async (
  request: DealBlockCreateRequest
): Promise<DealBlockResponse> => {
  const response = await apiClient.post<DealBlockResponse>(
    '/api/v1/deals',
    request
  );
  return response.data;
};

export const getDeal = async (dealId: string): Promise<DealBlockResponse> => {
  const response = await apiClient.get<DealBlockResponse>(
    `/api/v1/deals/${encodeURIComponent(dealId)}`
  );
  return response.data;
};

export const listDeals = async (): Promise<DealBlockListResponse> => {
  const response = await apiClient.get<DealBlockListResponse>('/api/v1/deals');
  return response.data;
};

export const deleteDeal = async (dealId: string): Promise<void> => {
  await apiClient.delete(`/api/v1/deals/${encodeURIComponent(dealId)}`);
};

export const getDealTemplates = async (): Promise<DealTemplate[]> => {
  const response = await apiClient.get<{ templates: DealTemplate[] }>(
    '/api/v1/deals/templates'
  );
  return response.data.templates;
};

// Engine 4: Ownership Scoring

export const scoreOwnership = async (
  request: OwnershipScoreRequest
): Promise<OwnershipScoreResponse> => {
  const response = await apiClient.post<OwnershipScoreResponse>(
    '/api/v1/ownership/score',
    request
  );
  return response.data;
};

export const getDefaultWeights = async (): Promise<Record<string, number>> => {
  const response = await apiClient.get<Record<string, number>>(
    '/api/v1/ownership/weights'
  );
  return response.data;
};

export const getDimensionInfo = async (): Promise<Record<string, any>> => {
  const response = await apiClient.get('/api/v1/ownership/dimensions');
  return response.data;
};

// Engine 5: Capital Programs

export const createCapitalProgram = async (
  request: CapitalProgramInput
): Promise<CapitalProgramResponse> => {
  const response = await apiClient.post<CapitalProgramResponse>(
    '/api/v1/capital-programs',
    request
  );
  return response.data;
};

export const getCapitalProgram = async (
  programId: string
): Promise<CapitalProgramResponse> => {
  const response = await apiClient.get<CapitalProgramResponse>(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}`
  );
  return response.data;
};

export const listCapitalPrograms = async (
  programType?: string,
  status?: string
): Promise<CapitalProgramListResponse> => {
  const params = new URLSearchParams();
  if (programType) params.append('program_type', programType);
  if (status) params.append('status', status);
  const queryString = params.toString();
  const url = queryString
    ? `/api/v1/capital-programs?${queryString}`
    : '/api/v1/capital-programs';
  const response = await apiClient.get<CapitalProgramListResponse>(url);
  return response.data;
};

export const deleteCapitalProgram = async (programId: string): Promise<void> => {
  await apiClient.delete(`/api/v1/capital-programs/${encodeURIComponent(programId)}`);
};

export const getProgramTypes = async (): Promise<ProgramTypesResponse> => {
  const response = await apiClient.get<ProgramTypesResponse>(
    '/api/v1/capital-programs/types'
  );
  return response.data;
};

export const addCapitalSource = async (
  programId: string,
  source: CapitalSourceInput
): Promise<CapitalSourceResponse> => {
  const response = await apiClient.post<CapitalSourceResponse>(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/sources`,
    source
  );
  return response.data;
};

export const removeCapitalSource = async (
  programId: string,
  sourceId: string
): Promise<void> => {
  await apiClient.delete(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/sources/${encodeURIComponent(sourceId)}`
  );
};

export const allocateCapital = async (
  programId: string,
  allocation: AllocationRequestInput
): Promise<AllocationResultResponse> => {
  const response = await apiClient.post<AllocationResultResponse>(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/allocate`,
    allocation
  );
  return response.data;
};

export const fundDeployment = async (
  programId: string,
  deploymentId: string,
  amount?: number
): Promise<any> => {
  const response = await apiClient.post(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/deployments/${encodeURIComponent(deploymentId)}/fund`,
    amount ? { amount } : {}
  );
  return response.data;
};

export const recordRecoupment = async (
  programId: string,
  deploymentId: string,
  recoupedAmount: number,
  profitAmount: number = 0
): Promise<any> => {
  const response = await apiClient.post(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/deployments/${encodeURIComponent(deploymentId)}/recoup`,
    { recouped_amount: recoupedAmount, profit_amount: profitAmount }
  );
  return response.data;
};

export const getPortfolioMetrics = async (
  programId: string
): Promise<PortfolioMetricsResponse> => {
  const response = await apiClient.get<PortfolioMetricsResponse>(
    `/api/v1/capital-programs/${encodeURIComponent(programId)}/metrics`
  );
  return response.data;
};
