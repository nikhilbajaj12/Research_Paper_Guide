'use client';

import React from 'react';
import { Button } from '@/components/common/Button';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
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
      <div className="bg-white p-8 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Generated Files</h2>
        <ul className="space-y-2">
          {generatedFiles.map((file) => (
            <li key={file.file_name} className="flex items-center p-2 bg-gray-50 rounded">
              <span className="font-mono text-sm">{file.file_name}</span>
              <span className="ml-auto text-gray-500 text-sm">{file.file_type}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="bg-white p-8 rounded-lg shadow">
      <p className="mb-6 text-gray-700">
        Generate an Overleaf-ready LaTeX package with main.tex, references.bib, and compliance report.
      </p>
      <Button onClick={onGenerate} disabled={loading}>
        {loading ? <Loader /> : 'Generate Package'}
      </Button>
      {error && <div className="mt-4"><ErrorMessage message={error} /></div>}
    </div>
  );
};
