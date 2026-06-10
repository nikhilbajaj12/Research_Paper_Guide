'use client';

import React from 'react';
import { Card } from '@/components/common/Card';

interface StatsPreviewProps {
  score?: number | null;
  criticalCount?: number;
  warningCount?: number;
  passedCount?: number;
  hasReport?: boolean;
}

export const StatsPreview: React.FC<StatsPreviewProps> = ({
  score = null,
  criticalCount = 0,
  warningCount = 0,
  passedCount = 0,
  hasReport = false,
}) => {
  const items = [
    {
      label: 'Readiness Score',
      value: score !== null ? `${score}/100` : '--',
      color: score !== null && score >= 80 ? 'text-green-600' : score !== null && score >= 50 ? 'text-amber-600' : 'text-slate-400',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      label: 'Critical Issues',
      value: hasReport ? criticalCount : '0',
      color: criticalCount > 0 ? 'text-red-600' : 'text-slate-400',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
    },
    {
      label: 'Warnings',
      value: hasReport ? warningCount : '0',
      color: warningCount > 0 ? 'text-amber-600' : 'text-slate-400',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: 'Passed Checks',
      value: hasReport ? passedCount : '0',
      color: 'text-green-600',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ];

  return (
    <Card>
      <h2 className="text-lg font-bold text-slate-900 mb-5">Compliance Overview</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
            <div className="text-slate-400">{item.icon}</div>
            <div>
              <p className="text-xs text-slate-500">{item.label}</p>
              <p className={`text-xl font-bold ${item.color}`}>{item.value}</p>
            </div>
          </div>
        ))}
      </div>
      {!hasReport && (
        <p className="text-xs text-slate-400 mt-4 text-center">Waiting for paper upload</p>
      )}
    </Card>
  );
};
