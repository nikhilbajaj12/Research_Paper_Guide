'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Card } from '@/components/common/Card';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { RecommendationsPanel } from '@/components/report/RecommendationsPanel';
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

function severityVariant(severity: string): 'success' | 'warning' | 'error' | 'info' {
  if (severity === 'critical') return 'error';
  if (severity === 'warning') return 'warning';
  return 'info';
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
        <div className="flex justify-center items-center h-96"><Loader /></div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="max-w-3xl mx-auto space-y-4">
          <ErrorMessage message={error} />
          <Button onClick={() => router.push(ROUTES.UPLOAD)}>Back to Upload</Button>
        </div>
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

  const statusVariant: Record<string, 'success' | 'warning' | 'error' | 'info'> = {
    submission_ready: 'success',
    needs_minor_fixes: 'warning',
    needs_major_fixes: 'error',
    not_ready: 'error',
  };

  return (
    <PageContainer>
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Compliance Report</h1>
          <p className="text-slate-500 mt-1">Detailed compliance check results for your paper.</p>
        </div>

        <Card>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-xs text-slate-500 mb-1">Readiness Score</p>
              <p className={`text-3xl font-bold ${report.readiness_score >= 80 ? 'text-emerald-600' : report.readiness_score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                {report.readiness_score}/100
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Status</p>
              <Badge text={report.overall_status.replace(/_/g, ' ')} variant={statusVariant[report.overall_status] || 'info'} />
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Issues</p>
              <p className="text-2xl font-bold text-slate-800">{report.issues.length}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Passed</p>
              <p className="text-2xl font-bold text-emerald-600">{report.passed_checks.length}</p>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            {report.critical_count > 0 && (
              <div className="rounded-xl border border-red-200 bg-white p-5">
                <h3 className="text-sm font-bold text-red-700 mb-3 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center text-xs">!</span>
                  Critical Issues ({report.critical_count})
                </h3>
                <div className="space-y-2">
                  {report.issues.filter(i => i.severity === 'critical').map(issue => (
                    <div key={issue.issue_id} className="p-3 rounded-lg bg-red-50 border border-red-100">
                      <p className="text-sm font-medium text-red-800">{issue.message}</p>
                      {issue.suggested_fix && <p className="text-xs text-red-600 mt-1">Fix: {issue.suggested_fix}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {report.warnings_count > 0 && (
              <div className="rounded-xl border border-amber-200 bg-white p-5">
                <h3 className="text-sm font-bold text-amber-700 mb-3 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center text-xs">!</span>
                  Warnings ({report.warnings_count})
                </h3>
                <div className="space-y-2">
                  {report.issues.filter(i => i.severity === 'warning').map(issue => (
                    <div key={issue.issue_id} className="p-3 rounded-lg bg-amber-50 border border-amber-100">
                      <p className="text-sm font-medium text-amber-800">{issue.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-6">
            {report.passed_checks.length > 0 && (
              <div className="rounded-xl border border-emerald-200 bg-white p-5">
                <h3 className="text-sm font-bold text-emerald-700 mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Passed Checks ({report.passed_checks.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {report.passed_checks.map((check) => (
                    <span key={check} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {check.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {report.recommendations && report.recommendations.length > 0 && (
          <RecommendationsPanel recommendations={report.recommendations} />
        )}

        <div className="flex gap-3">
          <Button onClick={() => router.push(ROUTES.PACKAGES)}>
            Generate Overleaf Package
          </Button>
          <Button onClick={() => router.push(ROUTES.UPLOAD)} variant="secondary">
            Upload New Paper
          </Button>
        </div>
      </div>
    </PageContainer>
  );
}
