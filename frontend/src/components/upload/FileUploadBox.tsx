'use client';

import React, { useRef } from 'react';

interface FileUploadBoxProps {
  onFileSelect: (file: File) => void;
  accept?: string;
}

export const FileUploadBox: React.FC<FileUploadBoxProps> = ({ onFileSelect, accept = '.pdf,.docx,.zip' }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center cursor-pointer hover:border-blue-500"
      onClick={() => inputRef.current?.click()}
    >
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} className="hidden" />
      <p className="text-gray-600 text-lg mb-2">Click to select a file</p>
      <p className="text-gray-400 text-sm">PDF, DOCX, or LaTeX ZIP</p>
    </div>
  );
};
