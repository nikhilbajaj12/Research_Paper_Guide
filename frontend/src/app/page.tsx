'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { HeroSection } from '@/components/dashboard/HeroSection';
import { WorkflowStepper } from '@/components/dashboard/WorkflowStepper';
import { StatsPreview } from '@/components/dashboard/StatsPreview';
import { ConferenceSelector } from '@/components/conference/ConferenceSelector';
import { RecommendationsPanel } from '@/components/report/RecommendationsPanel';
import { FileUploadBox } from '@/components/upload/FileUploadBox';
import { UploadProgress } from '@/components/upload/UploadProgress';
import { PackageGenerationPanel } from '@/components/package/PackageGenerationPanel';
import { conferenceApi } from '@/services/conferenceApi';
import { paperApi } from '@/services/paperApi';
import { complianceApi } from '@/services/complianceApi';
import { packageApi } from '@/services/packageApi';
import { ROUTES } from '@/constants/routes';
import { isValidFileType, isValidFileSize } from '@/utils/validators';
import { formatFileSize } from '@/utils/formatters';
import { Conference, ConferenceBrief } from '@/types/conference';
import { ConferenceConfig } from '@/services/conferenceApi';
import { ComplianceReport } from '@/types/compliance';
import { Package } from '@/types/package';

export default function HomePage() {
  const router = useRouter();
  const [conferences, setConferences] = useState<ConferenceBrief[]>([]);
  const [conferenceConfigs, setConferenceConfigs] = useState<Record<string, any>>({});
  const [selectedConference, setSelectedConference] = useState<Conference | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [pkg, setPkg] = useState<Package | null>(null);
  const [generatingPkg, setGeneratingPkg] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const configList: ConferenceConfig[] = await conferenceApi.getConfigList();

        const conferenceList: ConferenceBrief[] = configList.map(cfg => ({
          id: cfg.conference_id,
          abbr: cfg.conference_name.substring(0, 4).toUpperCase(),
          name: cfg.conference_name,
          start_date: `${cfg.conference_year}-01-01`,
          submission_deadline: `${cfg.conference_year}-06-01`,
          location: 'TBD',
        }));
        setConferences(conferenceList);

        const cfgMap: Record<string, any> = {};
        for (const cfg of configList) {
          cfgMap[cfg.conference_id] = {
            conference_name: cfg.conference_name,
            conference_year: cfg.conference_year,
            max_pages: cfg.max_pages,
            blind_review: cfg.blind_review,
            reference_style: cfg.reference_style,
            required_sections: cfg.required_sections,
            package_template: cfg.package_template,
          };
        }
        setConferenceConfigs(cfgMap);
      } catch (err: any) {
        setError(err.message || 'Failed to load conferences');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSelectConference = (conf: ConferenceBrief) => {
    const cfg = conferenceConfigs[conf.id];
    const detailed: Conference = {
      ...conf,
      max_pages: cfg?.max_pages ?? 9,
      requires_anonymity: cfg?.blind_review ?? true,
      reference_format: cfg?.reference_style ?? 'bibtex',
      guidelines: cfg ? {
        conference_id: conf.id,
        max_pages: cfg.max_pages,
        requires_anonymity: cfg.blind_review,
        reference_format: cfg.reference_style,
        required_sections: cfg.required_sections,
      } : undefined,
    };
    setSelectedConference(detailed);
    localStorage.setItem('selectedConference', JSON.stringify(detailed));
  };

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

  const handleUploadAndAnalyze = async () => {
    if (!file || !selectedConference) {
      setError('Please select a conference and file first.');
      return;
    }

    setUploading(true);
    setError(null);
    try {
      const uploaded = await paperApi.uploadPaper(file, selectedConference.id);
      localStorage.setItem('uploadedPaper', JSON.stringify(uploaded));

      setUploading(false);
      setAnalyzing(true);

      const complianceResult = await complianceApi.analyzeCompliance(uploaded.paper_id, selectedConference.id);
      setReport(complianceResult);
      localStorage.setItem('complianceReport', JSON.stringify(complianceResult));
    } catch (err: any) {
      setError(err.message || 'Upload or analysis failed');
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const handleGeneratePackage = async () => {
    if (!report) return;
    setGeneratingPkg(true);
    setError(null);
    try {
      const result = await packageApi.generatePackage(report.paper_id, report.conference_id);
      setPkg(result);
      localStorage.setItem('generatedPackage', JSON.stringify(result));
    } catch (err: any) {
      setError(err.message || 'Package generation failed');
    } finally {
      setGeneratingPkg(false);
    }
  };

  const handleDownloadPackage = async () => {
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

  const cfgData = selectedConference ? conferenceConfigs[selectedConference.id] : null;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      <HeroSection />

      <WorkflowStepper />

      {error && <ErrorMessage message={error} />}

      <ConferenceSelector
        conferences={conferences}
        selectedId={selectedConference?.id || null}
        onSelect={handleSelectConference}
        configMap={conferenceConfigs}
      />

      {selectedConference && cfgData && (
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                {cfgData.conference_name} {cfgData.conference_year}
              </h2>
              <p className="text-sm text-slate-500 mt-1">{selectedConference.id}</p>
            </div>
            <Badge text="Selected" variant="success" />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500">Max Pages</p>
              <p className="text-lg font-bold text-slate-800">{cfgData.max_pages}</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500">Blind Review</p>
              <p className="text-lg font-bold text-slate-800">{cfgData.blind_review ? 'Yes' : 'No'}</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500">Reference Style</p>
              <p className="text-lg font-bold text-slate-800 capitalize">{cfgData.reference_style}</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500">Required Sections</p>
              <p className="text-lg font-bold text-slate-800">{cfgData.required_sections?.length || 0}</p>
            </div>
          </div>
        </Card>
      )}

      {selectedConference && (
        <FileUploadBox
          onFileSelect={handleFileSelect}
          selectedFile={file ? { name: file.name, size: file.size } : null}
        />
      )}

      {(uploading || analyzing) && (
        <UploadProgress
          fileName={file?.name || ''}
          status={uploading ? 'uploading' : 'processing'}
        />
      )}

      {selectedConference && file && !uploading && !analyzing && !report && (
        <div className="flex justify-center">
          <Button onClick={handleUploadAndAnalyze} size="lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Upload & Run Compliance Check
          </Button>
        </div>
      )}

      {report && (
        <Card>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <div className="text-center">
              <p className="text-xs text-slate-500 mb-1">Compliance Score</p>
              <div className={`text-4xl font-bold ${
                report.readiness_score >= 80 ? 'text-emerald-600' :
                report.readiness_score >= 50 ? 'text-amber-600' : 'text-red-600'
              }`}>
                {report.readiness_score}
                <span className="text-lg text-slate-400">/100</span>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-xs text-slate-500 mb-1">Status</p>
              <Badge
                text={report.overall_status.replace(/_/g, ' ')}
                variant={
                  report.overall_status === 'submission_ready' ? 'success' :
                  report.overall_status === 'needs_minor_fixes' ? 'warning' : 'error'
                }
              />
              <div className="grid grid-cols-3 gap-4 mt-3">
                <div>
                  <p className="text-xs text-slate-400">Issues</p>
                  <p className="text-lg font-bold text-slate-800">{report.issues.length}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Critical</p>
                  <p className={`text-lg font-bold ${report.critical_count > 0 ? 'text-red-600' : 'text-slate-400'}`}>{report.critical_count}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Warnings</p>
                  <p className={`text-lg font-bold ${report.warnings_count > 0 ? 'text-amber-600' : 'text-slate-400'}`}>{report.warnings_count}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      <StatsPreview
        score={report?.readiness_score ?? null}
        criticalCount={report?.critical_count ?? 0}
        warningCount={report?.warnings_count ?? 0}
        passedCount={report?.passed_checks?.length ?? 0}
        hasReport={!!report}
      />

      {report && report.recommendations && report.recommendations.length > 0 && (
        <RecommendationsPanel recommendations={report.recommendations} />
      )}

      {report && !pkg && (
        <PackageGenerationPanel
          onGenerate={handleGeneratePackage}
          loading={generatingPkg}
          error={null}
          generatedFiles={null}
        />
      )}

      {pkg && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-emerald-800">Package generated successfully!</p>
                <p className="text-sm text-emerald-600">{pkg.generated_files.length} files ready for download</p>
              </div>
            </div>
            <Button onClick={handleDownloadPackage} variant="primary">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download Package
            </Button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {report && (
          <div className="space-y-6">
            {report.critical_count > 0 && (
              <div className="rounded-xl border border-red-200 bg-white p-5">
                <h3 className="text-sm font-bold text-red-700 mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  Critical Issues ({report.critical_count})
                </h3>
                <div className="space-y-2">
                  {report.issues.filter(i => i.severity === 'critical').map(issue => (
                    <div key={issue.issue_id} className="p-3 rounded-lg bg-red-50 border border-red-100">
                      <p className="text-sm font-medium text-red-800">{issue.message}</p>
                      {issue.location && <p className="text-xs text-red-500 mt-0.5">Location: {issue.location}</p>}
                      {issue.suggested_fix && <p className="text-xs text-red-600 mt-1">Fix: {issue.suggested_fix}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {report.warnings_count > 0 && (
              <div className="rounded-xl border border-amber-200 bg-white p-5">
                <h3 className="text-sm font-bold text-amber-700 mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Warnings ({report.warnings_count})
                </h3>
                <div className="space-y-2">
                  {report.issues.filter(i => i.severity === 'warning').map(issue => (
                    <div key={issue.issue_id} className="p-3 rounded-lg bg-amber-50 border border-amber-100">
                      <p className="text-sm font-medium text-amber-800">{issue.message}</p>
                      {issue.location && <p className="text-xs text-amber-500 mt-0.5">Location: {issue.location}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {report && (
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
        )}
      </div>
    </div>
  );
}
