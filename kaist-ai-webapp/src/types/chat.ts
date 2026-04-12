export type MessageRole = 'user' | 'assistant';

export interface SourceReference {
  document_id: string;
  file_name: string;
  chunk_id: string;
  relevance_score: number;
  excerpt: string;
}

export interface ChatMessage {
  message_id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  sources: SourceReference[];
}

export interface ChatQueryRequest {
  query: string;
  session_id?: string;
  document_ids?: string[];
}

export interface ChatQueryResponse {
  answer: string;
  sources: SourceReference[];
  message_id: string;
  timestamp: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
}
