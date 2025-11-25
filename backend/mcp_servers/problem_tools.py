"""
Problem Tools - Standalone Implementation

Core logic for problem tools that can be used independently
or wrapped in MCP server protocol.

This provides the 4 tools:
1. get_problem - Get specific problem by ID or filter by topic/difficulty
2. search_problems - Search problems by keywords
3. get_random_problem - Get random problem with optional filters
4. list_topics - List all available topics and statistics
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProblemTools:
    """Core problem tool implementations."""

    def __init__(self, problems_index_path: str):
        """
        Initialize problem tools.

        Args:
            problems_index_path: Path to problems_index.json
        """
        self.problems_index_path = Path(problems_index_path)
        self.problems_data = self._load_problems()

    def _load_problems(self) -> Dict[str, Any]:
        """Load the problems index."""
        if not self.problems_index_path.exists():
            raise FileNotFoundError(f"Problems index not found: {self.problems_index_path}")

        with open(self.problems_index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _filter_problems(
        self,
        problems: List[Dict],
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Filter problems by topic and/or difficulty."""
        filtered = problems

        if topic:
            filtered = [p for p in filtered if p.get("topic", "").lower() == topic.lower()]

        if difficulty:
            filtered = [p for p in filtered if p.get("difficulty", "").lower() == difficulty.lower()]

        return filtered

    def get_problem(
        self,
        problem_id: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get problem(s) by ID or filters.

        Args:
            problem_id: Specific problem ID
            topic: Filter by topic
            difficulty: Filter by difficulty

        Returns:
            Problem details WITHOUT solution initially (only question and hints)
        """
        problems = self.problems_data.get("problems", [])

        # If problem_id specified, return that specific problem
        if problem_id:
            for problem in problems:
                if problem.get("id") == problem_id:
                    # Return without solution (only show on request)
                    return {
                        "id": problem["id"],
                        "topic": problem["topic"],
                        "difficulty": problem["difficulty"],
                        "question": problem["question"],
                        "hints": problem["hints"]
                    }
            return {"error": f"Problem not found: {problem_id}"}

        # Otherwise filter and return list
        filtered = self._filter_problems(problems, topic, difficulty)

        if not filtered:
            return {
                "error": "No problems found matching criteria",
                "criteria": {"topic": topic, "difficulty": difficulty}
            }

        # Return list without solutions
        results = []
        for p in filtered:
            results.append({
                "id": p["id"],
                "topic": p["topic"],
                "difficulty": p["difficulty"],
                "question": p["question"],
                "hints": p["hints"]
            })

        return {
            "count": len(results),
            "problems": results
        }

    def search_problems(
        self,
        query: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search problems by keywords.

        Args:
            query: Search keywords
            topic: Optional topic filter
            difficulty: Optional difficulty filter
            limit: Maximum number of results

        Returns:
            Matching problems
        """
        problems = self.problems_data.get("problems", [])

        # Filter by topic/difficulty first
        filtered = self._filter_problems(problems, topic, difficulty)

        # Search in question text
        query_lower = query.lower()
        matches = []

        for problem in filtered:
            question_text = problem.get("question", "").lower()
            if query_lower in question_text:
                matches.append({
                    "id": problem["id"],
                    "topic": problem["topic"],
                    "difficulty": problem["difficulty"],
                    "question": problem["question"],
                    "hints": problem["hints"]
                })

        # Limit results
        matches = matches[:limit]

        return {
            "query": query,
            "count": len(matches),
            "problems": matches
        }

    def get_random_problem(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a random problem.

        Args:
            topic: Optional topic filter
            difficulty: Optional difficulty filter

        Returns:
            Random problem
        """
        problems = self.problems_data.get("problems", [])

        # Filter
        filtered = self._filter_problems(problems, topic, difficulty)

        if not filtered:
            return {
                "error": "No problems found matching criteria",
                "criteria": {"topic": topic, "difficulty": difficulty}
            }

        # Select random
        problem = random.choice(filtered)

        return {
            "id": problem["id"],
            "topic": problem["topic"],
            "difficulty": problem["difficulty"],
            "question": problem["question"],
            "hints": problem["hints"]
        }

    def list_topics(self) -> Dict[str, Any]:
        """
        List all available topics with counts.

        Returns:
            Topics, difficulties, and total problem count
        """
        return {
            "total_problems": self.problems_data.get("total_problems", 0),
            "topics": self.problems_data.get("topics", {}),
            "difficulties": self.problems_data.get("difficulties", {})
        }


def create_problem_tools(problems_index_path: str) -> ProblemTools:
    """
    Factory function to create ProblemTools.

    Args:
        problems_index_path: Path to problems_index.json

    Returns:
        Initialized ProblemTools instance
    """
    return ProblemTools(problems_index_path)


# Example usage and testing
if __name__ == "__main__":
    import sys

    # Determine problems index path
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    index_path = backend_dir / "data" / "extracted" / "problems_index.json"

    if not index_path.exists():
        print(f"Error: Problems index not found at {index_path}")
        print("Please run: python scripts/index_problems.py")
        sys.exit(1)

    print("=" * 60)
    print("Problem Tools - Test Suite")
    print("=" * 60)

    # Create tools instance
    tools = create_problem_tools(str(index_path))

    # Test 1: List topics
    print("\nTest 1: list_topics()")
    print("-" * 60)
    result = tools.list_topics()
    print(json.dumps(result, indent=2))

    # Test 2: Get problem by ID
    print("\nTest 2: get_problem(problem_id='kinematics_001')")
    print("-" * 60)
    result = tools.get_problem(problem_id="kinematics_001")
    print(json.dumps(result, indent=2))

    # Test 3: Get problems by topic
    print("\nTest 3: get_problem(topic='dynamics')")
    print("-" * 60)
    result = tools.get_problem(topic="dynamics")
    print(json.dumps(result, indent=2))

    # Test 4: Search problems
    print("\nTest 4: search_problems(query='force')")
    print("-" * 60)
    result = tools.search_problems(query="force")
    print(json.dumps(result, indent=2))

    # Test 5: Get random problem
    print("\nTest 5: get_random_problem()")
    print("-" * 60)
    result = tools.get_random_problem()
    print(json.dumps(result, indent=2))

    # Test 6: Get random problem with filter
    print("\nTest 6: get_random_problem(difficulty='medium')")
    print("-" * 60)
    result = tools.get_random_problem(difficulty="medium")
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
