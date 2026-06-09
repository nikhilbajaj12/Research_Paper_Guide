'use client';

import React from 'react';
import { Badge } from '@/components/common/Badge';

interface ComplianceScoreProps {
  score: number;
  status: string;
  totalIssues: number;
}

const statusBadgeVariant = (status: string): 'success' | 'warning' | 'error' | 'info' => {
  if (status === 'submission_ready') return 'success';
  if (status === 'needs_minor_fixes') return 'warning';
  if (status === 'needs_major_fixes') return 'error';
  return 'error';
};

export const ComplianceScore: React.FC<ComplianceScoreProps> = ({ score, status, totalIssues }) => {
  return (
    <div className="bg-white p-8 rounded-lg shadow mb-8">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-gray-600 text-sm mb-1">Score</p>
          <p className="text-4xl font-bold text-blue-600">{score}/100</p>
        </div>
        <div>
          <p className="text-gray-600 text-sm mb-1">Status</p>
          <Badge text={status.replace(/_/g, ' ')} variant={statusBadgeVariant(status)} />
        </div>
        <div>
          <p className="text-gray-600 text-sm mb-1">Issues</p>
          <p className="text-2xl font-bold">{totalIssues}</p>
        </div>
      </div>
    </div>
  );
};
