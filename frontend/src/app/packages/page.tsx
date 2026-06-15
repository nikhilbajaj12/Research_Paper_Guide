'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Card } from '@/components/common/Card';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { packageApi } from '@/services/packageApi';
import { ROUTES } from '@/constants/routes';
import { Package } from '@/types/package';

function getConferenceData(): { id: string; name: string; year?: number } {
  if (typeof window === 'undefined') return { id: 'neurips-2025', name: 'NeurIPS' };
  const stored = localStorage.getItem('selectedConference');
  if (stored) {
    try {
      const data = JSON.parse(stored);
      return { id: data.id || 'neurips-2025', name: data.name || 'NeurIPS', year: data.start_date ? parseInt(data.start_date.slice(0, 4)) : 2026 };
    } catch { return { id: 'neurips-2025', name: 'NeurIPS' }; }
  }
  return { id: 'neurips-2025', name: 'NeurIPS' };
}

export default function PackagesPage() {
  const router = useRouter();
  const [pkg, setPkg] = useState<Package | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const conference = getConferenceData();

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
      const result = await packageApi.generatePackage(paper_id, conference.id);
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
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Packages</h1>
          <p className="text-slate-500 mt-1">Generate and download Overleaf-ready LaTeX packages.</p>
        </div>

        {!pkg ? (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 mb-1">Generate Overleaf Package</h2>
                  <p className="text-sm text-slate-500">
                    Generate an Overleaf-ready LaTeX package with main.tex, references.bib, and compliance report.
                  </p>
                </div>
                <Button onClick={handleGenerate} disabled={loading}>
                  {loading ? <Loader /> : 'Generate Package'}
                </Button>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <span className="font-medium text-slate-700">Conference:</span>
                <Badge text={`${conference.name}${conference.year ? ` ${conference.year}` : ''}`} variant="info" />
                <span className="text-xs text-slate-400 ml-2">Conference-aware template will be applied</span>
              </div>
              {error && <div className="mt-4"><ErrorMessage message={error} /></div>}
            </div>
          </Card>
        ) : (
          <div className="space-y-6">
            <Card className="border-emerald-200 bg-emerald-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-emerald-800">Package generated successfully!</p>
                  <p className="text-sm text-emerald-600">Generated for {conference.name}{conference.year ? ` ${conference.year}` : ''}</p>
                </div>
              </div>
            </Card>

            <Card>
              <h2 className="text-lg font-bold text-slate-900 mb-4">Generated Files</h2>
              <div className="space-y-2">
                {pkg.generated_files.map(file => (
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

            <Card>
              <h2 className="text-lg font-bold text-slate-900 mb-4">Next Steps</h2>
              <ol className="space-y-2 text-sm text-slate-600">
                {[
                  'Download the ZIP package below',
                  'Upload ZIP to Overleaf',
                  'Ensure the conference .sty file exists in project',
                  'Set main.tex as main file',
                  'Recompile from scratch if references don\'t appear',
                  'Review and submit to conference',
                ].map((step, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold mt-0.5">{i + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </Card>

            <div className="flex gap-3">
              <Button onClick={handleDownload}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Package
              </Button>
              <Button onClick={() => router.push(ROUTES.UPLOAD)} variant="secondary">
                Upload New Paper
              </Button>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
