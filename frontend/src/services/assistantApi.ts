import apiClient from './apiClient';
import { AssistantChatRequest, AssistantChatResponse } from '@/types/compliance';

export const assistantApi = {
  chat: async (request: AssistantChatRequest): Promise<AssistantChatResponse> => {
    const response = await apiClient.post('/api/v1/assistant/chat', request);
    return response.data;
  },
};
