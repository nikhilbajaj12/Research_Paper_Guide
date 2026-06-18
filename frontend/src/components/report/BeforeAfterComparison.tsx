'use client';

import React from 'react';
import { Card } from '@/components/common/Card';
import { BeforeAfterScore } from '@/types/compliance';

interface BeforeAfterComparisonProps {
  comparison: BeforeAfterScore;
}

export const BeforeAfterComparison: React.FC<BeforeAfterComparisonProps> = ({ comparison }) => {
  const improved = comparison.improvement > 0;

  return (
    <Card padding="sm">
      <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Score Improvement
      </h3>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-xs text-slate-500 mb-1">Before</p>
          <p className={`text-2xl font-bold ${comparison.before_score >= 80 ? 'text-emerald-600' : comparison.before_score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {comparison.before_score}
          </p>
          <p className="text-xs text-slate-400 capitalize">{comparison.before_status.replace(/_/g, ' ')}</p>
        </div>
        <div className="flex items-center justify-center">
          <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
            improved ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
          }`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={improved ? 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' : 'M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6'} />
            </svg>
            {improved ? '+' : ''}{comparison.improvement}
          </div>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-1">After</p>
          <p className={`text-2xl font-bold ${comparison.after_score >= 80 ? 'text-emerald-600' : comparison.after_score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {comparison.after_score}
          </p>
          <p className="text-xs text-slate-400 capitalize">{comparison.after_status.replace(/_/g, ' ')}</p>
        </div>
      </div>
      <div className="mt-3 w-full bg-slate-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-700 ${improved ? 'bg-emerald-500' : 'bg-red-500'}`}
          style={{ width: `${Math.min(100, (comparison.after_score / 100) * 100)}%` }}
        />
      </div>
    </Card>
  );
};
