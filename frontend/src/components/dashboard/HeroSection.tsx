'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ROUTES } from '@/constants/routes';

export const HeroSection: React.FC = () => {
  const router = useRouter();

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 text-white">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
      <div className="relative px-6 md:px-10 py-10 md:py-14">
        <div className="max-w-3xl">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight mb-4">
            Conference-Aware Research Paper<br className="hidden sm:inline" /> Submission Assistant
          </h1>
          <p className="text-lg md:text-xl text-indigo-100 mb-8 max-w-2xl">
            Validate your paper against conference submission rules, detect compliance issues, and generate an Overleaf-ready package.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => router.push(ROUTES.UPLOAD)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-indigo-700 font-semibold rounded-lg shadow-lg hover:bg-indigo-50 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Start New Analysis
            </button>
            <button
              onClick={() => router.push(ROUTES.DASHBOARD)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white font-semibold rounded-lg hover:bg-white/20 transition-colors border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              View Demo Flow
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
