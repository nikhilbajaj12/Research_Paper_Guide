'use client';

import React from 'react';
import { Conference } from '@/types/conference';
import { ConferenceCard } from './ConferenceCard';

interface ConferenceSelectorProps {
  conferences: Conference[];
  onSelect: (conference: Conference) => void;
}

export const ConferenceSelector: React.FC<ConferenceSelectorProps> = ({ conferences, onSelect }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {conferences.map((conf) => (
        <ConferenceCard
          key={conf.id}
          abbr={conf.abbr}
          name={conf.name}
          isAvailable={conf.id === 'neurips-2025'}
          onClick={() => onSelect(conf)}
        />
      ))}
    </div>
  );
};
