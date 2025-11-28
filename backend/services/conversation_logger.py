"""
Conversation Logger Service
Stores conversation logs for analysis and enhancement
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConversationLogger:
    """Service for logging and managing conversation data"""

    def __init__(self, log_dir: str = "backend/data/conversation_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_conversation(self, conversation_data: Dict) -> str:
        """
        Log a complete conversation session

        Args:
            conversation_data: Dictionary containing session data

        Returns:
            str: Path to the saved log file
        """
        try:
            # Generate filename
            session_id = conversation_data.get('session_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{session_id}.json"
            filepath = self.log_dir / filename

            # Add server-side metadata
            conversation_data['logged_at'] = datetime.now().isoformat()
            conversation_data['log_version'] = '1.0'

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            return str(filepath)

        except Exception as e:
            print(f"Error logging conversation: {e}")
            return ""

    def get_all_logs(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all conversation logs

        Args:
            limit: Optional limit on number of logs to return

        Returns:
            List of conversation log dictionaries
        """
        logs = []

        try:
            # Get all JSON files sorted by modification time (newest first)
            log_files = sorted(
                self.log_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            # Apply limit if specified
            if limit:
                log_files = log_files[:limit]

            # Read each log file
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                        logs.append(log_data)
                except Exception as e:
                    print(f"Error reading log file {log_file}: {e}")

        except Exception as e:
            print(f"Error retrieving logs: {e}")

        return logs

    def get_logs_by_student(self, student_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get logs for a specific student"""
        all_logs = self.get_all_logs()
        student_logs = [log for log in all_logs if log.get('student_id') == student_id]

        if limit:
            student_logs = student_logs[:limit]

        return student_logs

    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get logs within a date range (YYYY-MM-DD format)"""
        all_logs = self.get_all_logs()

        filtered_logs = []
        for log in all_logs:
            log_date = log.get('started_at', '')[:10]  # Extract YYYY-MM-DD
            if start_date <= log_date <= end_date:
                filtered_logs.append(log)

        return filtered_logs

    def get_analytics_summary(self) -> Dict:
        """Get analytics summary of all conversations"""
        logs = self.get_all_logs()

        total_messages = sum(len(log.get('messages', [])) for log in logs)
        total_hints = sum(log.get('hints_requested', 0) for log in logs)
        total_solutions = sum(1 for log in logs if log.get('solution_requested', False))

        # Calculate averages
        avg_messages = total_messages / len(logs) if logs else 0
        avg_duration = sum(log.get('duration_seconds', 0) for log in logs) / len(logs) if logs else 0

        # Group by date
        sessions_by_date = {}
        for log in logs:
            date = log.get('started_at', '')[:10]
            sessions_by_date[date] = sessions_by_date.get(date, 0) + 1

        return {
            'total_sessions': len(logs),
            'total_messages': total_messages,
            'total_hints_requested': total_hints,
            'total_solutions_requested': total_solutions,
            'avg_messages_per_session': round(avg_messages, 2),
            'avg_session_duration_seconds': round(avg_duration, 2),
            'sessions_by_date': sessions_by_date,
            'unique_students': len(set(log.get('student_id') for log in logs if log.get('student_id')))
        }

    def export_logs_as_csv(self, output_file: Optional[str] = None) -> str:
        """Export all logs as CSV"""
        import csv

        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = str(self.log_dir / f"conversation_export_{timestamp}.csv")

        logs = self.get_all_logs()

        # CSV headers
        headers = [
            'session_id', 'student_id', 'started_at', 'ended_at',
            'duration_seconds', 'message_count', 'hints_requested',
            'solution_requested', 'screen_resolution', 'viewport'
        ]

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

                for log in logs:
                    writer.writerow({
                        'session_id': log.get('session_id', ''),
                        'student_id': log.get('student_id', ''),
                        'started_at': log.get('started_at', ''),
                        'ended_at': log.get('ended_at', ''),
                        'duration_seconds': log.get('duration_seconds', 0),
                        'message_count': len(log.get('messages', [])),
                        'hints_requested': log.get('hints_requested', 0),
                        'solution_requested': log.get('solution_requested', False),
                        'screen_resolution': log.get('metadata', {}).get('screen_resolution', ''),
                        'viewport': log.get('metadata', {}).get('viewport', '')
                    })

            return output_file

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""

    def clear_old_logs(self, days_to_keep: int = 30) -> int:
        """Clear logs older than specified days"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        try:
            for log_file in self.log_dir.glob("*.json"):
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1

        except Exception as e:
            print(f"Error clearing old logs: {e}")

        return deleted_count
