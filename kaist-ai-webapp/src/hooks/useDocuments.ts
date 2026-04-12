import { useMutation, useQuery } from '@tanstack/react-query';
import { getDocumentStatus, uploadDocument } from '../api/documents';
import type { StatusResponse, UploadResponse } from '../types/document';

export function useDocumentStatus(documentId: string | null) {
  return useQuery<StatusResponse>({
    queryKey: ['documentStatus', documentId],
    queryFn: () => getDocumentStatus(documentId!),
    enabled: documentId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'completed' || status === 'failed') return false;
      return 5_000;
    },
  });
}

export function useUploadDocument() {
  return useMutation<UploadResponse, Error, File>({
    mutationFn: (file: File) => uploadDocument(file),
  });
}
