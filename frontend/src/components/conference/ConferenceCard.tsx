'use client';

import React from 'react';

interface ConferenceCardProps {
  abbr: string;
  name: string;
  isAvailable: boolean;
  onClick?: () => void;
}

export const ConferenceCard: React.FC<ConferenceCardProps> = ({ abbr, name, isAvailable, onClick }) => {
  return (
    <div
      className={`p-6 bg-white rounded-lg shadow border-t-4 border-blue-500 ${isAvailable ? 'cursor-pointer hover:shadow-lg' : ''}`}
      onClick={isAvailable ? onClick : undefined}
    >
      <h3 className="text-xl font-bold mb-1">{abbr}</h3>
      <p className="text-gray-600 text-sm mb-3">{name}</p>
      {isAvailable ? (
        <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">Available</span>
      ) : (
        <span className="inline-block bg-gray-100 text-gray-500 px-3 py-1 rounded-full text-sm font-medium">Coming Soon</span>
      )}
    </div>
  );
};
