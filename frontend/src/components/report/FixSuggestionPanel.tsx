'use client';

import React from 'react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { FixSuggestion } from '@/types/compliance';

interface FixSuggestionPanelProps {
  suggestions: FixSuggestion[];
}

export const FixSuggestionPanel: React.FC<FixSuggestionPanelProps> = ({ suggestions }) => {
  if (suggestions.length === 0) return null;

  return (
    <Card>
      <h2 className="text-lg font-bold text-slate-900 mb-4">Fix Suggestions</h2>
      <div className="space-y-3">
        {suggestions.map((s) => (
          <div key={s.issue_id} className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-sm font-medium text-slate-800">{s.suggested_action}</p>
              <Badge text={s.can_auto_fix ? 'Auto-fixable' : 'Manual'} variant={s.can_auto_fix ? 'success' : 'warning'} />
            </div>
            <p className="text-xs text-slate-500">{s.explanation}</p>
          </div>
        ))}
      </div>
    </Card>
  );
};
