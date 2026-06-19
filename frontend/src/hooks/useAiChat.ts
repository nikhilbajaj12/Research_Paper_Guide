'use client';

import { useState, useCallback, useRef } from 'react';
import { AssistantMessage, ComplianceReport, AssistantChatRequest, AssistantChatResponse } from '@/types/compliance';
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

export function useAiChat() {
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFixResponse, setLastFixResponse] = useState<AssistantChatResponse | null>(null);
  const reportRef = useRef<ComplianceReport | null>(null);

  const setReport = useCallback((report: ComplianceReport) => {
    reportRef.current = report;
  }, []);

  const sendMessage = useCallback(async (userMessage: string) => {
    const report = reportRef.current;
    if (!report) return;

    const userMsg = createMessage('user', userMessage);
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const request: AssistantChatRequest = {
        conference: { id: report.conference_id },
        compliance_score: report.readiness_score,
        critical_issues: report.issues.filter(i => i.severity === 'critical'),
        warnings: report.issues.filter(i => i.severity === 'warning'),
        passed_checks: report.passed_checks,
        recommendations: report.recommendations || [],
        user_message: userMessage,
        paper_id: report.paper_id,
        conference_id: report.conference_id,
      };

      const response = await assistantApi.chat(request);
      const assistantMsg = createMessage('assistant', response.answer);
      setMessages(prev => [...prev, assistantMsg]);

      if (response.fix_run) {
        setLastFixResponse(response);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to get response from assistant');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setLastFixResponse(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearMessages,
    setReport,
    lastFixResponse,
  };
}
