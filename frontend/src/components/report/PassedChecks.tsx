'use client';

import React from 'react';
import { Badge } from '@/components/common/Badge';
import { EmptyState } from '@/components/common/EmptyState';

interface PassedChecksProps {
  checks: string[];
}

export const PassedChecks: React.FC<PassedChecksProps> = ({ checks }) => {
  if (checks.length === 0) return null;

  return (
    <div className="bg-white p-8 rounded-lg shadow mb-8 border-l-4 border-green-600">
      <h2 className="text-2xl font-bold mb-4 text-green-600">Passed Checks</h2>
      <div className="flex flex-wrap gap-2">
        {checks.map((check) => (
          <Badge key={check} text={check.replace(/_/g, ' ')} variant="success" />
        ))}
      </div>
    </div>
  );
};
