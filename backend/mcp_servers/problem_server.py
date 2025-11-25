"""
JEE Problem MCP Server

MCP server that provides tools for accessing the physics problem bank.
Exposes 4 tools: get_problem, search_problems, get_random_problem, list_topics
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class ProblemServer:
    """MCP Server for JEE Physics problems."""

    def __init__(self, problems_index_path: str):
        """
        Initialize the problem server.

        Args:
            problems_index_path: Path to problems_index.json
        """
        self.problems_index_path = Path(problems_index_path)
        self.problems_data = self._load_problems()
        self.server = Server("jee-problem-server")
        self._register_handlers()

    def _load_problems(self) -> Dict[str, Any]:
        """Load the problems index."""
        if not self.problems_index_path.exists():
            raise FileNotFoundError(f"Problems index not found: {self.problems_index_path}")

        with open(self.problems_index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _register_handlers(self):
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_problem",
                    description="Get specific problem by ID or all problems for a topic",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_id": {
                                "type": "string",
                                "description": "Problem ID (e.g., 'kinematics_001')"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic to filter by (e.g., 'kinematics', 'dynamics')"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "Difficulty level: 'easy', 'medium', or 'hard'"
                            }
                        }
                    }
                ),
                Tool(
                    name="search_problems",
                    description="Search problems by keywords in question text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search keywords"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Optional: filter by topic"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "Optional: filter by difficulty"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max number of results (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_random_problem",
                    description="Get a random practice problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Optional: filter by topic"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "Optional: filter by difficulty"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_topics",
                    description="Get all available topics with problem counts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            if name == "get_problem":
                result = self._get_problem(
                    problem_id=arguments.get("problem_id"),
                    topic=arguments.get("topic"),
                    difficulty=arguments.get("difficulty")
                )
            elif name == "search_problems":
                result = self._search_problems(
                    query=arguments["query"],
                    topic=arguments.get("topic"),
                    difficulty=arguments.get("difficulty"),
                    limit=arguments.get("limit", 5)
                )
            elif name == "get_random_problem":
                result = self._get_random_problem(
                    topic=arguments.get("topic"),
                    difficulty=arguments.get("difficulty")
                )
            elif name == "list_topics":
                result = self._list_topics()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

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

    def _get_problem(
        self,
        problem_id: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get problem(s) by ID or filters.

        Returns problem details WITHOUT solution initially (only question and hints).
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

    def _search_problems(
        self,
        query: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Search problems by keywords."""
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

    def _get_random_problem(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a random problem."""
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

    def _list_topics(self) -> Dict[str, Any]:
        """List all available topics with counts."""
        return {
            "total_problems": self.problems_data.get("total_problems", 0),
            "topics": self.problems_data.get("topics", {}),
            "difficulties": self.problems_data.get("difficulties", {})
        }

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_problem_server(problems_index_path: str) -> ProblemServer:
    """
    Factory function to create a ProblemServer.

    Args:
        problems_index_path: Path to problems_index.json

    Returns:
        Initialized ProblemServer
    """
    return ProblemServer(problems_index_path)


# Standalone execution
if __name__ == "__main__":
    import asyncio
    import sys

    # Determine problems index path
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    index_path = backend_dir / "data" / "extracted" / "problems_index.json"

    if not index_path.exists():
        print(f"Error: Problems index not found at {index_path}")
        print("Please run: python scripts/index_problems.py")
        sys.exit(1)

    print(f"Starting JEE Problem MCP Server...")
    print(f"Using index: {index_path}")
    print(f"Server ready for connections via stdio")

    server = create_problem_server(str(index_path))
    asyncio.run(server.run())
