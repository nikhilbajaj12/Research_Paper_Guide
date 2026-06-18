import apiClient from './apiClient';
import { AutoFixRequest, AutoFixStatusResponse } from '@/types/compliance';

export const autoFixApi = {
  runAutoFix: async (request: AutoFixRequest): Promise<AutoFixStatusResponse> => {
    const response = await apiClient.post('/api/v1/auto-fix/run', request);
    return response.data;
  },

  getStatus: async (pipelineId: string): Promise<AutoFixStatusResponse> => {
    const response = await apiClient.get(`/api/v1/auto-fix/${pipelineId}/status`);
    return response.data;
  },

  getDownloadUrl: (pipelineId: string): string => {
    const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    return `${baseURL}/api/v1/auto-fix/${pipelineId}/download`;
  },
};
