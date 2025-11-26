"""
Test script for the updated JEE Problem MCP Server.

Tests all 11 tools with the new comprehensive problem structure.
"""

import asyncio
import json
import sys
from pathlib import Path
from problem_server import create_problem_server

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


async def test_all_tools():
    """Test all MCP server tools."""

    # Initialize server
    backend_dir = Path(__file__).parent.parent
    problems_dir = backend_dir / "data" / "problems"

    print(f"Initializing server with problems directory: {problems_dir}")
    server_instance = create_problem_server(str(problems_dir))

    print(f"\n{'='*80}")
    print(f"Loaded {server_instance.problems_data['total_problems']} problems")
    print(f"{'='*80}\n")

    # Test 1: Get Statistics
    print("\n[TEST 1] Get Statistics")
    print("-" * 80)
    stats = server_instance._get_statistics()
    print(json.dumps(stats, indent=2))

    # Test 2: List Chapters
    print("\n[TEST 2] List Chapters")
    print("-" * 80)
    chapters = server_instance._list_chapters()
    print(json.dumps(chapters, indent=2))

    # Test 3: Search Problems - by chapter
    print("\n[TEST 3] Search Problems - Centre of Mass")
    print("-" * 80)
    search_results = server_instance._search_problems(chapter="Centre of Mass", limit=5)
    print(json.dumps(search_results, indent=2))

    # Get first problem ID for subsequent tests
    if search_results.get("problems"):
        test_problem_id = search_results["problems"][0]["id"]
    else:
        # Fallback to any problem
        test_problem_id = server_instance.problems_data["problems"][0]["id"]

    print(f"\n\nUsing problem ID for detailed tests: {test_problem_id}")

    # Test 4: Get Problem (without metadata)
    print("\n[TEST 4] Get Problem (Basic Info)")
    print("-" * 80)
    problem = server_instance._get_problem(test_problem_id, include_metadata=False)
    print(json.dumps(problem, indent=2, ensure_ascii=False))

    # Test 5: Get Problem (with metadata)
    print("\n[TEST 5] Get Problem (With Metadata)")
    print("-" * 80)
    problem_with_meta = server_instance._get_problem(test_problem_id, include_metadata=True)
    print(json.dumps(problem_with_meta, indent=2, ensure_ascii=False))

    # Test 6: Get Solution
    print("\n[TEST 6] Get Solution")
    print("-" * 80)
    solution = server_instance._get_solution(test_problem_id)
    print(json.dumps(solution, indent=2, ensure_ascii=False))

    # Test 7: Get Common Mistakes
    print("\n[TEST 7] Get Common Mistakes")
    print("-" * 80)
    mistakes = server_instance._get_common_mistakes(test_problem_id)
    print(json.dumps(mistakes, indent=2, ensure_ascii=False))

    # Test 8: Get Alternative Approaches
    print("\n[TEST 8] Get Alternative Approaches")
    print("-" * 80)
    alternatives = server_instance._get_alternative_approaches(test_problem_id)
    print(json.dumps(alternatives, indent=2, ensure_ascii=False))

    # Test 9: Get Key Insights
    print("\n[TEST 9] Get Key Insights")
    print("-" * 80)
    insights = server_instance._get_key_insights(test_problem_id)
    print(json.dumps(insights, indent=2, ensure_ascii=False))

    # Test 10: Get NCERT Mapping
    print("\n[TEST 10] Get NCERT Mapping")
    print("-" * 80)
    ncert = server_instance._get_ncert_mapping(test_problem_id)
    print(json.dumps(ncert, indent=2, ensure_ascii=False))

    # Test 11: Get Prerequisite Knowledge
    print("\n[TEST 11] Get Prerequisite Knowledge")
    print("-" * 80)
    prereqs = server_instance._get_prerequisite_knowledge(test_problem_id)
    print(json.dumps(prereqs, indent=2, ensure_ascii=False))

    # Test 12: Get Random Problem
    print("\n[TEST 12] Get Random Problem")
    print("-" * 80)
    random_problem = server_instance._get_random_problem(difficulty="medium")
    print(json.dumps(random_problem, indent=2, ensure_ascii=False))

    # Test 13: Search by multiple filters
    print("\n[TEST 13] Search Problems - Multiple Filters")
    print("-" * 80)
    filtered_search = server_instance._search_problems(
        difficulty="medium",
        year=2019,
        limit=5
    )
    print(json.dumps(filtered_search, indent=2, ensure_ascii=False))

    # Test 14: Search by keyword
    print("\n[TEST 14] Search Problems - Keyword Search")
    print("-" * 80)
    keyword_search = server_instance._search_problems(
        query="velocity",
        limit=5
    )
    print(json.dumps(keyword_search, indent=2, ensure_ascii=False))

    print("\n" + "="*80)
    print("All tests completed successfully!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_all_tools())
