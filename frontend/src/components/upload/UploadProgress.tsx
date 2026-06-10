'use client';

import React from 'react';

interface UploadProgressProps {
  fileName: string;
  progress?: number;
  status?: 'uploading' | 'processing' | 'complete' | 'error';
}

export const UploadProgress: React.FC<UploadProgressProps> = ({ fileName, progress, status = 'uploading' }) => {
  const statusConfig = {
    uploading: { bg: 'bg-slate-200', fill: 'bg-indigo-500', text: 'Uploading...', color: 'text-indigo-700' },
    processing: { bg: 'bg-slate-200', fill: 'bg-amber-500', text: 'Analyzing...', color: 'text-amber-700' },
    complete: { bg: 'bg-slate-200', fill: 'bg-emerald-500', text: 'Complete', color: 'text-emerald-700' },
    error: { bg: 'bg-slate-200', fill: 'bg-red-500', text: 'Failed', color: 'text-red-700' },
  };

  const cfg = statusConfig[status];
  const pct = progress !== undefined ? progress : status === 'complete' ? 100 : status === 'uploading' ? 45 : 75;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <svg className={`w-4 h-4 flex-shrink-0 ${cfg.color}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="text-sm font-medium text-slate-800 truncate">{fileName}</span>
        </div>
        <span className={`text-xs font-medium ${cfg.color}`}>{cfg.text}</span>
      </div>
      <div className={`w-full h-2 rounded-full ${cfg.bg}`}>
        <div className={`h-2 rounded-full transition-all duration-500 ${cfg.fill}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
};
