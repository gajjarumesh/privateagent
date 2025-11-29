import React, { useState, KeyboardEvent } from 'react';
import { ModuleType } from '../../types';
import './InputBar.css';

interface InputBarProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  module: ModuleType;
}

/**
 * Input bar for sending messages
 */
function InputBar({ onSend, isLoading, module }: InputBarProps) {
  const [message, setMessage] = useState('');

  const getPlaceholder = () => {
    const placeholders = {
      general: 'Ask me anything...',
      developer: 'Ask about code, debugging, best practices...',
      trading: 'Ask about technical analysis, indicators...',
      research: 'Search the web or ask about documents...',
    };
    return placeholders[module];
  };

  const handleSubmit = () => {
    if (message.trim() && !isLoading) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="input-bar">
      <div className="input-container">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={getPlaceholder()}
          disabled={isLoading}
          rows={1}
          className="message-input"
        />
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || isLoading}
          className="send-btn"
        >
          {isLoading ? (
            <span className="loading-spinner">⏳</span>
          ) : (
            <span>➤</span>
          )}
        </button>
      </div>
      <p className="input-hint">
        Press Enter to send, Shift+Enter for new line. All AI processing runs locally via Ollama.
      </p>
    </div>
  );
}

export default InputBar;
