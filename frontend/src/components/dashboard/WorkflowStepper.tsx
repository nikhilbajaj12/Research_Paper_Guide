'use client';

import React from 'react';
import { Card } from '@/components/common/Card';

const STEPS = [
  { num: 1, title: 'Select Conference', desc: 'Choose your target conference' },
  { num: 2, title: 'Upload Paper', desc: 'Upload PDF, DOCX, or LaTeX ZIP' },
  { num: 3, title: 'Run Compliance Checks', desc: 'Analyze against conference rules' },
  { num: 4, title: 'Review Issues', desc: 'View compliance issues and fixes' },
  { num: 5, title: 'Generate Overleaf ZIP', desc: 'Download ready-to-use package' },
];

export const WorkflowStepper: React.FC = () => {
  return (
    <Card>
      <h2 className="text-lg font-bold text-slate-900 mb-5">How It Works</h2>
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
        {STEPS.map((step, idx) => (
          <div key={step.num} className="relative flex sm:flex-col items-start sm:items-center gap-3 sm:gap-2">
            {idx < STEPS.length - 1 && (
              <div className="hidden sm:block absolute top-5 left-[calc(50%+1.5rem)] w-full h-0.5 bg-slate-200 -z-0" />
            )}
            <div className="flex-shrink-0 w-10 h-10 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm z-10">
              {step.num}
            </div>
            <div className="sm:text-center">
              <p className="text-sm font-semibold text-slate-800">{step.title}</p>
              <p className="text-xs text-slate-500 mt-0.5">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
