'use client';

import React from 'react';
import { ConferenceCard } from './ConferenceCard';
import { Card } from '@/components/common/Card';
import { Conference } from '@/types/conference';

interface ConferenceSelectorProps {
  conferences: Conference[];
  selectedId?: string | null;
  onSelect: (conference: Conference) => void;
  configMap?: Record<string, { conference_name: string; conference_year: number; max_pages: number; blind_review: boolean; reference_style: string }>;
}

export const ConferenceSelector: React.FC<ConferenceSelectorProps> = ({ conferences, selectedId, onSelect, configMap }) => {
  return (
    <Card>
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-bold text-slate-900">Select Conference</h2>
        {selectedId && (
          <span className="text-xs text-indigo-600 font-medium">Conference selected</span>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {conferences.map((conf) => {
          const cfgData = configMap?.[conf.id];
          return (
            <ConferenceCard
              key={conf.id}
              abbr={conf.abbr}
              name={conf.name}
              year={cfgData?.conference_year}
              isAvailable={!!cfgData}
              isSelected={selectedId === conf.id}
              onClick={() => onSelect(conf)}
              maxPages={cfgData?.max_pages}
              blindReview={cfgData?.blind_review}
              referenceStyle={cfgData?.reference_style}
            />
          );
        })}
      </div>
    </Card>
  );
};
