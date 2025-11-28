import React from 'react';

const WelcomeMessage = () => {
  return (
    <div className="welcome-message">
      <h2>Welcome to JEE Physics Tutor! 🎓</h2>
      <p>
        I'm your AI-powered physics tutor designed specifically for JEE Advanced preparation.
        Let's work together to master challenging physics problems!
      </p>

      <div className="features">
        <div className="feature">
          <span className="feature-icon">💡</span>
          <div className="feature-text">
            <strong>Progressive Hints</strong>
            <p>Get up to 3 levels of hints to guide your thinking</p>
          </div>
        </div>

        <div className="feature">
          <span className="feature-icon">📊</span>
          <div className="feature-text">
            <strong>Progress Tracking</strong>
            <p>See your understanding grow with real-time progress</p>
          </div>
        </div>

        <div className="feature">
          <span className="feature-icon">✓</span>
          <div className="feature-text">
            <strong>Solution Unlock</strong>
            <p>Earn full solutions by demonstrating 50% understanding</p>
          </div>
        </div>

        <div className="feature">
          <span className="feature-icon">🎯</span>
          <div className="feature-text">
            <strong>Guided Learning</strong>
            <p>Learn through Socratic questioning and conceptual clarity</p>
          </div>
        </div>
      </div>

      <div className="getting-started">
        <h3>Getting Started:</h3>
        <ul>
          <li>Ask me any JEE physics problem</li>
          <li>Work through the solution step-by-step with my guidance</li>
          <li>Use hints when you're stuck (max 3 per problem)</li>
          <li>Unlock the full solution when you reach 50% progress</li>
        </ul>
      </div>
    </div>
  );
};

export default WelcomeMessage;
