'use client';

import React from 'react';

interface GuidelineSummaryProps {
  maxPages?: number;
  requiresAnonymity?: boolean;
  referenceFormat?: string;
}

export const GuidelineSummary: React.FC<GuidelineSummaryProps> = ({
  maxPages,
  requiresAnonymity,
  referenceFormat,
}) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">Conference Guidelines</h3>
      <dl className="space-y-3">
        {maxPages && (
          <div className="flex justify-between">
            <dt className="text-gray-600">Page Limit</dt>
            <dd className="font-semibold">{maxPages} pages</dd>
          </div>
        )}
        {requiresAnonymity !== undefined && (
          <div className="flex justify-between">
            <dt className="text-gray-600">Anonymous</dt>
            <dd className="font-semibold">{requiresAnonymity ? 'Required' : 'Not Required'}</dd>
          </div>
        )}
        {referenceFormat && (
          <div className="flex justify-between">
            <dt className="text-gray-600">Reference Format</dt>
            <dd className="font-semibold uppercase">{referenceFormat}</dd>
          </div>
        )}
      </dl>
    </div>
  );
};
