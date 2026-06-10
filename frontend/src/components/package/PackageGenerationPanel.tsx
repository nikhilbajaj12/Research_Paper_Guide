'use client';

import React from 'react';
import { Button } from '@/components/common/Button';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { Card } from '@/components/common/Card';
import { GeneratedFile } from '@/types/package';

interface PackageGenerationPanelProps {
  onGenerate: () => void;
  loading: boolean;
  error: string | null;
  generatedFiles: GeneratedFile[] | null;
}

export const PackageGenerationPanel: React.FC<PackageGenerationPanelProps> = ({
  onGenerate,
  loading,
  error,
  generatedFiles,
}) => {
  if (generatedFiles) {
    return (
      <Card>
        <h2 className="text-lg font-bold text-slate-900 mb-4">Generated Files</h2>
        <div className="space-y-2">
          {generatedFiles.map((file) => (
            <div key={file.file_name} className="flex items-center p-3 rounded-lg bg-slate-50 border border-slate-200">
              <svg className="w-4 h-4 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="font-mono text-sm text-slate-800">{file.file_name}</span>
              <span className="ml-auto text-xs text-slate-500">{file.file_type}</span>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900 mb-1">Generate Overleaf Package</h2>
          <p className="text-sm text-slate-500">Create a ready-to-use LaTeX package with compliance fixes.</p>
        </div>
        <Button onClick={onGenerate} disabled={loading}>
          {loading ? <Loader /> : 'Generate Package'}
        </Button>
      </div>
      {error && <div className="mt-4"><ErrorMessage message={error} /></div>}
    </Card>
  );
};
