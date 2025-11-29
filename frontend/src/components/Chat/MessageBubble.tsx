import React, { useState } from 'react';
import { Message, FeedbackRating } from '../../types';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: Message;
  onFeedback: (messageId: string, rating: FeedbackRating, correction?: string) => void;
}

/**
 * Individual message bubble component
 */
function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const [feedbackGiven, setFeedbackGiven] = useState<FeedbackRating | null>(null);
  const [showCorrection, setShowCorrection] = useState(false);
  const [correction, setCorrection] = useState('');

  const isUser = message.role === 'user';
  const isError = message.content.startsWith('Error:');

  const handleFeedback = (rating: FeedbackRating) => {
    if (rating === -1 && !showCorrection) {
      setShowCorrection(true);
      return;
    }
    
    onFeedback(message.id, rating, correction || undefined);
    setFeedbackGiven(rating);
    setShowCorrection(false);
  };

  const submitCorrection = () => {
    onFeedback(message.id, -1, correction);
    setFeedbackGiven(-1);
    setShowCorrection(false);
  };

  // Simple markdown-like formatting for code blocks
  const formatContent = (content: string) => {
    // Handle code blocks
    const parts = content.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const codeContent = part.replace(/```(\w+)?\n?/g, '').replace(/```$/g, '');
        return (
          <pre key={index} className="code-block">
            <code>{codeContent}</code>
          </pre>
        );
      }
      
      // Handle inline code
      const inlineParts = part.split(/(`[^`]+`)/g);
      return inlineParts.map((inline, i) => {
        if (inline.startsWith('`') && inline.endsWith('`')) {
          return <code key={`${index}-${i}`} className="inline-code">{inline.slice(1, -1)}</code>;
        }
        return <span key={`${index}-${i}`}>{inline}</span>;
      });
    });
  };

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'} ${isError ? 'error' : ''}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      
      <div className="message-content">
        <div className="message-text">
          {formatContent(message.content)}
        </div>
        
        {!isUser && !isError && (
          <div className="message-actions">
            {feedbackGiven === null ? (
              <>
                <button
                  className="feedback-btn positive"
                  onClick={() => handleFeedback(1)}
                  title="Good response"
                >
                  👍
                </button>
                <button
                  className="feedback-btn negative"
                  onClick={() => handleFeedback(-1)}
                  title="Bad response"
                >
                  👎
                </button>
              </>
            ) : (
              <span className="feedback-thanks">
                {feedbackGiven === 1 ? '👍 Thanks!' : '👎 Thanks for the feedback'}
              </span>
            )}
            
            {message.tokensUsed && (
              <span className="tokens-used">{message.tokensUsed} tokens</span>
            )}
          </div>
        )}
        
        {showCorrection && (
          <div className="correction-input">
            <textarea
              value={correction}
              onChange={(e) => setCorrection(e.target.value)}
              placeholder="What should the response have been? (optional)"
              rows={3}
            />
            <div className="correction-actions">
              <button onClick={() => setShowCorrection(false)}>Cancel</button>
              <button className="submit-btn" onClick={submitCorrection}>Submit Feedback</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
