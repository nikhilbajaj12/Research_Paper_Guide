import { PageContainer } from '@/components/layout/PageContainer';
import Link from 'next/link';
import { ROUTES } from '@/constants/routes';
import { LABELS } from '@/constants/labels';
import { Button } from '@/components/common/Button';

export default function Home() {
  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto text-center py-12">
        <h1 className="text-4xl font-bold mb-4">{LABELS.APP_NAME}</h1>
        <p className="text-xl text-gray-600 mb-8">{LABELS.APP_SUBTITLE}</p>
        
        <Link href={ROUTES.UPLOAD}>
          <Button>Start New Analysis</Button>
        </Link>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
          <ConferenceCard name={LABELS.NEURIPS} status="available" abbr="NeurIPS" />
          <ConferenceCard name={LABELS.CVPR} status="coming" abbr="CVPR" />
          <ConferenceCard name={LABELS.ICML} status="coming" abbr="ICML" />
          <ConferenceCard name={LABELS.ACL} status="coming" abbr="ACL" />
        </div>
      </div>
    </PageContainer>
  );
}

function ConferenceCard({ name, status, abbr }: { name: string; status: string; abbr: string }) {
  const isAvailable = status === 'available';
  return (
    <div className="p-6 bg-white rounded-lg shadow border-t-4 border-blue-500">
      <h3 className="text-xl font-bold mb-1">{abbr}</h3>
      <p className="text-gray-600 text-sm mb-3">{name}</p>
      {isAvailable ? (
        <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">Available</span>
      ) : (
        <span className="inline-block bg-gray-100 text-gray-500 px-3 py-1 rounded-full text-sm font-medium">Coming Soon</span>
      )}
    </div>
  );
}
