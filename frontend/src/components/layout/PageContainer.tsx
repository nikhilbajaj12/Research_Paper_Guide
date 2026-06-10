'use client';

import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
}

export const PageContainer: React.FC<PageContainerProps> = ({ children }) => {
  return (
    <div className="max-w-6xl mx-auto">
      {children}
    </div>
  );
};
