'use client';

import React, { useState } from 'react';
import { Button } from '@/components/common/Button';
import { Loader } from '@/components/common/Loader';

interface DownloadPackageButtonProps {
  onDownload: () => Promise<void>;
}

export const DownloadPackageButton: React.FC<DownloadPackageButtonProps> = ({ onDownload }) => {
  const [downloading, setDownloading] = useState(false);

  const handleClick = async () => {
    setDownloading(true);
    try {
      await onDownload();
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Button onClick={handleClick} disabled={downloading}>
      {downloading ? <Loader /> : 'Download Package'}
    </Button>
  );
};
