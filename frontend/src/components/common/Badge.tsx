'use client';

import React from 'react';
import { getSeverityColor } from '@/utils/formatters';

interface BadgeProps {
  text: string;
  variant?: 'success' | 'warning' | 'error' | 'info';
}

export const Badge: React.FC<BadgeProps> = ({ text, variant = 'info' }) => {
  const colors = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  };

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${colors[variant]}`}>
      {text}
    </span>
  );
};
