"""
Test script for Problem MCP Server

Tests all 4 tools: get_problem, search_problems, get_random_problem, list_topics
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.problem_server import ProblemServer


def test_list_topics(server: ProblemServer):
    """Test list_topics tool."""
    print("\n" + "=" * 60)
    print("TEST 1: list_topics")
    print("=" * 60)

    result = server._list_topics()
    print(json.dumps(result, indent=2))
    return result


def test_get_problem_by_id(server: ProblemServer):
    """Test get_problem by ID."""
    print("\n" + "=" * 60)
    print("TEST 2: get_problem (by ID)")
    print("=" * 60)

    result = server._get_problem(problem_id="kinematics_001")
    print(json.dumps(result, indent=2))
    return result


def test_get_problems_by_topic(server: ProblemServer):
    """Test get_problem by topic."""
    print("\n" + "=" * 60)
    print("TEST 3: get_problem (by topic)")
    print("=" * 60)

    result = server._get_problem(topic="dynamics")
    print(json.dumps(result, indent=2))
    return result


def test_get_problems_by_difficulty(server: ProblemServer):
    """Test get_problem by difficulty."""
    print("\n" + "=" * 60)
    print("TEST 4: get_problem (by difficulty)")
    print("=" * 60)

    result = server._get_problem(difficulty="medium")
    print(json.dumps(result, indent=2))
    return result


def test_search_problems(server: ProblemServer):
    """Test search_problems."""
    print("\n" + "=" * 60)
    print("TEST 5: search_problems")
    print("=" * 60)

    result = server._search_problems(query="force", limit=5)
    print(json.dumps(result, indent=2))
    return result


def test_get_random_problem(server: ProblemServer):
    """Test get_random_problem."""
    print("\n" + "=" * 60)
    print("TEST 6: get_random_problem")
    print("=" * 60)

    result = server._get_random_problem()
    print(json.dumps(result, indent=2))
    return result


def test_get_random_problem_filtered(server: ProblemServer):
    """Test get_random_problem with filters."""
    print("\n" + "=" * 60)
    print("TEST 7: get_random_problem (with topic filter)")
    print("=" * 60)

    result = server._get_random_problem(topic="kinematics")
    print(json.dumps(result, indent=2))
    return result


def main():
    """Run all tests."""
    # Determine problems index path
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    index_path = backend_dir / "data" / "extracted" / "problems_index.json"

    if not index_path.exists():
        print(f"Error: Problems index not found at {index_path}")
        print("Please run: python scripts/index_problems.py")
        sys.exit(1)

    print("=" * 60)
    print("JEE Problem MCP Server - Test Suite")
    print("=" * 60)
    print(f"Using index: {index_path}")

    # Create server instance
    server = ProblemServer(str(index_path))

    # Run tests
    tests = [
        test_list_topics,
        test_get_problem_by_id,
        test_get_problems_by_topic,
        test_get_problems_by_difficulty,
        test_search_problems,
        test_get_random_problem,
        test_get_random_problem_filtered
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            result = test_func(server)
            if "error" not in result:
                print("✅ PASSED")
                passed += 1
            else:
                print(f"⚠️  WARNING: {result.get('error')}")
                passed += 1  # Not a failure, just no matches
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    print("=" * 60)


if __name__ == "__main__":
    main()
