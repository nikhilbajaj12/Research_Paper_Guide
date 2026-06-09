export interface GeneratedFile {
  file_name: string;
  file_type: string;
  file_path: string;
}

export interface Package {
  package_id: string;
  project_id?: string;
  paper_id: string;
  conference_id: string;
  package_type: string;
  zip_file_path: string;
  generated_files: GeneratedFile[];
  status: string;
  message: string;
}
