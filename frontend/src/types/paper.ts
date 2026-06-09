export interface UploadedPaper {
  paper_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
}

export interface Paper extends UploadedPaper {
  conference_id: string;
  upload_date: string;
}
