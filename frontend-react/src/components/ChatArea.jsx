import React, { useRef, useEffect } from 'react';
import Message from './Message';
import WelcomeMessage from './WelcomeMessage';

const ChatArea = ({ messages, showWelcome, isLoading }) => {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-area" id="chatArea">
      {showWelcome && <WelcomeMessage />}
      {messages.map((msg, index) => (
        <Message
          key={index}
          role={msg.role}
          content={msg.content}
          type={msg.type}
        />
      ))}
      {isLoading && (
        <div className="message assistant-message">
          <span className="message-icon">🤖</span>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatArea;
