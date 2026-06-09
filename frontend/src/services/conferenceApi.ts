import apiClient from './apiClient';
import { Conference } from '@/types/conference';

export const conferenceApi = {
  getConferences: async (): Promise<Conference[]> => {
    const response = await apiClient.get('/api/v1/conferences');
    return response.data;
  },

  getConferenceById: async (conferenceId: string): Promise<Conference> => {
    const response = await apiClient.get(`/api/v1/conferences/${conferenceId}`);
    return response.data;
  },
};
