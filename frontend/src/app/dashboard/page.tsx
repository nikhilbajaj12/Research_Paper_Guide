'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ROUTES } from '@/constants/routes';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(ROUTES.HOME);
  }, []);

  return null;
}
