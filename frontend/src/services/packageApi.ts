import apiClient from './apiClient';
import { Package } from '@/types/package';

export const packageApi = {
  generatePackage: async (paperId: string, conferenceId: string, projectId?: string): Promise<Package> => {
    const response = await apiClient.post('/api/v1/packages/generate', {
      paper_id: paperId,
      conference_id: conferenceId,
      project_id: projectId,
      package_type: 'neurips_overleaf',
    });
    return response.data;
  },

  downloadPackage: async (packageId: string): Promise<Blob> => {
    const response = await apiClient.get(`/api/v1/packages/${packageId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
