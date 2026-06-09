'use client';

import Link from 'next/link';
import { ROUTES } from '@/constants/routes';
import { LABELS } from '@/constants/labels';

export const Header: React.FC = () => {
  return (
    <header className="bg-blue-600 text-white shadow">
      <div className="container mx-auto px-4 py-4">
        <Link href={ROUTES.HOME} className="text-2xl font-bold hover:text-blue-100">
          {LABELS.APP_NAME}
        </Link>
      </div>
    </header>
  );
};
