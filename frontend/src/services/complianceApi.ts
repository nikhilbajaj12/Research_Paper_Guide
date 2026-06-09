import apiClient from './apiClient';
import { ComplianceReport } from '@/types/compliance';

export const complianceApi = {
  analyzeCompliance: async (paperId: string, conferenceId: string): Promise<ComplianceReport> => {
    const response = await apiClient.post('/api/v1/compliance/analyze', {
      paper_id: paperId,
      conference_id: conferenceId,
    });
    return response.data;
  },
};
