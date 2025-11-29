/**
 * Type definitions for ARIA frontend
 */

/** Module types */
export type ModuleType = 'general' | 'developer' | 'trading' | 'research';

/** Message role */
export type MessageRole = 'user' | 'assistant' | 'system';

/** Message interface */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  module?: ModuleType;
  tokensUsed?: number;
}

/** Conversation interface */
export interface Conversation {
  id: string;
  sessionId: string;
  title: string;
  module: ModuleType;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
}

/** Chat request */
export interface ChatRequest {
  message: string;
  sessionId?: string;
  module: ModuleType;
}

/** Chat response */
export interface ChatResponse {
  response: string;
  sessionId: string;
  module: ModuleType;
  tokensUsed?: number;
}

/** Feedback rating */
export type FeedbackRating = -1 | 0 | 1;

/** Feedback request */
export interface FeedbackRequest {
  sessionId: string;
  messageId: string;
  rating: FeedbackRating;
  correction?: string;
  module: ModuleType;
}

/** Feedback response */
export interface FeedbackResponse {
  message: string;
  feedbackId: string;
}

/** Trading analysis request */
export interface AnalysisRequest {
  symbol: string;
  period?: string;
  indicators?: string[];
}

/** Trading analysis response */
export interface AnalysisResponse {
  symbol: string;
  currentPrice?: number;
  analysis: Record<string, unknown>;
  indicators: Record<string, unknown>;
  recommendation: string;
  disclaimer: string;
}

/** Research search request */
export interface SearchRequest {
  query: string;
  maxResults?: number;
}

/** Search result */
export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
}

/** Search response */
export interface SearchResponse {
  query: string;
  results: SearchResult[];
  summary?: string;
}

/** Agent status */
export interface AgentStatus {
  status: 'healthy' | 'degraded' | 'unavailable';
  llm: {
    status: string;
  };
  memory: {
    sessions: number;
  };
}

/** App state */
export interface AppState {
  currentModule: ModuleType;
  currentSessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
