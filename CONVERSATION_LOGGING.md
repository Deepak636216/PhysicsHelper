# Conversation Logging System

## Overview

The JEE Physics Tutor application now includes a comprehensive conversation logging system that tracks all user interactions for analysis and application enhancement. Logs are stored both locally (in browser localStorage) and can be sent to the backend for persistent storage.

## Features

### 1. **Automatic Logging**
- Every message exchange (user and assistant)
- Hint requests and responses
- Solution requests and results
- Progress updates
- Error events
- Session metadata (browser, screen resolution, viewport)

### 2. **Local Storage (Frontend)**
- Logs stored in browser localStorage
- Keeps last 100 sessions automatically
- Survives page refreshes
- Accessible via browser DevTools or analytics page

### 3. **Backend Storage**
- Persistent storage in JSON format
- Organized by timestamp and session ID
- Located in: `backend/data/conversation_logs/`
- CSV export capability

### 4. **Analytics Dashboard**
- Access at: `http://localhost:3000/analytics.html`
- View statistics:
  - Total sessions
  - Total messages
  - Hints requested
  - Average session duration
- Export logs (JSON/CSV)
- View detailed log table
- Clear all logs

## How It Works

### Frontend Logging

#### Automatic Session Tracking
```javascript
// Session starts when first message is sent
conversationLogger.startSession(sessionId, studentId);

// Each message is logged automatically
conversationLogger.logMessage({
  role: 'user',
  content: 'What is Newton\'s second law?',
  type: 'chat'
});

// Interactions logged
conversationLogger.logInteraction('hint_request');
conversationLogger.logInteraction('solution_request');

// Progress updates logged
conversationLogger.logProgress({
  progress_score: 45,
  hints_used: 2
});

// Session ends when new chat is started
conversationLogger.endSession({
  final_progress: 75,
  final_hints_used: 3
});
```

### Backend API Endpoints

#### 1. Log Conversation
```http
POST /api/log-conversation
Content-Type: application/json

{
  "session_id": "sess_123",
  "student_id": "student_456",
  "started_at": "2025-01-15T10:00:00Z",
  "ended_at": "2025-01-15T10:15:30Z",
  "duration_seconds": 930,
  "messages": [...],
  "interactions": [...],
  "hints_requested": 2,
  "solution_requested": true,
  "metadata": {...}
}
```

#### 2. Get All Logs
```http
GET /api/conversation-logs?limit=50
```

#### 3. Get Student Logs
```http
GET /api/conversation-logs/student/{student_id}?limit=20
```

#### 4. Get Analytics
```http
GET /api/conversation-analytics
```

## Log Data Structure

### Session Log Format
```json
{
  "session_id": "sess_20250115_103045",
  "student_id": "student_1736932800_abc123",
  "started_at": "2025-01-15T10:30:45.123Z",
  "ended_at": "2025-01-15T10:45:30.456Z",
  "duration_seconds": 885,
  "messages": [
    {
      "timestamp": "2025-01-15T10:30:50.123Z",
      "type": "chat",
      "role": "user",
      "content": "A ball is thrown upward...",
      "metadata": {}
    },
    {
      "timestamp": "2025-01-15T10:31:05.456Z",
      "type": "chat",
      "role": "assistant",
      "content": "Let's analyze this projectile motion problem...",
      "metadata": {
        "agent_used": "socratic_tutor",
        "confidence": 0.95
      }
    }
  ],
  "interactions": [
    {
      "timestamp": "2025-01-15T10:35:00.000Z",
      "type": "hint_request",
      "data": {}
    },
    {
      "timestamp": "2025-01-15T10:40:00.000Z",
      "type": "progress_update",
      "data": {
        "progress_score": 45,
        "hints_used": 1
      }
    }
  ],
  "hints_requested": 1,
  "solution_requested": false,
  "metadata": {
    "browser": "Mozilla/5.0...",
    "screen_resolution": "1920x1080",
    "viewport": "1272x594"
  },
  "final_metadata": {
    "final_progress": 60,
    "final_hints_used": 1
  }
}
```

## Usage Examples

### Viewing Analytics
1. Open your browser to `http://localhost:3000/analytics.html`
2. View session statistics
3. Click "View Logs" to see detailed table
4. Export data as JSON or CSV

### Accessing Logs Programmatically

#### Browser Console
```javascript
// Get logger instance
import conversationLogger from './utils/conversationLogger';

// Get all logs
const allLogs = conversationLogger.getAllLogs();
console.log('Total sessions:', allLogs.length);

// Get analytics summary
const analytics = conversationLogger.getAnalyticsSummary();
console.log('Analytics:', analytics);

// Export logs
conversationLogger.exportLogsAsJSON();  // Downloads JSON file
conversationLogger.exportLogsAsCSV();   // Downloads CSV file
```

#### Python (Backend)
```python
from services.conversation_logger import ConversationLogger

logger = ConversationLogger()

# Get all logs
logs = logger.get_all_logs(limit=100)

# Get analytics
analytics = logger.get_analytics_summary()

# Export to CSV
logger.export_logs_as_csv('output.csv')
```

## Data Analysis Use Cases

### 1. **User Behavior Analysis**
- Average session length
- Messages per session
- Hint usage patterns
- Solution unlock timing

### 2. **Learning Patterns**
- Progress trajectory
- Concept mastery
- Common misconceptions
- Help-seeking behavior

### 3. **System Performance**
- Response times
- Error rates
- Agent selection patterns
- Confidence scores

### 4. **A/B Testing**
- Compare different tutoring strategies
- Test new hint formats
- Evaluate solution unlock thresholds

### 5. **Student Profiling**
- Identify struggling students
- Track improvement over time
- Personalize learning paths

## Privacy & Data Management

### Local Storage Limits
- Automatically keeps last 100 sessions
- Older sessions deleted automatically
- User can clear all logs from analytics page

### Backend Storage
- Logs stored as individual JSON files
- Files named: `{timestamp}_{session_id}.json`
- Can be backed up, archived, or deleted
- CSV export for easy analysis in Excel/Google Sheets

### Clearing Old Logs (Backend)
```python
from services.conversation_logger import ConversationLogger

logger = ConversationLogger()

# Delete logs older than 30 days
deleted_count = logger.clear_old_logs(days_to_keep=30)
print(f'Deleted {deleted_count} old logs')
```

## Best Practices

### 1. **Regular Exports**
- Export logs weekly for backup
- Store in version control or cloud storage
- Use CSV for spreadsheet analysis
- Use JSON for programmatic analysis

### 2. **Analysis Workflow**
```bash
# 1. Export from frontend
# Visit http://localhost:3000/analytics.html
# Click "Export as JSON"

# 2. Analyze with Python
import json
import pandas as pd

with open('logs.json') as f:
    logs = json.load(f)

df = pd.DataFrame([{
    'session_id': log['session_id'],
    'messages': len(log['messages']),
    'duration': log.get('duration_seconds', 0),
    'hints': log['hints_requested']
} for log in logs])

print(df.describe())
```

### 3. **Monitoring**
- Check analytics dashboard weekly
- Look for unusual patterns
- Identify common error points
- Track average session metrics

## Troubleshooting

### Logs Not Appearing
1. Check browser console for errors
2. Verify localStorage is enabled
3. Check that sessions are starting (first message sent)

### Backend Not Logging
1. Verify `backend/data/conversation_logs/` directory exists
2. Check file permissions
3. Review backend logs for errors

### Analytics Page Not Loading
1. Ensure development server is running
2. Clear browser cache
3. Check browser console for JavaScript errors

## Future Enhancements

Potential improvements for the logging system:

1. **Real-time Sync**: Automatically sync logs to backend
2. **Advanced Analytics**: Machine learning insights
3. **Visualization**: Charts and graphs
4. **Search**: Filter logs by content, date, student
5. **Comparison**: Side-by-side session comparison
6. **Alerts**: Notify when patterns indicate issues

## API Reference

### Frontend (conversationLogger)

| Method | Description |
|--------|-------------|
| `startSession(sessionId, studentId)` | Start logging a new session |
| `logMessage(messageData)` | Log a message exchange |
| `logInteraction(type, data)` | Log user interaction |
| `logProgress(progressData)` | Log progress update |
| `logError(type, message, data)` | Log error event |
| `endSession(finalMetadata)` | End session and save |
| `getAllLogs()` | Get all stored logs |
| `getAnalyticsSummary()` | Get analytics summary |
| `exportLogsAsJSON()` | Download logs as JSON |
| `exportLogsAsCSV()` | Download logs as CSV |
| `clearAllLogs()` | Clear all logs (with confirmation) |

### Backend (ConversationLogger)

| Method | Description |
|--------|-------------|
| `log_conversation(data)` | Save conversation to file |
| `get_all_logs(limit)` | Get all logs (newest first) |
| `get_logs_by_student(student_id, limit)` | Get student's logs |
| `get_logs_by_date_range(start, end)` | Get logs in date range |
| `get_analytics_summary()` | Get analytics summary |
| `export_logs_as_csv(output_file)` | Export to CSV |
| `clear_old_logs(days_to_keep)` | Delete old logs |

## Support

For issues or questions about the logging system:
1. Check this documentation
2. Review backend logs
3. Inspect browser console
4. Check file permissions on backend

---

**Note**: This logging system is designed for development and analysis. For production deployments, consider implementing proper data protection, anonymization, and compliance with privacy regulations (GDPR, CCPA, etc.).
