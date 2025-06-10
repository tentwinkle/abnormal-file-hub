export interface File {
  id: string;
  original_filename: string;
  file_type: string;
  size: number;
  uploaded_at: string;
  file: string;
}

export interface FileQueryParams {
  search?: string;
  file_type?: string;
  size_min?: number;
  size_max?: number;
  date_from?: string;
  date_to?: string;
}
