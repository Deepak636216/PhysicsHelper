import React from 'react';

const ActionButtons = ({ onHintClick, onSolutionClick, onNewQuestionClick, disabled }) => {
  return (
    <div className="action-buttons">
      <button
        className="action-btn hint"
        onClick={onHintClick}
        disabled={disabled}
      >
        <span className="btn-icon">💡</span> Get Hint
      </button>
      <button
        className="action-btn solution"
        onClick={onSolutionClick}
        disabled={disabled}
      >
        <span className="btn-icon">✓</span> Show Solution
      </button>
      <button
        className="action-btn new-question"
        onClick={onNewQuestionClick}
      >
        <span className="btn-icon">🔄</span> New Question
      </button>
    </div>
  );
};

export default ActionButtons;
