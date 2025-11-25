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
