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

  getConfigList: async (): Promise<{ conference_id: string; conference_name: string; conference_year: number }[]> => {
    const response = await apiClient.get('/api/v1/conferences/configs/list');
    return response.data;
  },

  getConfigDetail: async (conferenceId: string): Promise<{
    conference_id: string;
    conference_name: string;
    conference_year: number;
    max_pages: number;
    blind_review: boolean;
    reference_style: string;
    required_sections: string[];
    package_template: string;
  } | null> => {
    try {
      const response = await apiClient.get(`/api/v1/conferences/${conferenceId}`);
      const conf: Conference = response.data;
      return {
        conference_id: conf.id,
        conference_name: conf.name,
        conference_year: conf.start_date ? parseInt(conf.start_date.slice(0, 4)) : 2026,
        max_pages: conf.max_pages || conf.guidelines?.max_pages || 9,
        blind_review: conf.requires_anonymity ?? conf.guidelines?.requires_anonymity ?? true,
        reference_style: conf.reference_format || conf.guidelines?.reference_format || 'bibtex',
        required_sections: [],
        package_template: conf.id?.split('-')[0] || 'neurips',
      };
    } catch {
      return null;
    }
  },
};
