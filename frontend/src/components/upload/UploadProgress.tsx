'use client';

import React from 'react';
import { Loader } from '@/components/common/Loader';

interface UploadProgressProps {
  fileName: string;
  progress?: number;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({ fileName, progress }) => {
  return (
    <div className="bg-blue-50 p-4 rounded-lg">
      <div className="flex items-center gap-3 mb-2">
        <Loader />
        <p className="text-blue-900 font-medium">Uploading {fileName}...</p>
      </div>
      {progress !== undefined && (
        <div className="w-full bg-blue-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${progress}%` }} />
        </div>
      )}
    </div>
  );
};
