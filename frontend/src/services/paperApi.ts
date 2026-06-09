import apiClient from './apiClient';

export const paperApi = {
  uploadPaper: async (file: File, conferenceId: string): Promise<{paper_id: string; file_name: string; file_size: number}> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('conference_id', conferenceId);
    
    const response = await apiClient.post('/api/v1/papers/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
