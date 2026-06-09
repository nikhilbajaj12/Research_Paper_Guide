export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'submission_ready':
      return 'bg-green-100 text-green-800';
    case 'needs_minor_fixes':
      return 'bg-yellow-100 text-yellow-800';
    case 'needs_major_fixes':
      return 'bg-orange-100 text-orange-800';
    case 'not_ready':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical':
      return 'text-red-600';
    case 'warning':
      return 'text-yellow-600';
    case 'info':
      return 'text-blue-600';
    default:
      return 'text-gray-600';
  }
};
