import React from 'react';

const Header = ({ onToggleSidebar, hintsUsed, maxHints, progress }) => {
  return (
    <header className="header-compact">
      <div className="header-left">
        <button className="sidebar-toggle" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          <span className="hamburger-icon">☰</span>
        </button>
        <div className="logo-compact">
          <span className="logo-icon">🎓</span>
          <h1>JEE Physics Tutor</h1>
        </div>
      </div>

      <div className="header-right">
        {hintsUsed > 0 && (
          <span className="header-badge hints-badge">
            💡 {hintsUsed}/{maxHints}
          </span>
        )}
        {progress > 0 && (
          <span className="header-badge progress-badge">
            📊 {progress}%
          </span>
        )}
      </div>
    </header>
  );
};

export default Header;
