'use client';

import React from 'react';
import { IssueCard } from './IssueCard';
import { ComplianceIssue } from '@/types/compliance';
import { EmptyState } from '@/components/common/EmptyState';

interface IssueListProps {
  issues: ComplianceIssue[];
  title: string;
  severity: 'critical' | 'warning' | 'info';
  borderColor: string;
  textColor: string;
}

export const IssueList: React.FC<IssueListProps> = ({ issues, title, borderColor, textColor }) => {
  const filtered = issues.filter((i) => i.severity === severity);
  if (filtered.length === 0) return null;

  return (
    <div className={`bg-white p-8 rounded-lg shadow mb-8 border-l-4 ${borderColor}`}>
      <h2 className={`text-2xl font-bold mb-4 ${textColor}`}>
        {title} ({filtered.length})
      </h2>
      {filtered.map((issue) => (
        <IssueCard key={issue.issue_id} issue={issue} />
      ))}
    </div>
  );
};
