import React, { useState } from 'react';

const InputArea = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <textarea
        id="userInput"
        placeholder="Ask your physics question or work through the problem..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        rows="3"
        disabled={disabled}
      />
      <button
        type="submit"
        id="sendButton"
        disabled={disabled || !input.trim()}
      >
        Send
      </button>
    </form>
  );
};

export default InputArea;
