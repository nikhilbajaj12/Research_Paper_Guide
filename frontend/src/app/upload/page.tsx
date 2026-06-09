'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { Loader } from '@/components/common/Loader';
import { paperApi } from '@/services/paperApi';
import { ROUTES } from '@/constants/routes';
import { formatFileSize } from '@/utils/formatters';
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (!isValidFileType(selectedFile.name)) {
      setError('Invalid file type. Please upload PDF, DOCX, or ZIP file.');
      return;
    }

    if (!isValidFileSize(selectedFile.size)) {
      setError('File size exceeds 50MB limit.');
      return;
    }

    setError(null);
    setFile(selectedFile);
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
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Upload Paper</h1>

        <div className="bg-white p-8 rounded-lg shadow">
          <div className="mb-6">
            <label className="block text-lg font-semibold mb-4">Select File (PDF, DOCX, or ZIP)</label>
            <input
              type="file"
              accept=".pdf,.docx,.zip"
              onChange={handleFileSelect}
              className="block w-full p-3 border border-gray-300 rounded"
            />
          </div>

          {file && (
            <div className="mb-6 p-4 bg-blue-50 rounded">
              <p className="text-blue-900">
                Selected: {file.name} ({formatFileSize(file.size)})
              </p>
            </div>
          )}

          {error && <ErrorMessage message={error} />}

          <Button onClick={handleUpload} disabled={!file || loading}>
            {loading ? <Loader /> : 'Upload & Analyze'}
          </Button>
        </div>
      </div>
    </PageContainer>
  );
}
