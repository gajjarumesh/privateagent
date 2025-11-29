import React, { useState, useEffect, useRef } from 'react';
import { ModuleType } from '../../types';
import { useChat } from '../../hooks/useChat';
import MessageBubble from './MessageBubble';
import InputBar from './InputBar';
import './ChatWindow.css';

interface ChatWindowProps {
  module: ModuleType;
}

/**
 * Main chat window component
 */
function ChatWindow({ module }: ChatWindowProps) {
  const { messages, isLoading, error, sendMessage, submitFeedback, clearMessages } = useChat(module);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [key, setKey] = useState(0);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Listen for new chat event
  useEffect(() => {
    const handleNewChat = () => {
      clearMessages();
      setKey(k => k + 1);
    };

    window.addEventListener('newChat', handleNewChat);
    return () => window.removeEventListener('newChat', handleNewChat);
  }, [clearMessages]);

  // Clear messages when module changes
  useEffect(() => {
    clearMessages();
  }, [module, clearMessages]);

  const getModuleInfo = () => {
    const info = {
      general: { name: 'General Assistant', icon: '💬', description: 'General purpose AI assistance' },
      developer: { name: 'Developer Assistant', icon: '👨‍💻', description: 'Code generation, debugging, and best practices' },
      trading: { name: 'Trading Analyst', icon: '📈', description: 'Technical analysis and market insights' },
      research: { name: 'Research Engine', icon: '🔬', description: 'Web search and document analysis' },
    };
    return info[module];
  };

  const moduleInfo = getModuleInfo();

  return (
    <div className="chat-window" key={key}>
      <header className="chat-header">
        <div className="module-info">
          <span className="module-icon">{moduleInfo.icon}</span>
          <div>
            <h2 className="module-name">{moduleInfo.name}</h2>
            <p className="module-description">{moduleInfo.description}</p>
          </div>
        </div>
      </header>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">{moduleInfo.icon}</span>
            <h3>Start a conversation</h3>
            <p>Send a message to begin chatting with {moduleInfo.name}</p>
            {module === 'trading' && (
              <p className="disclaimer">
                ⚠️ Trading analysis is for educational purposes only, not financial advice.
              </p>
            )}
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onFeedback={submitFeedback}
              />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="loading-text">Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      <InputBar onSend={sendMessage} isLoading={isLoading} module={module} />
    </div>
  );
}

export default ChatWindow;
