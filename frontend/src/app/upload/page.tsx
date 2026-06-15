'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Card } from '@/components/common/Card';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { Loader } from '@/components/common/Loader';
import { FileUploadBox } from '@/components/upload/FileUploadBox';
import { UploadProgress } from '@/components/upload/UploadProgress';
import { paperApi } from '@/services/paperApi';
import { ROUTES } from '@/constants/routes';
import { isValidFileType, isValidFileSize } from '@/utils/validators';

const DEFAULT_CONFERENCE = 'neurips-2025';

function getConferenceInfo(): { id: string; name: string } {
  if (typeof window === 'undefined') return { id: DEFAULT_CONFERENCE, name: 'NeurIPS 2026' };
  const stored = localStorage.getItem('selectedConference');
  if (stored) {
    try {
      const data = JSON.parse(stored);
      return { id: data.id || DEFAULT_CONFERENCE, name: data.name || 'NeurIPS' };
    } catch { return { id: DEFAULT_CONFERENCE, name: 'NeurIPS 2026' }; }
  }
  return { id: DEFAULT_CONFERENCE, name: 'NeurIPS 2026' };
}

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const conference = getConferenceInfo();

  const handleFileSelect = (f: File) => {
    if (!isValidFileType(f.name)) {
      setError('Invalid file type. Please upload PDF, DOCX, or ZIP file.');
      return;
    }
    if (!isValidFileSize(f.size)) {
      setError('File size exceeds 50MB limit.');
      return;
    }
    setError(null);
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await paperApi.uploadPaper(file, conference.id);
      localStorage.setItem('uploadedPaper', JSON.stringify(result));
      router.push(ROUTES.REPORT);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">New Analysis</h1>
          <p className="text-slate-500 mt-1">Upload your paper for compliance checking.</p>
        </div>

        <Card>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-500">Conference:</span>
            <Badge text={conference.name} variant="info" />
            <span className="text-xs text-slate-400 ml-auto">Selected on home screen</span>
          </div>
        </Card>

        <FileUploadBox onFileSelect={handleFileSelect} selectedFile={file ? { name: file.name, size: file.size } : null} />

        {loading && file && <UploadProgress fileName={file.name} />}

        {error && <ErrorMessage message={error} />}

        <div className="flex gap-3">
          <Button onClick={handleUpload} disabled={!file || loading}>
            {loading ? <Loader /> : 'Upload & Analyze'}
          </Button>
          <Button onClick={() => router.push(ROUTES.HOME)} variant="secondary">
            Back
          </Button>
        </div>

        <Card>
          <h3 className="text-sm font-bold text-slate-800 mb-2">Supported Formats</h3>
          <ul className="text-sm text-slate-500 space-y-1">
            <li>• PDF (.pdf)</li>
            <li>• Word Document (.docx)</li>
            <li>• LaTeX Project (.zip)</li>
          </ul>
          <p className="text-xs text-slate-400 mt-2">Maximum file size: 50MB</p>
        </Card>
      </div>
    </PageContainer>
  );
}
