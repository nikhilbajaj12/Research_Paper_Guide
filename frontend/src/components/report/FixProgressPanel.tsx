'use client';

import React from 'react';
import { Card } from '@/components/common/Card';
import { Loader } from '@/components/common/Loader';
import { Button } from '@/components/common/Button';
import { FixStep, AgentResult, BeforeAfterScore } from '@/types/compliance';
import { BeforeAfterComparison } from './BeforeAfterComparison';

interface FixProgressPanelProps {
  running: boolean;
  progress: number;
  steps: FixStep[];
  agentResults: AgentResult[];
  scoreComparison?: BeforeAfterScore | null;
  packageDownloadUrl?: string | null;
  error?: string | null;
  onStartFix: (command: string) => void;
  onReset: () => void;
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  pending: <span className="w-4 h-4 rounded-full border-2 border-slate-300 inline-block" />,
  running: <span className="w-4 h-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin inline-block" />,
  completed: (
    <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  failed: (
    <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
};

const FIX_COMMANDS = [
  { label: 'Fix All Issues', command: 'Fix all issues' },
  { label: 'Make ACL Ready', command: 'Make this ACL ready' },
  { label: 'Fix Anonymity', command: 'Fix anonymity issues' },
  { label: 'Fix Citations', command: 'Fix citation issues' },
  { label: 'Create Missing Sections', command: 'Create missing sections' },
  { label: 'Generate Package', command: 'Generate submission package' },
];

export const FixProgressPanel: React.FC<FixProgressPanelProps> = ({
  running,
  progress,
  steps,
  agentResults,
  scoreComparison,
  packageDownloadUrl,
  error,
  onStartFix,
  onReset,
}) => {
  return (
    <Card padding="sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Auto-Fix Pipeline
        </h3>
        {!running && steps.length === 0 && (
          <Button onClick={onReset} variant="ghost" size="sm">
            Clear
          </Button>
        )}
      </div>

      {running && (
        <div className="mb-3">
          <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
            <Loader />
            <span>Fixing your paper... {progress}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-1.5">
            <div className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm mb-3">
          {error}
        </div>
      )}

      {steps.length > 0 && (
        <div className="space-y-1.5 mb-3">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Execution Plan</p>
          {steps.map((step) => (
            <div key={step.step_id} className="flex items-center gap-2 text-sm">
              {STATUS_ICONS[step.status] || STATUS_ICONS.pending}
              <span className={`${step.status === 'failed' ? 'text-red-600' : step.status === 'completed' ? 'text-slate-500' : 'text-slate-700'}`}>
                {step.action}
              </span>
            </div>
          ))}
        </div>
      )}

      {agentResults.length > 0 && (
        <div className="space-y-1.5 mb-3">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Changes Applied</p>
          {agentResults.map((ar, i) => (
            <div key={i} className="text-sm">
              <p className={`font-medium ${ar.success ? 'text-emerald-700' : 'text-red-700'}`}>
                {ar.agent.replace(/_/g, ' ')}: {ar.success ? `${ar.changes_made.length} change(s)` : 'Failed'}
              </p>
              {ar.changes_made.length > 0 && (
                <ul className="ml-4 text-xs text-slate-500 list-disc">
                  {ar.changes_made.map((c, j) => <li key={j}>{c}</li>)}
                </ul>
              )}
              {ar.error && <p className="text-xs text-red-500 ml-4">{ar.error}</p>}
            </div>
          ))}
        </div>
      )}

      {scoreComparison && <BeforeAfterComparison comparison={scoreComparison} />}

      {packageDownloadUrl && (
        <div className="mt-3">
          <a
            href={packageDownloadUrl}
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Fixed Package
          </a>
        </div>
      )}

      {!running && steps.length === 0 && (
        <div className="space-y-2">
          <p className="text-xs text-slate-500">Run automatic fixes for your paper:</p>
          <div className="flex flex-wrap gap-1.5">
            {FIX_COMMANDS.map((cmd) => (
              <button
                key={cmd.command}
                onClick={() => onStartFix(cmd.command)}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors"
              >
                {cmd.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
};
