export const isValidFileType = (fileName: string): boolean => {
  const validExtensions = ['.pdf', '.docx', '.zip'];
  const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
  return validExtensions.includes(ext);
};

export const isValidFileSize = (sizeInBytes: number, maxMB: number = 50): boolean => {
  const maxBytes = maxMB * 1024 * 1024;
  return sizeInBytes <= maxBytes;
};
