'use client';

import { useState, useCallback } from 'react';
import { AssistantMessage, AssistantChatRequest } from '@/types/compliance';
import { assistantApi } from '@/services/assistantApi';

let messageCounter = 0;

function createMessage(role: 'user' | 'assistant', content: string): AssistantMessage {
  return {
    id: `msg_${++messageCounter}`,
    role,
    content,
    timestamp: Date.now(),
  };
}

export function useFloatingChat() {
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (userMessage: string) => {
    const userMsg = createMessage('user', userMessage);
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      // Try to get report context from localStorage if available
      let reportContext: any = null;
      try {
        const stored = localStorage.getItem('complianceReport');
        if (stored) reportContext = JSON.parse(stored);
      } catch {}

      const request: AssistantChatRequest = {
        conference: reportContext ? { id: reportContext.conference_id } : { id: 'neurips-2025' },
        compliance_score: reportContext?.readiness_score ?? 0,
        critical_issues: reportContext?.issues?.filter((i: any) => i.severity === 'critical') ?? [],
        warnings: reportContext?.issues?.filter((i: any) => i.severity === 'warning') ?? [],
        passed_checks: reportContext?.passed_checks ?? [],
        recommendations: reportContext?.recommendations ?? [],
        user_message: userMessage,
      };

      const response = await assistantApi.chat(request);
      const assistantMsg = createMessage('assistant', response.answer);
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'Failed to get response from assistant');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearMessages,
  };
}