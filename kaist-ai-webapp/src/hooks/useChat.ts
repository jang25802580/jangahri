import { useMutation, useQuery } from '@tanstack/react-query';
import { getChatHistory, sendQuery } from '../api/chat';
import type { ChatHistoryResponse, ChatQueryRequest, ChatQueryResponse } from '../types/chat';

export function useChatHistory(sessionId: string) {
  return useQuery<ChatHistoryResponse>({
    queryKey: ['chatHistory', sessionId],
    queryFn: () => getChatHistory(sessionId),
  });
}

export function useSendQuery() {
  return useMutation<ChatQueryResponse, Error, ChatQueryRequest>({
    mutationFn: (request: ChatQueryRequest) => sendQuery(request),
  });
}
