'use client';

import { useState, useCallback } from 'react';
import { AutoFixStatusResponse, FixPipelineResult } from '@/types/compliance';
import { autoFixApi } from '@/services/autoFixApi';

interface UseAutoFixReturn {
  running: boolean;
  progress: number;
  result: FixPipelineResult | null;
  error: string | null;
  startFix: (paperId: string, conferenceId: string, command: string) => Promise<void>;
  reset: () => void;
}

export function useAutoFix(): UseAutoFixReturn {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<FixPipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startFix = useCallback(async (paperId: string, conferenceId: string, command: string) => {
    setRunning(true);
    setProgress(0);
    setResult(null);
    setError(null);

    try {
      const response = await autoFixApi.runAutoFix({
        paper_id: paperId,
        conference_id: conferenceId,
        command,
      });

      setProgress(response.progress);
      if (response.result) {
        setResult(response.result);
      }
      if (response.status === 'failed') {
        setError(response.result?.error || 'Auto-fix failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to run auto-fix');
    } finally {
      setRunning(false);
    }
  }, []);

  const reset = useCallback(() => {
    setRunning(false);
    setProgress(0);
    setResult(null);
    setError(null);
  }, []);

  return { running, progress, result, error, startFix, reset };
}
