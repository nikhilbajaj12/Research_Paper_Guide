'use client';

import React from 'react';
import { Badge } from '@/components/common/Badge';

interface ConferenceCardProps {
  abbr: string;
  name: string;
  isAvailable: boolean;
  isSelected?: boolean;
  onClick?: () => void;
}

const conferenceMeta: Record<string, { icon: string; guidelines: string[] }> = {
  NeurIPS: {
    icon: 'N',
    guidelines: ['Anonymous review required', 'Main page limit: 9 pages', 'Official LaTeX template required', 'OpenReview submission'],
  },
  CVPR: { icon: 'C', guidelines: ['Coming in 2026'] },
  ICML: { icon: 'I', guidelines: ['Coming in 2026'] },
  ACL: { icon: 'A', guidelines: ['Coming in 2026'] },
  EMNLP: { icon: 'E', guidelines: ['Coming in 2026'] },
};

export const ConferenceCard: React.FC<ConferenceCardProps> = ({ abbr, name, isAvailable, isSelected, onClick }) => {
  const meta = conferenceMeta[abbr] || { icon: abbr[0], guidelines: [] };

  return (
    <div
      className={`relative group rounded-xl border-2 transition-all ${
        isSelected
          ? 'border-indigo-500 bg-indigo-50 shadow-md shadow-indigo-100'
          : isAvailable
          ? 'border-slate-200 bg-white hover:border-indigo-300 hover:shadow-lg cursor-pointer'
          : 'border-slate-100 bg-slate-50 opacity-60 cursor-default'
      }`}
      onClick={isAvailable ? onClick : undefined}
    >
      {isSelected && (
        <div className="absolute -top-2.5 -right-2.5 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg ${
              isAvailable ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-400'
            }`}>
              {meta.icon}
            </div>
            <div>
              <h3 className="font-bold text-slate-900">{abbr}</h3>
              <p className="text-xs text-slate-500">{name}</p>
            </div>
          </div>
          <Badge
            text={isAvailable ? 'Available' : 'Coming Soon'}
            variant={isAvailable ? 'success' : 'default'}
          />
        </div>

        <div className="space-y-1.5 mb-4">
          {meta.guidelines.map((g, i) => (
            <p key={i} className={`text-xs flex items-start gap-1.5 ${
              isAvailable ? 'text-slate-600' : 'text-slate-400'
            }`}>
              <span className="mt-0.5">•</span>
              {g}
            </p>
          ))}
        </div>

        {isAvailable && (
          <button
            onClick={(e) => { e.stopPropagation(); onClick?.(); }}
            className={`w-full py-2 rounded-lg text-sm font-semibold transition-colors ${
              isSelected
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-indigo-600 hover:text-white'
            }`}
          >
            {isSelected ? 'Selected' : 'Select ' + abbr}
          </button>
        )}
      </div>
    </div>
  );
};
