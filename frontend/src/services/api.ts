/**
 * API service for ARIA backend communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  FeedbackRequest,
  FeedbackResponse,
  AnalysisRequest,
  AnalysisResponse,
  SearchRequest,
  SearchResponse,
  AgentStatus,
} from '../types';

// API base URL from environment or default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minute timeout for LLM requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleApiError = (error: AxiosError): never => {
  if (error.response) {
    const message = (error.response.data as { detail?: string })?.detail || 'An error occurred';
    throw new Error(message);
  } else if (error.request) {
    throw new Error('Unable to connect to server. Please check if the backend is running.');
  } else {
    throw new Error(error.message);
  }
};

/**
 * Chat API
 */
export const chatApi = {
  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/api/chat/', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Get chat history for a session
   */
  async getHistory(sessionId: string): Promise<{ history: Array<{ role: string; content: string }> }> {
    try {
      const response = await api.get(`/api/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Clear chat history for a session
   */
  async clearHistory(sessionId: string): Promise<void> {
    try {
      await api.delete(`/api/chat/history/${sessionId}`);
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },
};

/**
 * Feedback API
 */
export const feedbackApi = {
  /**
   * Submit feedback for a message
   */
  async submit(request: FeedbackRequest): Promise<FeedbackResponse> {
    try {
      const response = await api.post<FeedbackResponse>('/api/feedback/submit', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Get feedback statistics
   */
  async getStats(module?: string): Promise<Record<string, unknown>> {
    try {
      const params = module ? { module } : {};
      const response = await api.get('/api/feedback/stats', { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },
};

/**
 * Trading API
 */
export const tradingApi = {
  /**
   * Analyze a trading symbol
   */
  async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await api.post<AnalysisResponse>('/api/trading/analyze', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Get quote for a symbol
   */
  async getQuote(symbol: string): Promise<Record<string, unknown>> {
    try {
      const response = await api.get(`/api/trading/quote/${symbol}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },
};

/**
 * Research API
 */
export const researchApi = {
  /**
   * Perform web search
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    try {
      const response = await api.post<SearchResponse>('/api/research/search', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Ingest a document
   */
  async ingestDocument(content: string, source?: string): Promise<{ documentId: string }> {
    try {
      const response = await api.post('/api/research/ingest', { content, source });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },

  /**
   * Query documents
   */
  async query(question: string, sessionId?: string): Promise<{ answer: string; sources: string[] }> {
    try {
      const response = await api.post('/api/research/query', { question, sessionId });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },
};

/**
 * Health/Status API
 */
export const statusApi = {
  /**
   * Check API health
   */
  async getHealth(): Promise<{ status: string; version: string }> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError);
    }
  },
};

export default api;
