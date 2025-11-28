/**
 * Conversation Logger Utility
 * Stores all conversation data locally for analysis and enhancement
 */

class ConversationLogger {
  constructor() {
    this.logKey = 'jee_conversation_logs';
    this.currentSessionLog = null;
  }

  /**
   * Start a new conversation session
   */
  startSession(sessionId, studentId) {
    this.currentSessionLog = {
      session_id: sessionId,
      student_id: studentId,
      started_at: new Date().toISOString(),
      messages: [],
      interactions: [],
      hints_requested: 0,
      solution_requested: false,
      metadata: {
        browser: navigator.userAgent,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
      }
    };
  }

  /**
   * Update session ID (for when it's created after first message)
   */
  updateSessionId(sessionId) {
    if (this.currentSessionLog) {
      this.currentSessionLog.session_id = sessionId;
    }
  }

  /**
   * Log a message exchange
   */
  logMessage(messageData) {
    if (!this.currentSessionLog) return;

    const logEntry = {
      timestamp: new Date().toISOString(),
      type: messageData.type || 'chat',
      role: messageData.role,
      content: messageData.content,
      metadata: messageData.metadata || {}
    };

    this.currentSessionLog.messages.push(logEntry);
  }

  /**
   * Log a user interaction (hint request, solution request, etc.)
   */
  logInteraction(interactionType, data = {}) {
    if (!this.currentSessionLog) return;

    const interaction = {
      timestamp: new Date().toISOString(),
      type: interactionType,
      data: data
    };

    this.currentSessionLog.interactions.push(interaction);

    // Update counters
    if (interactionType === 'hint_request') {
      this.currentSessionLog.hints_requested++;
    } else if (interactionType === 'solution_request') {
      this.currentSessionLog.solution_requested = true;
    }
  }

  /**
   * Log progress updates
   */
  logProgress(progressData) {
    if (!this.currentSessionLog) return;

    this.logInteraction('progress_update', {
      progress_score: progressData.progress_score,
      hints_used: progressData.hints_used,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log an error
   */
  logError(errorType, errorMessage, errorData = {}) {
    if (!this.currentSessionLog) return;

    this.logInteraction('error', {
      error_type: errorType,
      error_message: errorMessage,
      error_data: errorData
    });
  }

  /**
   * End the current session and save to localStorage
   */
  endSession(finalMetadata = {}) {
    if (!this.currentSessionLog) {
      console.warn('[ConversationLogger] No active session to end');
      return;
    }

    this.currentSessionLog.ended_at = new Date().toISOString();
    this.currentSessionLog.duration_seconds = Math.floor(
      (new Date(this.currentSessionLog.ended_at) - new Date(this.currentSessionLog.started_at)) / 1000
    );
    this.currentSessionLog.final_metadata = finalMetadata;

    console.log('[ConversationLogger] Ending session:', {
      session_id: this.currentSessionLog.session_id,
      messages: this.currentSessionLog.messages.length,
      duration: this.currentSessionLog.duration_seconds
    });

    // Save to localStorage
    this._saveToPersistentStorage();

    // Reset current session
    this.currentSessionLog = null;
  }

  /**
   * Save current session to localStorage
   */
  _saveToPersistentStorage() {
    if (!this.currentSessionLog) return;

    try {
      // Get existing logs
      const existingLogs = this.getAllLogs();

      // Add new log
      existingLogs.push(this.currentSessionLog);

      // Keep only last 100 sessions to avoid localStorage overflow
      const logsToKeep = existingLogs.slice(-100);

      // Save back to localStorage
      localStorage.setItem(this.logKey, JSON.stringify(logsToKeep));

      console.log('[ConversationLogger] Saved to localStorage:', {
        total_logs: logsToKeep.length,
        this_session_messages: this.currentSessionLog.messages.length
      });
    } catch (error) {
      console.error('[ConversationLogger] Error saving conversation log:', error);
    }
  }

  /**
   * Get all logged conversations
   */
  getAllLogs() {
    try {
      const logs = localStorage.getItem(this.logKey);
      return logs ? JSON.parse(logs) : [];
    } catch (error) {
      console.error('Error reading conversation logs:', error);
      return [];
    }
  }

  /**
   * Get logs for a specific student
   */
  getStudentLogs(studentId) {
    const allLogs = this.getAllLogs();
    return allLogs.filter(log => log.student_id === studentId);
  }

  /**
   * Get logs within a date range
   */
  getLogsByDateRange(startDate, endDate) {
    const allLogs = this.getAllLogs();
    return allLogs.filter(log => {
      const logDate = new Date(log.started_at);
      return logDate >= startDate && logDate <= endDate;
    });
  }

  /**
   * Export logs as JSON file
   */
  exportLogsAsJSON() {
    const logs = this.getAllLogs();
    const dataStr = JSON.stringify(logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `jee-conversation-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Export logs as CSV file
   */
  exportLogsAsCSV() {
    const logs = this.getAllLogs();

    // CSV headers
    const headers = [
      'Session ID',
      'Student ID',
      'Started At',
      'Ended At',
      'Duration (seconds)',
      'Message Count',
      'Hints Requested',
      'Solution Requested',
      'Screen Resolution',
      'Viewport'
    ];

    // CSV rows
    const rows = logs.map(log => [
      log.session_id || '',
      log.student_id || '',
      log.started_at || '',
      log.ended_at || '',
      log.duration_seconds || 0,
      log.messages.length,
      log.hints_requested,
      log.solution_requested ? 'Yes' : 'No',
      log.metadata?.screen_resolution || '',
      log.metadata?.viewport || ''
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Download
    const dataBlob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `jee-conversation-summary-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Get analytics summary
   */
  getAnalyticsSummary() {
    const logs = this.getAllLogs();

    return {
      total_sessions: logs.length,
      total_messages: logs.reduce((sum, log) => sum + log.messages.length, 0),
      total_hints_requested: logs.reduce((sum, log) => sum + log.hints_requested, 0),
      total_solutions_requested: logs.filter(log => log.solution_requested).length,
      avg_messages_per_session: logs.length > 0
        ? (logs.reduce((sum, log) => sum + log.messages.length, 0) / logs.length).toFixed(2)
        : 0,
      avg_session_duration: logs.length > 0
        ? (logs.reduce((sum, log) => sum + (log.duration_seconds || 0), 0) / logs.length).toFixed(2)
        : 0,
      sessions_by_date: this._groupSessionsByDate(logs)
    };
  }

  /**
   * Helper: Group sessions by date
   */
  _groupSessionsByDate(logs) {
    const grouped = {};
    logs.forEach(log => {
      const date = log.started_at.split('T')[0];
      grouped[date] = (grouped[date] || 0) + 1;
    });
    return grouped;
  }

  /**
   * Clear all logs (use with caution!)
   */
  clearAllLogs() {
    if (confirm('Are you sure you want to clear all conversation logs? This cannot be undone.')) {
      localStorage.removeItem(this.logKey);
      return true;
    }
    return false;
  }

  /**
   * Get current session log (for debugging)
   */
  getCurrentSession() {
    return this.currentSessionLog;
  }
}

// Create singleton instance
const conversationLogger = new ConversationLogger();

export default conversationLogger;
