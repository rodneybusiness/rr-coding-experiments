import { apiClient } from './client';
import type {
  IncentiveCalculationRequest,
  IncentiveCalculationResponse,
  WaterfallExecutionRequest,
  WaterfallExecutionResponse,
  ScenarioGenerationRequest,
  ScenarioGenerationResponse,
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
