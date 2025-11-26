"""
JEE Problem MCP Server

MCP server that provides comprehensive tools for accessing the JEE physics problem bank.
Supports detailed problem metadata including:
- Official solutions with step-by-step explanations
- Common mistakes and misconceptions
- NCERT mappings and prerequisite knowledge
- Multiple approaches and key insights
- Chapter-wise organization (Centre of Mass, Laws of Motion, Rotation, Work-Power-Energy)

Exposes 10+ tools for rich problem exploration and learning.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class ProblemServer:
    """MCP Server for JEE Physics problems with comprehensive metadata."""

    def __init__(self, problems_dir: str):
        """
        Initialize the problem server.

        Args:
            problems_dir: Path to directory containing problem JSON files
        """
        self.problems_dir = Path(problems_dir)
        self.problems_data = self._load_all_problems()
        self.server = Server("jee-problem-server")
        self._register_handlers()

    def _load_all_problems(self) -> Dict[str, Any]:
        """Load all problem files from the problems directory."""
        all_problems = []
        chapters = {}
        topics = {}
        difficulties = {"easy": 0, "medium": 0, "hard": 0}
        exams = {}
        years = {}

        # Load all JSON files in the problems directory
        for json_file in self.problems_dir.glob("*.json"):
            if json_file.name == "problems_index.json":
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_problems = json.load(f)

                    # Handle both list and dict formats
                    if isinstance(file_problems, list):
                        problems_list = file_problems
                    elif isinstance(file_problems, dict) and "problems" in file_problems:
                        problems_list = file_problems["problems"]
                    else:
                        continue

                    # Add source file info and collect stats
                    for problem in problems_list:
                        problem["source_file"] = json_file.stem
                        all_problems.append(problem)

                        # Collect statistics
                        chapter = problem.get("chapter", "Unknown")
                        chapters[chapter] = chapters.get(chapter, 0) + 1

                        topic = problem.get("topic", "Unknown")
                        topics[topic] = topics.get(topic, 0) + 1

                        difficulty = problem.get("difficulty", "medium")
                        if difficulty in difficulties:
                            difficulties[difficulty] += 1

                        exam = problem.get("exam", "Unknown")
                        exams[exam] = exams.get(exam, 0) + 1

                        year = problem.get("year")
                        if year:
                            years[str(year)] = years.get(str(year), 0) + 1

            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue

        return {
            "problems": all_problems,
            "total_problems": len(all_problems),
            "chapters": chapters,
            "topics": topics,
            "difficulties": difficulties,
            "exams": exams,
            "years": years
        }

    def _register_handlers(self):
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_problem",
                    description="Get problem question and hints (without solution initially)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID (e.g., 'COM_Q1_VELOCITY_CM')"
                            },
                            "include_metadata": {
                                "type": "boolean",
                                "description": "Include concepts, formulas, NCERT mapping",
                                "default": False
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_solution",
                    description="Get detailed step-by-step solution for a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_common_mistakes",
                    description="Get common mistakes and correct approaches for a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_alternative_approaches",
                    description="Get alternative solution methods for a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_key_insights",
                    description="Get key insights and learning points from a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="search_problems",
                    description="Search problems by keywords, chapter, topic, difficulty, year, or exam",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search keywords (searches in question text)"
                            },
                            "chapter": {
                                "type": "string",
                                "description": "Chapter (e.g., 'Centre of Mass', 'Laws of Motion')"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Specific topic"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "easy, medium, or hard"
                            },
                            "year": {
                                "type": "integer",
                                "description": "JEE year"
                            },
                            "exam": {
                                "type": "string",
                                "description": "Exam type (e.g., 'JEE Main', 'JEE Advanced')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results (default: 10)",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="get_random_problem",
                    description="Get a random practice problem with filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chapter": {
                                "type": "string",
                                "description": "Filter by chapter"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "Filter by difficulty"
                            },
                            "year": {
                                "type": "integer",
                                "description": "Filter by year"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_chapters",
                    description="Get all available chapters with problem counts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_ncert_mapping",
                    description="Get NCERT textbook mapping for a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_prerequisite_knowledge",
                    description="Get prerequisite concepts needed for a problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID"
                            }
                        },
                        "required": ["problem_id"]
                    }
                ),
                Tool(
                    name="get_statistics",
                    description="Get overall statistics about the problem bank",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            tool_map = {
                "get_problem": lambda: self._get_problem(
                    problem_id=arguments["problem_id"],
                    include_metadata=arguments.get("include_metadata", False)
                ),
                "get_solution": lambda: self._get_solution(arguments["problem_id"]),
                "get_common_mistakes": lambda: self._get_common_mistakes(arguments["problem_id"]),
                "get_alternative_approaches": lambda: self._get_alternative_approaches(arguments["problem_id"]),
                "get_key_insights": lambda: self._get_key_insights(arguments["problem_id"]),
                "search_problems": lambda: self._search_problems(
                    query=arguments.get("query"),
                    chapter=arguments.get("chapter"),
                    topic=arguments.get("topic"),
                    difficulty=arguments.get("difficulty"),
                    year=arguments.get("year"),
                    exam=arguments.get("exam"),
                    limit=arguments.get("limit", 10)
                ),
                "get_random_problem": lambda: self._get_random_problem(
                    chapter=arguments.get("chapter"),
                    difficulty=arguments.get("difficulty"),
                    year=arguments.get("year")
                ),
                "list_chapters": lambda: self._list_chapters(),
                "get_ncert_mapping": lambda: self._get_ncert_mapping(arguments["problem_id"]),
                "get_prerequisite_knowledge": lambda: self._get_prerequisite_knowledge(arguments["problem_id"]),
                "get_statistics": lambda: self._get_statistics()
            }

            if name in tool_map:
                result = tool_map[name]()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

    def _find_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Find a problem by ID."""
        problems = self.problems_data.get("problems", [])
        for problem in problems:
            if problem.get("id") == problem_id:
                return problem
        return None

    def _get_problem(
        self,
        problem_id: str,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Get problem question and hints (without solution).
        Optionally include concepts, formulas, and NCERT mapping.
        """
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        result = {
            "id": problem["id"],
            "chapter": problem.get("chapter", "Unknown"),
            "topic": problem.get("topic", "Unknown"),
            "difficulty": problem.get("difficulty", "medium"),
            "marks": problem.get("marks", 0),
            "year": problem.get("year"),
            "exam": problem.get("exam"),
            "date": problem.get("date"),
            "question": problem.get("text", problem.get("question", "")),
            "type": problem.get("type", "objective_single_correct"),
            "options": problem.get("options", [])
        }

        if include_metadata:
            result.update({
                "concepts_required": problem.get("concepts_required", []),
                "formulas_used": problem.get("formulas_used", []),
                "ncert_mapping": problem.get("ncert_mapping", {}),
                "given_data": problem.get("given_data", {}),
                "subtopics": problem.get("subtopics", [])
            })

        return result

    def _get_solution(self, problem_id: str) -> Dict[str, Any]:
        """Get detailed step-by-step solution."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "correct_answer": problem.get("correct_answer"),
            "numerical_answer": problem.get("numerical_answer"),
            "units": problem.get("units"),
            "official_solution": problem.get("official_solution", {}),
            "answer_justification": problem.get("official_solution", {}).get("answer_justification", "")
        }

    def _get_common_mistakes(self, problem_id: str) -> Dict[str, Any]:
        """Get common mistakes and correct approaches."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "common_mistakes": problem.get("common_mistakes", [])
        }

    def _get_alternative_approaches(self, problem_id: str) -> Dict[str, Any]:
        """Get alternative solution methods."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "alternative_approaches": problem.get("alternative_approaches", [])
        }

    def _get_key_insights(self, problem_id: str) -> Dict[str, Any]:
        """Get key insights and learning points."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "key_insights": problem.get("key_insights", []),
            "prerequisite_knowledge": problem.get("prerequisite_knowledge", []),
            "related_problems": problem.get("related_problems", [])
        }

    def _search_problems(
        self,
        query: Optional[str] = None,
        chapter: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        year: Optional[int] = None,
        exam: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search problems with multiple filters."""
        problems = self.problems_data.get("problems", [])
        filtered = problems

        # Apply filters
        if chapter:
            filtered = [p for p in filtered if p.get("chapter", "").lower() == chapter.lower()]

        if topic:
            filtered = [p for p in filtered if topic.lower() in p.get("topic", "").lower()]

        if difficulty:
            filtered = [p for p in filtered if p.get("difficulty", "").lower() == difficulty.lower()]

        if year:
            filtered = [p for p in filtered if p.get("year") == year]

        if exam:
            filtered = [p for p in filtered if exam.lower() in p.get("exam", "").lower()]

        if query:
            query_lower = query.lower()
            filtered = [p for p in filtered if query_lower in p.get("text", "").lower()]

        # Format results
        results = []
        for p in filtered[:limit]:
            results.append({
                "id": p["id"],
                "chapter": p.get("chapter"),
                "topic": p.get("topic"),
                "difficulty": p.get("difficulty"),
                "year": p.get("year"),
                "exam": p.get("exam"),
                "question": p.get("text", "")[:200] + "..." if len(p.get("text", "")) > 200 else p.get("text", "")
            })

        return {
            "filters": {
                "query": query,
                "chapter": chapter,
                "topic": topic,
                "difficulty": difficulty,
                "year": year,
                "exam": exam
            },
            "count": len(results),
            "total_matches": len([p for p in problems if self._matches_filters(p, chapter, topic, difficulty, year, exam, query)]),
            "problems": results
        }

    def _matches_filters(self, problem, chapter, topic, difficulty, year, exam, query):
        """Check if problem matches all filters."""
        if chapter and problem.get("chapter", "").lower() != chapter.lower():
            return False
        if topic and topic.lower() not in problem.get("topic", "").lower():
            return False
        if difficulty and problem.get("difficulty", "").lower() != difficulty.lower():
            return False
        if year and problem.get("year") != year:
            return False
        if exam and exam.lower() not in problem.get("exam", "").lower():
            return False
        if query and query.lower() not in problem.get("text", "").lower():
            return False
        return True

    def _get_random_problem(
        self,
        chapter: Optional[str] = None,
        difficulty: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a random problem with filters."""
        problems = self.problems_data.get("problems", [])
        filtered = problems

        if chapter:
            filtered = [p for p in filtered if p.get("chapter", "").lower() == chapter.lower()]
        if difficulty:
            filtered = [p for p in filtered if p.get("difficulty", "").lower() == difficulty.lower()]
        if year:
            filtered = [p for p in filtered if p.get("year") == year]

        if not filtered:
            return {
                "error": "No problems found matching criteria",
                "criteria": {"chapter": chapter, "difficulty": difficulty, "year": year}
            }

        problem = random.choice(filtered)
        return self._get_problem(problem["id"], include_metadata=False)

    def _list_chapters(self) -> Dict[str, Any]:
        """List all available chapters with statistics."""
        return {
            "total_problems": self.problems_data.get("total_problems", 0),
            "chapters": self.problems_data.get("chapters", {}),
            "topics": self.problems_data.get("topics", {}),
            "difficulties": self.problems_data.get("difficulties", {}),
            "exams": self.problems_data.get("exams", {}),
            "years": self.problems_data.get("years", {})
        }

    def _get_ncert_mapping(self, problem_id: str) -> Dict[str, Any]:
        """Get NCERT textbook mapping."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "ncert_mapping": problem.get("ncert_mapping", {})
        }

    def _get_prerequisite_knowledge(self, problem_id: str) -> Dict[str, Any]:
        """Get prerequisite concepts."""
        problem = self._find_problem(problem_id)
        if not problem:
            return {"error": f"Problem not found: {problem_id}"}

        return {
            "id": problem["id"],
            "prerequisite_knowledge": problem.get("prerequisite_knowledge", []),
            "concepts_required": problem.get("concepts_required", [])
        }

    def _get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about the problem bank."""
        return {
            "total_problems": self.problems_data.get("total_problems", 0),
            "by_chapter": self.problems_data.get("chapters", {}),
            "by_topic": self.problems_data.get("topics", {}),
            "by_difficulty": self.problems_data.get("difficulties", {}),
            "by_exam": self.problems_data.get("exams", {}),
            "by_year": self.problems_data.get("years", {})
        }

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_problem_server(problems_dir: str) -> ProblemServer:
    """
    Factory function to create a ProblemServer.

    Args:
        problems_dir: Path to directory containing problem JSON files

    Returns:
        Initialized ProblemServer
    """
    return ProblemServer(problems_dir)


# Standalone execution
if __name__ == "__main__":
    import asyncio
    import sys

    # Determine problems directory path
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    problems_dir = backend_dir / "data" / "problems"

    if not problems_dir.exists():
        print(f"Error: Problems directory not found at {problems_dir}")
        sys.exit(1)

    # Count available problem files
    problem_files = list(problems_dir.glob("*.json"))
    if not problem_files:
        print(f"Error: No problem JSON files found in {problems_dir}")
        sys.exit(1)

    print(f"Starting JEE Problem MCP Server...")
    print(f"Using problems directory: {problems_dir}")
    print(f"Found {len(problem_files)} problem file(s)")
    print(f"Server ready for connections via stdio")

    server = create_problem_server(str(problems_dir))
    asyncio.run(server.run())
