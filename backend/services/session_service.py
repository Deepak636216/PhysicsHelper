"""
Session Service

Tracks student conversations with context persistence.
Manages session lifecycle and state updates.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json


class SessionService:
    """
    Service for managing student tutoring sessions.

    Features:
    - Session creation and retrieval
    - State persistence
    - Automatic cleanup of inactive sessions
    - Conversation history tracking
    """

    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize the session service.

        Args:
            session_timeout_minutes: Minutes of inactivity before session expires (default: 60)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

    def create_student_session(
        self,
        student_id: str,
        topic: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new student session.

        Args:
            student_id: Unique student identifier
            topic: Optional initial topic
            initial_state: Optional initial state dictionary

        Returns:
            session_id: Unique session identifier
        """
        # Generate unique session ID
        timestamp = int(datetime.now().timestamp())
        session_id = f"{student_id}_{timestamp}"

        # Create session object
        now = datetime.now().isoformat()
        session = {
            "session_id": session_id,
            "student_id": student_id,
            "created_at": now,
            "last_active": now,
            "state": initial_state or {
                "current_topic": topic,
                "current_problem_id": None,
                "interaction_count": 0,
                "hints_provided": 0,
                "tools_used": [],
                "agents_used": [],
                "conversation_history": []
            }
        }

        # Store session
        self.sessions[session_id] = session

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary or None if not found/expired
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if session has expired
        last_active = datetime.fromisoformat(session["last_active"])
        if datetime.now() - last_active > self.session_timeout:
            # Session expired, remove it
            del self.sessions[session_id]
            return None

        # Update last active time
        session["last_active"] = datetime.now().isoformat()

        return session

    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session state.

        Args:
            session_id: Session identifier
            updates: Dictionary of state updates

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        # Update state fields
        for key, value in updates.items():
            if key in session["state"]:
                session["state"][key] = value
            else:
                session["state"][key] = value

        # Update last active time
        session["last_active"] = datetime.now().isoformat()

        return True

    def increment_interaction(self, session_id: str) -> bool:
        """
        Increment interaction count.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        session["state"]["interaction_count"] += 1
        session["last_active"] = datetime.now().isoformat()

        return True

    def add_to_history(
        self,
        session_id: str,
        entry: Dict[str, Any]
    ) -> bool:
        """
        Add entry to conversation history.

        Args:
            session_id: Session identifier
            entry: History entry (role, message, agent, etc.)

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        # Add timestamp if not present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()

        session["state"]["conversation_history"].append(entry)
        session["last_active"] = datetime.now().isoformat()

        return True

    def record_agent_usage(
        self,
        session_id: str,
        agent_name: str
    ) -> bool:
        """
        Record that an agent was used in this session.

        Args:
            session_id: Session identifier
            agent_name: Name of agent used

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        if agent_name not in session["state"]["agents_used"]:
            session["state"]["agents_used"].append(agent_name)

        session["last_active"] = datetime.now().isoformat()

        return True

    def record_tool_usage(
        self,
        session_id: str,
        tool_name: str
    ) -> bool:
        """
        Record that a tool was used in this session.

        Args:
            session_id: Session identifier
            tool_name: Name of tool used

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        if tool_name not in session["state"]["tools_used"]:
            session["state"]["tools_used"].append(tool_name)

        session["last_active"] = datetime.now().isoformat()

        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Summary dictionary or None if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        created = datetime.fromisoformat(session["created_at"])
        last_active = datetime.fromisoformat(session["last_active"])
        duration = (last_active - created).total_seconds() / 60  # minutes

        return {
            "session_id": session_id,
            "student_id": session["student_id"],
            "duration_minutes": round(duration, 2),
            "interaction_count": session["state"]["interaction_count"],
            "hints_provided": session["state"]["hints_provided"],
            "agents_used": session["state"]["agents_used"],
            "tools_used": session["state"]["tools_used"],
            "current_topic": session["state"]["current_topic"],
            "conversation_length": len(session["state"]["conversation_history"])
        }

    def cleanup_inactive_sessions(self) -> int:
        """
        Remove all inactive/expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            last_active = datetime.fromisoformat(session["last_active"])
            if now - last_active > self.session_timeout:
                expired_sessions.append(session_id)

        # Remove expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]

        return len(expired_sessions)

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of all active sessions.

        Returns:
            List of session summaries
        """
        # Cleanup first
        self.cleanup_inactive_sessions()

        summaries = []
        for session_id in self.sessions.keys():
            summary = self.get_session_summary(session_id)
            if summary:
                summaries.append(summary)

        return summaries

    def get_student_sessions(self, student_id: str) -> List[str]:
        """
        Get all active session IDs for a student.

        Args:
            student_id: Student identifier

        Returns:
            List of session IDs
        """
        session_ids = []

        for session_id, session in self.sessions.items():
            if session["student_id"] == student_id:
                # Check if still active
                if self.get_session(session_id) is not None:
                    session_ids.append(session_id)

        return session_ids

    def delete_session(self, session_id: str) -> bool:
        """
        Explicitly delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Session Service - Test Suite")
    print("=" * 70)

    # Create service
    service = SessionService(session_timeout_minutes=60)

    # Test 1: Create session
    print("\n" + "=" * 70)
    print("Test 1: Create Student Session")
    print("=" * 70)
    session_id = service.create_student_session(
        student_id="student_123",
        topic="kinematics"
    )
    print(f"✅ Created session: {session_id}")

    # Test 2: Retrieve session
    print("\n" + "=" * 70)
    print("Test 2: Retrieve Session")
    print("=" * 70)
    session = service.get_session(session_id)
    print(f"✅ Retrieved session:")
    print(json.dumps(session, indent=2))

    # Test 3: Update session state
    print("\n" + "=" * 70)
    print("Test 3: Update Session State")
    print("=" * 70)
    success = service.update_session(session_id, {
        "current_problem_id": "kinematics_001",
        "hints_provided": 2
    })
    print(f"✅ Updated session: {success}")
    session = service.get_session(session_id)
    print(f"   Current problem: {session['state']['current_problem_id']}")
    print(f"   Hints provided: {session['state']['hints_provided']}")

    # Test 4: Increment interactions
    print("\n" + "=" * 70)
    print("Test 4: Increment Interaction Count")
    print("=" * 70)
    for i in range(5):
        service.increment_interaction(session_id)
    session = service.get_session(session_id)
    print(f"✅ Interaction count: {session['state']['interaction_count']}")

    # Test 5: Add to conversation history
    print("\n" + "=" * 70)
    print("Test 5: Add to Conversation History")
    print("=" * 70)
    service.add_to_history(session_id, {
        "role": "user",
        "message": "I need help with kinematics",
        "agent": "socratic_tutor"
    })
    service.add_to_history(session_id, {
        "role": "agent",
        "message": "What do you understand about motion?",
        "agent": "socratic_tutor"
    })
    session = service.get_session(session_id)
    print(f"✅ Conversation history length: {len(session['state']['conversation_history'])}")

    # Test 6: Record agent usage
    print("\n" + "=" * 70)
    print("Test 6: Record Agent Usage")
    print("=" * 70)
    service.record_agent_usage(session_id, "socratic_tutor")
    service.record_agent_usage(session_id, "physics_calculator")
    session = service.get_session(session_id)
    print(f"✅ Agents used: {session['state']['agents_used']}")

    # Test 7: Record tool usage
    print("\n" + "=" * 70)
    print("Test 7: Record Tool Usage")
    print("=" * 70)
    service.record_tool_usage(session_id, "problem_mcp")
    session = service.get_session(session_id)
    print(f"✅ Tools used: {session['state']['tools_used']}")

    # Test 8: Get session summary
    print("\n" + "=" * 70)
    print("Test 8: Get Session Summary")
    print("=" * 70)
    summary = service.get_session_summary(session_id)
    print("✅ Session Summary:")
    print(json.dumps(summary, indent=2))

    # Test 9: Create multiple sessions
    print("\n" + "=" * 70)
    print("Test 9: Multiple Sessions")
    print("=" * 70)
    session_id_2 = service.create_student_session("student_456", "dynamics")
    session_id_3 = service.create_student_session("student_123", "energy")
    print(f"✅ Created 2 more sessions")

    # Test 10: List active sessions
    print("\n" + "=" * 70)
    print("Test 10: List Active Sessions")
    print("=" * 70)
    active = service.list_active_sessions()
    print(f"✅ Active sessions: {len(active)}")
    for sess in active:
        print(f"   - {sess['session_id'][:30]}... ({sess['student_id']}, {sess['current_topic']})")

    # Test 11: Get student sessions
    print("\n" + "=" * 70)
    print("Test 11: Get Sessions for Student")
    print("=" * 70)
    student_sessions = service.get_student_sessions("student_123")
    print(f"✅ Sessions for student_123: {len(student_sessions)}")

    # Test 12: Delete session
    print("\n" + "=" * 70)
    print("Test 12: Delete Session")
    print("=" * 70)
    deleted = service.delete_session(session_id_2)
    print(f"✅ Deleted session: {deleted}")
    active = service.list_active_sessions()
    print(f"   Active sessions remaining: {len(active)}")

    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nSession Service Features Demonstrated:")
    print("  ✓ Session creation with student ID and topic")
    print("  ✓ Session retrieval with expiration checking")
    print("  ✓ State updates (problem ID, hints, etc.)")
    print("  ✓ Interaction counting")
    print("  ✓ Conversation history tracking")
    print("  ✓ Agent usage recording")
    print("  ✓ Tool usage recording")
    print("  ✓ Session summaries with statistics")
    print("  ✓ Multi-session management")
    print("  ✓ Student session lookup")
    print("  ✓ Session deletion")
    print("=" * 70)
