'use client';

import React from 'react';
import { Badge } from '@/components/common/Badge';
import { ComplianceIssue } from '@/types/compliance';

interface IssueCardProps {
  issue: ComplianceIssue;
}

const severityVariant = (severity: string): 'error' | 'warning' | 'info' => {
  if (severity === 'critical') return 'error';
  if (severity === 'warning') return 'warning';
  return 'info';
};

export const IssueCard: React.FC<IssueCardProps> = ({ issue }) => {
  return (
    <div className="mb-4 p-4 border border-gray-300 rounded">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-lg capitalize">{issue.category.replace(/_/g, ' ')}</h4>
        <Badge text={issue.severity} variant={severityVariant(issue.severity)} />
      </div>
      <p className="text-gray-700 mb-2">{issue.message}</p>
      {issue.location && <p className="text-sm text-gray-500 mb-1">Location: {issue.location}</p>}
      {issue.suggested_fix && (
        <p className="text-sm text-gray-600"><strong>Fix:</strong> {issue.suggested_fix}</p>
      )}
      {issue.needs_verification && (
        <p className="text-sm text-yellow-600 mt-1"><em>Requires manual verification</em></p>
      )}
    </div>
  );
};
