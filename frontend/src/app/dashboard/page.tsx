'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/common/Button';
import { Loader } from '@/components/common/Loader';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { ConferenceCard } from '@/components/conference/ConferenceCard';
import { GuidelineSummary } from '@/components/conference/GuidelineSummary';
import { conferenceApi } from '@/services/conferenceApi';
import { ROUTES } from '@/constants/routes';
import { Conference, ConferenceBrief } from '@/types/conference';

export default function DashboardPage() {
  const router = useRouter();
  const [conferences, setConferences] = useState<ConferenceBrief[]>([]);
  const [selectedConference, setSelectedConference] = useState<Conference | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConferences = async () => {
      try {
        const data = await conferenceApi.getConferences();
        setConferences(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load conferences');
      } finally {
        setLoading(false);
      }
    };
    fetchConferences();
  }, []);

  const handleSelect = async (conf: ConferenceBrief) => {
    setLoadingDetails(true);
    try {
      const detailed = await conferenceApi.getConferenceById(conf.id);
      setSelectedConference(detailed);
      localStorage.setItem('selectedConference', JSON.stringify(detailed));
    } catch (err: any) {
      setSelectedConference({ ...conf, max_pages: 9, requires_anonymity: true, reference_format: 'bibtex' });
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleStartAnalysis = () => {
    if (selectedConference) {
      router.push(ROUTES.UPLOAD);
    }
  };

  if (loading) {
    return (
      <PageContainer>
        <div className="flex justify-center items-center h-96"><Loader /></div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">PaperGuide AI</h1>
          <p className="text-xl text-gray-600 mb-8">
            Conference-Aware Research Paper Submission Assistant
          </p>
        </div>

        {error && <div className="mb-6"><ErrorMessage message={error} /></div>}

        <h2 className="text-2xl font-bold mb-6">Select a Conference</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {conferences.map((conf) => (
            <ConferenceCard
              key={conf.id}
              abbr={conf.abbr}
              name={conf.name}
              isAvailable={conf.id === 'neurips-2025'}
              onClick={() => handleSelect(conf)}
            />
          ))}
        </div>

        {loadingDetails && (
          <div className="mt-8 flex justify-center"><Loader /></div>
        )}

        {selectedConference && !loadingDetails && (
          <div className="mt-8 space-y-6">
            <GuidelineSummary
              maxPages={selectedConference.max_pages}
              requiresAnonymity={selectedConference.requires_anonymity}
              referenceFormat={selectedConference.reference_format}
            />
            <div className="text-center">
              <Button onClick={handleStartAnalysis}>Start Analysis</Button>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
