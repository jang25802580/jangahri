import { apiFetch } from './client';
import type { ChatHistoryResponse, ChatQueryRequest, ChatQueryResponse } from '../types/chat';

export async function sendQuery(request: ChatQueryRequest): Promise<ChatQueryResponse> {
  return apiFetch<ChatQueryResponse>('/api/chat/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
}

export async function getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return apiFetch<ChatHistoryResponse>(
    `/api/chat/history?sessionId=${encodeURIComponent(sessionId)}`,
  );
}
