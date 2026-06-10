'use client';

export const Loader: React.FC = () => {
  return (
    <div className="flex justify-center items-center">
      <div className="animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent" />
    </div>
  );
};
