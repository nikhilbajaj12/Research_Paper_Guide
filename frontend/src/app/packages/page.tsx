'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { packageApi } from '@/services/packageApi';
import { ROUTES } from '@/constants/routes';
import { Package } from '@/types/package';

function getConferenceId(): string {
  if (typeof window === 'undefined') return 'neurips-2025';
  const stored = localStorage.getItem('selectedConference');
  if (stored) {
    try { return JSON.parse(stored).id || 'neurips-2025'; } catch { return 'neurips-2025'; }
  }
  return 'neurips-2025';
}

export default function PackagesPage() {
  const router = useRouter();
  const [pkg, setPkg] = useState<Package | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const paperData = localStorage.getItem('uploadedPaper');
      if (!paperData) {
        router.push(ROUTES.UPLOAD);
        return;
      }

      const { paper_id } = JSON.parse(paperData);
      const result = await packageApi.generatePackage(paper_id, getConferenceId());
      setPkg(result);
      localStorage.setItem('generatedPackage', JSON.stringify(result));
    } catch (err: any) {
      setError(err.message || 'Package generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!pkg) return;

    try {
      const blob = await packageApi.downloadPackage(pkg.package_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `overleaf_${pkg.package_id}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'Download failed');
    }
  };

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Overleaf Package Generation</h1>

        {!pkg ? (
          <div className="bg-white p-8 rounded-lg shadow">
            <p className="mb-6 text-gray-700">
              Generate an Overleaf-ready LaTeX package with main.tex, references.bib, and compliance report.
            </p>
            <Button onClick={handleGenerate} disabled={loading}>
              {loading ? <Loader /> : 'Generate Package'}
            </Button>
            {error && <div className="mt-4"><ErrorMessage message={error} /></div>}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-green-100 p-6 rounded-lg">
              <p className="text-green-800 font-semibold">Package generated successfully!</p>
            </div>

            <div className="bg-white p-8 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Generated Files</h2>
              <ul className="space-y-2">
                {pkg.generated_files.map(file => (
                  <li key={file.file_name} className="flex items-center p-2 bg-gray-50 rounded">
                    <span className="font-mono text-sm">{file.file_name}</span>
                    <span className="ml-auto text-gray-500 text-sm">{file.file_type}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white p-8 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Next Steps</h2>
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Download the ZIP package below</li>
                <li>Upload ZIP to Overleaf</li>
                <li>Ensure neurips_2026.sty exists in project</li>
                <li>Set main.tex as main file</li>
                <li>Recompile from scratch if references dont appear</li>
                <li>Review and submit to conference</li>
              </ol>
            </div>

            <div className="flex gap-4">
              <Button onClick={handleDownload}>Download Package</Button>
              <Button onClick={() => router.push(ROUTES.UPLOAD)} variant="secondary">Upload New Paper</Button>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
