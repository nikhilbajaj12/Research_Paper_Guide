'use client';

import React from 'react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { RecommendationDetail } from '@/types/compliance';

interface RecommendationsPanelProps {
  recommendations: RecommendationDetail[];
}

const severityVariant = (severity: string): 'success' | 'warning' | 'error' | 'info' => {
  if (severity === 'critical') return 'error';
  if (severity === 'warning') return 'warning';
  return 'info';
};

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Card>
      <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Recommendations
      </h2>
      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <div key={index} className="rounded-lg border border-slate-200 p-4 hover:border-indigo-200 transition-colors">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="text-sm font-semibold text-slate-800">{rec.issue || rec.suggested_action}</h3>
              <Badge text={rec.severity} variant={severityVariant(rec.severity)} />
            </div>
            <div className="space-y-1 text-sm text-slate-600">
              {rec.suggested_action && (
                <p><span className="font-medium text-slate-700">Suggested action:</span> {rec.suggested_action}</p>
              )}
              {rec.explanation && (
                <p><span className="font-medium text-slate-700">Explanation:</span> {rec.explanation}</p>
              )}
              {rec.location && (
                <p><span className="font-medium text-slate-700">Affected section:</span> {rec.location}</p>
              )}
              {rec.category && (
                <p><span className="font-medium text-slate-700">Category:</span> {rec.category.replace(/_/g, ' ')}</p>
              )}
            </div>
            <div className="mt-2 flex items-center gap-2">
              <Badge
                text={rec.can_auto_fix ? 'Auto-fixable' : 'Manual fix'}
                variant={rec.can_auto_fix ? 'success' : 'warning'}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
