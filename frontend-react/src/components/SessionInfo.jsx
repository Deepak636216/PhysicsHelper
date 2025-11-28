import React from 'react';

const SessionInfo = ({ hintsUsed, maxHints, progress }) => {
  return (
    <div className="session-info">
      <span id="hintsInfo">
        Hints: <span className="badge">{hintsUsed}/{maxHints}</span>
      </span>
      <span id="progressInfo">
        Progress: <span className="badge">{progress}%</span>
      </span>
      <div className="progress-container" id="progressContainer">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default SessionInfo;
