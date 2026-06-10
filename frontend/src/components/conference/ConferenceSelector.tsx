'use client';

import React from 'react';
import { ConferenceCard } from './ConferenceCard';
import { Card } from '@/components/common/Card';
import { Conference } from '@/types/conference';

interface ConferenceSelectorProps {
  conferences: Conference[];
  selectedId?: string | null;
  onSelect: (conference: Conference) => void;
}

export const ConferenceSelector: React.FC<ConferenceSelectorProps> = ({ conferences, selectedId, onSelect }) => {
  return (
    <Card>
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-bold text-slate-900">Select Conference</h2>
        {selectedId && (
          <span className="text-xs text-indigo-600 font-medium">Conference selected</span>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {conferences.map((conf) => (
          <ConferenceCard
            key={conf.id}
            abbr={conf.abbr}
            name={conf.name}
            isAvailable={conf.id === 'neurips-2025'}
            isSelected={selectedId === conf.id}
            onClick={() => onSelect(conf)}
          />
        ))}
      </div>
    </Card>
  );
};
