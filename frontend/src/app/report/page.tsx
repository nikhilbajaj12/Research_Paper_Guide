'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { complianceApi } from '@/services/complianceApi';
import { ROUTES } from '@/constants/routes';
import { ComplianceReport } from '@/types/compliance';

function getConferenceId(): string {
  if (typeof window === 'undefined') return 'neurips-2025';
  const stored = localStorage.getItem('selectedConference');
  if (stored) {
    try { return JSON.parse(stored).id || 'neurips-2025'; } catch { return 'neurips-2025'; }
  }
  return 'neurips-2025';
}

export default function ReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const analyzePaper = async () => {
      try {
        const paperData = localStorage.getItem('uploadedPaper');
        if (!paperData) {
          router.push(ROUTES.UPLOAD);
          return;
        }

        const { paper_id } = JSON.parse(paperData);
        const result = await complianceApi.analyzeCompliance(paper_id, getConferenceId());
        setReport(result);
        localStorage.setItem('complianceReport', JSON.stringify(result));
      } catch (err: any) {
        setError(err.message || 'Analysis failed');
      } finally {
        setLoading(false);
      }
    };

    analyzePaper();
  }, []);

  if (loading) {
    return (
      <PageContainer>
        <div className="flex justify-center items-center h-96">
          <Loader />
        </div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <ErrorMessage message={error} />
        <Button onClick={() => router.push(ROUTES.UPLOAD)}>Back to Upload</Button>
      </PageContainer>
    );
  }

  if (!report) {
    return (
      <PageContainer>
        <ErrorMessage message="No report data found" />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Compliance Report</h1>

        <div className="bg-white p-8 rounded-lg shadow mb-8">
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <p className="text-gray-600">Score</p>
              <p className="text-4xl font-bold text-blue-600">{report.readiness_score}/100</p>
            </div>
            <div>
              <p className="text-gray-600">Status</p>
              <Badge text={report.overall_status.replace(/_/g, ' ')} variant="info" />
            </div>
            <div>
              <p className="text-gray-600">Issues</p>
              <p className="text-2xl font-bold">{report.issues.length}</p>
            </div>
          </div>
        </div>

        {report.critical_count > 0 && (
          <div className="bg-white p-8 rounded-lg shadow mb-8 border-l-4 border-red-600">
            <h2 className="text-2xl font-bold mb-4 text-red-600">Critical Issues ({report.critical_count})</h2>
            {report.issues.filter(i => i.severity === 'critical').map(issue => (
              <IssueCard key={issue.issue_id} issue={issue} />
            ))}
          </div>
        )}

        {report.warnings_count > 0 && (
          <div className="bg-white p-8 rounded-lg shadow mb-8 border-l-4 border-yellow-600">
            <h2 className="text-2xl font-bold mb-4 text-yellow-600">Warnings ({report.warnings_count})</h2>
            {report.issues.filter(i => i.severity === 'warning').map(issue => (
              <IssueCard key={issue.issue_id} issue={issue} />
            ))}
          </div>
        )}

        {report.passed_checks.length > 0 && (
          <div className="bg-white p-8 rounded-lg shadow mb-8 border-l-4 border-green-600">
            <h2 className="text-2xl font-bold mb-4 text-green-600">Passed Checks</h2>
            <div className="flex flex-wrap gap-2">
              {report.passed_checks.map(check => (
                <Badge key={check} text={check} variant="success" />
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-4 justify-between">
          <Button onClick={() => router.push(ROUTES.UPLOAD)} variant="secondary">Back to Upload</Button>
          <Button onClick={() => router.push(ROUTES.PACKAGES)}>Generate Overleaf Package</Button>
        </div>
      </div>
    </PageContainer>
  );
}

function IssueCard({ issue }: { issue: any }) {
  return (
    <div className="mb-4 p-4 border border-gray-300 rounded">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-lg">{issue.category}</h4>
        <Badge text={issue.severity} variant={issue.severity === 'critical' ? 'error' : 'warning'} />
      </div>
      <p className="text-gray-700 mb-2">{issue.message}</p>
      {issue.suggested_fix && (
        <p className="text-sm text-gray-600"><strong>Fix:</strong> {issue.suggested_fix}</p>
      )}
    </div>
  );
}
