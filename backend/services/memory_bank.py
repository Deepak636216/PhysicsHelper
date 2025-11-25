"""
Memory Bank Service

Stores student learning profiles and history using file-based JSON storage.
Tracks topic mastery, session history, and preferences.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class MemoryBank:
    """
    File-based memory storage for student profiles and learning history.

    Features:
    - Student profile creation and retrieval
    - Topic mastery tracking
    - Session history recording
    - Auto-save on updates
    - JSON-based persistent storage
    """

    def __init__(self, storage_dir: str = "backend/data/memory"):
        """
        Initialize the memory bank.

        Args:
            storage_dir: Directory for storing profile JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _get_profile_path(self, student_id: str) -> Path:
        """Get file path for student profile."""
        return self.storage_dir / f"{student_id}.json"

    def _load_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Load profile from file.

        Args:
            student_id: Student identifier

        Returns:
            Profile dictionary or None if not found
        """
        profile_path = self._get_profile_path(student_id)

        if not profile_path.exists():
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profile {student_id}: {e}")
            return None

    def _save_profile(self, student_id: str, profile: Dict[str, Any]) -> bool:
        """
        Save profile to file.

        Args:
            student_id: Student identifier
            profile: Profile dictionary

        Returns:
            True if successful
        """
        profile_path = self._get_profile_path(student_id)

        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving profile {student_id}: {e}")
            return False

    def create_student_profile(
        self,
        student_id: str,
        preferences: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new student profile.

        Args:
            student_id: Unique student identifier
            preferences: Optional initial preferences

        Returns:
            Created profile dictionary
        """
        profile = {
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "topic_mastery": {},
            "session_history": [],
            "preferences": preferences or {
                "difficulty_level": "medium",
                "learning_pace": "moderate"
            }
        }

        # Save to file
        self._save_profile(student_id, profile)

        # Cache it
        self.cache[student_id] = profile

        return profile

    def get_student_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get student profile (from cache or file).

        Args:
            student_id: Student identifier

        Returns:
            Profile dictionary or None if not found
        """
        # Check cache first
        if student_id in self.cache:
            return self.cache[student_id]

        # Load from file
        profile = self._load_profile(student_id)

        if profile:
            self.cache[student_id] = profile

        return profile

    def update_topic_mastery(
        self,
        student_id: str,
        topic: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update mastery information for a topic.

        Args:
            student_id: Student identifier
            topic: Physics topic (e.g., 'kinematics')
            updates: Dictionary of mastery updates

        Returns:
            True if successful
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            # Create profile if doesn't exist
            profile = self.create_student_profile(student_id)

        # Initialize topic if not present
        if topic not in profile["topic_mastery"]:
            profile["topic_mastery"][topic] = {
                "level": "beginner",
                "problems_attempted": 0,
                "problems_correct": 0,
                "weak_areas": [],
                "strong_areas": [],
                "last_practiced": None
            }

        # Update fields
        for key, value in updates.items():
            profile["topic_mastery"][topic][key] = value

        # Update last practiced
        profile["topic_mastery"][topic]["last_practiced"] = datetime.now().isoformat()

        # Save
        return self._save_profile(student_id, profile)

    def increment_problem_stats(
        self,
        student_id: str,
        topic: str,
        correct: bool
    ) -> bool:
        """
        Increment problem attempt/correct counters.

        Args:
            student_id: Student identifier
            topic: Physics topic
            correct: Whether problem was solved correctly

        Returns:
            True if successful
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            profile = self.create_student_profile(student_id)

        # Initialize topic if needed
        if topic not in profile["topic_mastery"]:
            profile["topic_mastery"][topic] = {
                "level": "beginner",
                "problems_attempted": 0,
                "problems_correct": 0,
                "weak_areas": [],
                "strong_areas": [],
                "last_practiced": None
            }

        # Increment counters
        profile["topic_mastery"][topic]["problems_attempted"] += 1
        if correct:
            profile["topic_mastery"][topic]["problems_correct"] += 1

        # Update mastery level based on success rate
        attempted = profile["topic_mastery"][topic]["problems_attempted"]
        correct_count = profile["topic_mastery"][topic]["problems_correct"]

        if attempted >= 10:
            success_rate = correct_count / attempted
            if success_rate >= 0.8:
                profile["topic_mastery"][topic]["level"] = "advanced"
            elif success_rate >= 0.5:
                profile["topic_mastery"][topic]["level"] = "intermediate"
            else:
                profile["topic_mastery"][topic]["level"] = "beginner"

        profile["topic_mastery"][topic]["last_practiced"] = datetime.now().isoformat()

        return self._save_profile(student_id, profile)

    def add_session_history(
        self,
        student_id: str,
        session_data: Dict[str, Any]
    ) -> bool:
        """
        Add session to history.

        Args:
            student_id: Student identifier
            session_data: Session summary data

        Returns:
            True if successful
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            profile = self.create_student_profile(student_id)

        # Add date if not present
        if "date" not in session_data:
            session_data["date"] = datetime.now().isoformat()

        profile["session_history"].append(session_data)

        return self._save_profile(student_id, profile)

    def get_topic_mastery(
        self,
        student_id: str,
        topic: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get mastery information for a specific topic.

        Args:
            student_id: Student identifier
            topic: Physics topic

        Returns:
            Topic mastery dictionary or None
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            return None

        return profile["topic_mastery"].get(topic)

    def get_recent_sessions(
        self,
        student_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent session history.

        Args:
            student_id: Student identifier
            limit: Maximum number of sessions to return

        Returns:
            List of recent sessions (newest first)
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            return []

        # Return most recent sessions
        return profile["session_history"][-limit:][::-1]

    def get_weak_areas(self, student_id: str) -> List[str]:
        """
        Get list of all weak areas across topics.

        Args:
            student_id: Student identifier

        Returns:
            List of weak area identifiers
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            return []

        weak_areas = []
        for topic, mastery in profile["topic_mastery"].items():
            weak_areas.extend(mastery.get("weak_areas", []))

        return list(set(weak_areas))  # Remove duplicates

    def update_preferences(
        self,
        student_id: str,
        preferences: Dict[str, str]
    ) -> bool:
        """
        Update student preferences.

        Args:
            student_id: Student identifier
            preferences: Preference updates

        Returns:
            True if successful
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            profile = self.create_student_profile(student_id, preferences)
            return True

        profile["preferences"].update(preferences)

        return self._save_profile(student_id, profile)

    def get_learning_stats(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get overall learning statistics.

        Args:
            student_id: Student identifier

        Returns:
            Statistics dictionary
        """
        profile = self.get_student_profile(student_id)

        if profile is None:
            return None

        total_attempted = 0
        total_correct = 0
        topics_count = len(profile["topic_mastery"])

        for topic, mastery in profile["topic_mastery"].items():
            total_attempted += mastery["problems_attempted"]
            total_correct += mastery["problems_correct"]

        success_rate = (total_correct / total_attempted * 100) if total_attempted > 0 else 0

        return {
            "student_id": student_id,
            "total_sessions": len(profile["session_history"]),
            "topics_studied": topics_count,
            "total_problems_attempted": total_attempted,
            "total_problems_correct": total_correct,
            "overall_success_rate": round(success_rate, 1),
            "weak_areas": self.get_weak_areas(student_id)
        }

    def list_all_students(self) -> List[str]:
        """
        Get list of all student IDs with profiles.

        Returns:
            List of student IDs
        """
        student_ids = []

        for file_path in self.storage_dir.glob("*.json"):
            student_id = file_path.stem
            student_ids.append(student_id)

        return sorted(student_ids)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Memory Bank Service - Test Suite")
    print("=" * 70)

    # Create memory bank (use test directory)
    memory = MemoryBank(storage_dir="backend/data/memory_test")

    # Test 1: Create student profile
    print("\n" + "=" * 70)
    print("Test 1: Create Student Profile")
    print("=" * 70)
    profile = memory.create_student_profile("student_123")
    print(f"✅ Created profile for: {profile['student_id']}")
    print(f"   Created at: {profile['created_at']}")
    print(f"   Preferences: {profile['preferences']}")

    # Test 2: Retrieve profile
    print("\n" + "=" * 70)
    print("Test 2: Retrieve Student Profile")
    print("=" * 70)
    retrieved = memory.get_student_profile("student_123")
    print(f"✅ Retrieved profile: {retrieved is not None}")
    print(f"   Student ID: {retrieved['student_id']}")

    # Test 3: Update topic mastery
    print("\n" + "=" * 70)
    print("Test 3: Update Topic Mastery")
    print("=" * 70)
    memory.update_topic_mastery("student_123", "kinematics", {
        "level": "intermediate",
        "weak_areas": ["circular_motion"],
        "strong_areas": ["linear_motion"]
    })
    profile = memory.get_student_profile("student_123")
    print(f"✅ Updated kinematics mastery:")
    print(json.dumps(profile["topic_mastery"]["kinematics"], indent=2))

    # Test 4: Increment problem stats
    print("\n" + "=" * 70)
    print("Test 4: Increment Problem Statistics")
    print("=" * 70)
    # Simulate solving problems
    for i in range(15):
        correct = i % 3 != 0  # 2/3 correct
        memory.increment_problem_stats("student_123", "kinematics", correct)

    mastery = memory.get_topic_mastery("student_123", "kinematics")
    print(f"✅ Kinematics stats:")
    print(f"   Attempted: {mastery['problems_attempted']}")
    print(f"   Correct: {mastery['problems_correct']}")
    print(f"   Level: {mastery['level']}")

    # Test 5: Add session history
    print("\n" + "=" * 70)
    print("Test 5: Add Session History")
    print("=" * 70)
    memory.add_session_history("student_123", {
        "session_id": "sess_001",
        "topic": "kinematics",
        "problems_attempted": 5,
        "hints_used": 2,
        "duration_minutes": 30
    })
    memory.add_session_history("student_123", {
        "session_id": "sess_002",
        "topic": "dynamics",
        "problems_attempted": 3,
        "hints_used": 1,
        "duration_minutes": 20
    })
    profile = memory.get_student_profile("student_123")
    print(f"✅ Session history count: {len(profile['session_history'])}")

    # Test 6: Get recent sessions
    print("\n" + "=" * 70)
    print("Test 6: Get Recent Sessions")
    print("=" * 70)
    recent = memory.get_recent_sessions("student_123", limit=5)
    print(f"✅ Recent sessions: {len(recent)}")
    for sess in recent:
        print(f"   - {sess['session_id']}: {sess['topic']}")

    # Test 7: Get weak areas
    print("\n" + "=" * 70)
    print("Test 7: Get Weak Areas")
    print("=" * 70)
    weak = memory.get_weak_areas("student_123")
    print(f"✅ Weak areas: {weak}")

    # Test 8: Update preferences
    print("\n" + "=" * 70)
    print("Test 8: Update Preferences")
    print("=" * 70)
    memory.update_preferences("student_123", {
        "difficulty_level": "hard",
        "learning_pace": "fast"
    })
    profile = memory.get_student_profile("student_123")
    print(f"✅ Updated preferences: {profile['preferences']}")

    # Test 9: Get learning stats
    print("\n" + "=" * 70)
    print("Test 9: Get Learning Statistics")
    print("=" * 70)
    stats = memory.get_learning_stats("student_123")
    print("✅ Learning Statistics:")
    print(json.dumps(stats, indent=2))

    # Test 10: Multiple students
    print("\n" + "=" * 70)
    print("Test 10: Multiple Students")
    print("=" * 70)
    memory.create_student_profile("student_456")
    memory.create_student_profile("student_789")
    students = memory.list_all_students()
    print(f"✅ Total students: {len(students)}")
    print(f"   Students: {students}")

    # Test 11: File persistence
    print("\n" + "=" * 70)
    print("Test 11: File Persistence")
    print("=" * 70)
    # Create new memory bank instance (should load from files)
    memory2 = MemoryBank(storage_dir="backend/data/memory_test")
    profile2 = memory2.get_student_profile("student_123")
    print(f"✅ Loaded from file: {profile2 is not None}")
    print(f"   Sessions: {len(profile2['session_history'])}")
    print(f"   Topics: {len(profile2['topic_mastery'])}")

    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nMemory Bank Features Demonstrated:")
    print("  ✓ Student profile creation")
    print("  ✓ Profile retrieval with caching")
    print("  ✓ Topic mastery tracking")
    print("  ✓ Problem statistics (attempted/correct)")
    print("  ✓ Automatic level calculation")
    print("  ✓ Session history recording")
    print("  ✓ Recent sessions retrieval")
    print("  ✓ Weak areas aggregation")
    print("  ✓ Preference management")
    print("  ✓ Learning statistics")
    print("  ✓ Multi-student support")
    print("  ✓ File-based persistence")
    print("=" * 70)
