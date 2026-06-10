'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { Loader } from '@/components/common/Loader';
import { FileUploadBox } from '@/components/upload/FileUploadBox';
import { UploadProgress } from '@/components/upload/UploadProgress';
import { paperApi } from '@/services/paperApi';
import { ROUTES } from '@/constants/routes';
import { isValidFileType, isValidFileSize } from '@/utils/validators';

const DEFAULT_CONFERENCE = 'neurips-2025';

function getConferenceId(): string {
  if (typeof window === 'undefined') return DEFAULT_CONFERENCE;
  const stored = localStorage.getItem('selectedConference');
  if (stored) {
    try { return JSON.parse(stored).id || DEFAULT_CONFERENCE; } catch { return DEFAULT_CONFERENCE; }
  }
  return DEFAULT_CONFERENCE;
}

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const result = await paperApi.uploadPaper(file, getConferenceId());
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
