export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface DocumentRecord {
  id: string;
  type: string;
  file_name: string;
  blob_url: string;
  status: DocumentStatus;
  uploaded_at: string;
  processed_at: string | null;
  size: number;
  page_count: number;
  chunk_count: number;
  progress: number;
  description: string | null;
  error: string | null;
}

export interface UploadResponse {
  document_id: string;
  file_name: string;
  status: DocumentStatus;
  uploaded_at: string;
}

export interface StatusResponse {
  document_id: string;
  status: DocumentStatus;
  progress: number;
  chunk_count: number;
  error: string | null;
}
