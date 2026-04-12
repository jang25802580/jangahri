import { apiFetch } from './client';
import type { StatusResponse, UploadResponse } from '../types/document';

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return apiFetch<UploadResponse>('/api/pdf/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function getDocumentStatus(documentId: string): Promise<StatusResponse> {
  return apiFetch<StatusResponse>(`/api/pdf/status/${encodeURIComponent(documentId)}`);
}

export async function processDocument(documentId: string): Promise<void> {
  await apiFetch<unknown>(`/api/pdf/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId }),
  });
}
