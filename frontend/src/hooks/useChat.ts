/**
 * Custom hook for chat functionality
 */

import { useState, useCallback } from 'react';
import { Message, ModuleType, FeedbackRating } from '../types';
import { chatApi, feedbackApi } from '../services/api';

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  sendMessage: (content: string) => Promise<void>;
  submitFeedback: (messageId: string, rating: FeedbackRating, correction?: string) => Promise<void>;
  clearMessages: () => void;
  setError: (error: string | null) => void;
}

/**
 * Hook for managing chat state and operations
 */
export function useChat(module: ModuleType): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  /**
   * Send a message to the chat
   */
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      module,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await chatApi.sendMessage({
        message: content,
        sessionId: sessionId || undefined,
        module,
      });

      // Update session ID if new
      if (!sessionId) {
        setSessionId(response.sessionId);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        module,
        tokensUsed: response.tokensUsed,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      
      // Add error message
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        timestamp: new Date().toISOString(),
        module,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [module, sessionId]);

  /**
   * Submit feedback for a message
   */
  const submitFeedback = useCallback(async (
    messageId: string,
    rating: FeedbackRating,
    correction?: string
  ) => {
    if (!sessionId) return;

    try {
      await feedbackApi.submit({
        sessionId,
        messageId,
        rating,
        correction,
        module,
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  }, [sessionId, module]);

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    submitFeedback,
    clearMessages,
    setError,
  };
}

export default useChat;
