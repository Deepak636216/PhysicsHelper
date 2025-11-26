"""
Solution Fetcher Service

Fetches verified solutions for physics problems using:
1. MCP Knowledge Base (fast, curated)
2. Google Search via ADK (broad coverage)
3. Model reasoning (fallback)

Solutions are fetched BEFORE teaching to ensure accuracy.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SolutionFetcher:
    """
    Fetches and verifies physics problem solutions from multiple sources.

    Strategy:
    1. Try MCP knowledge base first (if available)
    2. Use Google Search via ADK for comprehensive coverage
    3. Fall back to model reasoning if needed
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize Solution Fetcher with Google ADK.

        Args:
            api_key: Google AI API key
            model: Model to use for solution extraction
        """
        self.api_key = api_key
        self.model = model

        # Retry configuration
        self.retry_config = types.GenerateContentConfig(
            temperature=0.1,  # Low temperature for factual accuracy
            top_p=0.95,
            max_output_tokens=2048,
        )

        # Create Physics Solution Researcher agent
        self.solution_agent = Agent(
            name="PhysicsSolutionResearcher",
            model=Gemini(
                model=self.model,
                api_key=self.api_key,
            ),
            instruction=self._create_researcher_instruction(),
            tools=[google_search],
            output_key="verified_solution",
        )

        # Create runner with the agent
        self.runner = InMemoryRunner(agent=self.solution_agent)

    def _create_researcher_instruction(self) -> str:
        """Create instruction for the solution researcher agent."""
        return """You are a Physics Solution Researcher specialized in JEE-level physics problems.

Your Task:
- Search for accurate, step-by-step solutions to physics problems
- Verify solution correctness using multiple sources
- Extract key concepts, formulas, and derivations
- Format solutions in clear, educational manner

Search Strategy:
1. Search for "[problem text] JEE physics solution"
2. Look for authoritative sources (NCERT, coaching institutes, educational sites)
3. Verify formulas and calculations
4. Cross-reference with multiple sources

Output Format:
{
    "problem": "Original problem statement",
    "solution_steps": [
        "Step 1: Identify given quantities...",
        "Step 2: Apply relevant formula...",
        "Step 3: Calculate...",
        ...
    ],
    "final_answer": "Final result with units",
    "key_concepts": ["concept1", "concept2", ...],
    "formulas_used": ["formula1", "formula2", ...],
    "confidence": "high/medium/low",
    "sources": ["source1", "source2", ...]
}

IMPORTANT:
- Express final answers in terms of ORIGINAL variables given in problem
- Show all substitution steps clearly
- Verify calculations are correct
- If multiple solutions found, choose the most authoritative one
- Flag if solution seems uncertain or conflicting
"""

    async def fetch_solution(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Fetch verified solution for a physics problem.

        Args:
            problem: Physics problem statement
            context: Optional context (topic, difficulty, etc.)

        Returns:
            Tuple of (solution_dict, source)
            - solution_dict: Structured solution information
            - source: 'mcp', 'search', 'model', or None
        """
        try:
            logger.info(f"Fetching solution for problem: {problem[:100]}...")

            # Step 1: Try MCP Knowledge Base (TODO: implement when MCP available)
            # mcp_solution = await self._try_mcp(problem, context)
            # if mcp_solution:
            #     logger.info("Solution found in MCP knowledge base")
            #     return mcp_solution, "mcp"

            # Step 2: Try Google Search via ADK
            search_solution = await self._search_solution(problem, context)
            if search_solution and search_solution.get('confidence') in ['high', 'medium']:
                logger.info("Solution found via Google Search")
                return search_solution, "search"

            # Step 3: Fallback to model reasoning
            logger.info("Using model reasoning as fallback")
            model_solution = await self._model_solution(problem, context)
            return model_solution, "model"

        except Exception as e:
            logger.error(f"Error fetching solution: {e}")
            return None, None

    async def _search_solution(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for solution using Google Search via ADK.

        Args:
            problem: Physics problem statement
            context: Optional context

        Returns:
            Structured solution dictionary or None
        """
        try:
            # Build search query
            search_query = self._build_search_query(problem, context)

            # Run solution researcher agent
            result = await self.runner.run(
                agent=self.solution_agent,
                input_data={"problem": problem, "search_query": search_query}
            )

            # Extract solution from agent output
            if result and "verified_solution" in result:
                solution = result["verified_solution"]
                logger.info(f"Search found solution with confidence: {solution.get('confidence', 'unknown')}")
                return solution

            return None

        except Exception as e:
            logger.error(f"Error in Google Search: {e}")
            return None

    def _build_search_query(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build optimized search query for physics problem.

        Args:
            problem: Problem statement
            context: Optional context

        Returns:
            Optimized search query string
        """
        # Extract key terms from problem
        query_parts = [problem]

        # Add context if available
        if context:
            if "topic" in context:
                query_parts.append(context["topic"])
            if "difficulty" in context:
                query_parts.append(context["difficulty"])

        # Add JEE-specific keywords
        query_parts.extend(["JEE physics", "solution", "step by step"])

        return " ".join(query_parts)

    async def _model_solution(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate solution using model reasoning (fallback).

        Args:
            problem: Problem statement
            context: Optional context

        Returns:
            Structured solution dictionary
        """
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)

            prompt = f"""Solve this JEE physics problem step by step:

Problem: {problem}

Provide a complete solution with:
1. Identify given quantities
2. Relevant formulas
3. Step-by-step derivation
4. Final answer with units
5. Key concepts involved

Format your response as a structured solution."""

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.retry_config
            )

            # Parse response into structured format
            solution = {
                "problem": problem,
                "solution_text": response.text,
                "confidence": "medium",
                "source": "model_reasoning"
            }

            return solution

        except Exception as e:
            logger.error(f"Error in model solution: {e}")
            return None

    def get_solution_summary(self, solution: Dict[str, Any]) -> str:
        """
        Get human-readable summary of solution for logging.

        Args:
            solution: Solution dictionary

        Returns:
            Summary string
        """
        if not solution:
            return "No solution available"

        summary_parts = []

        if "final_answer" in solution:
            summary_parts.append(f"Answer: {solution['final_answer']}")

        if "confidence" in solution:
            summary_parts.append(f"Confidence: {solution['confidence']}")

        if "key_concepts" in solution:
            concepts = ", ".join(solution['key_concepts'][:3])
            summary_parts.append(f"Concepts: {concepts}")

        return " | ".join(summary_parts)


def create_solution_fetcher(api_key: str) -> SolutionFetcher:
    """
    Factory function to create SolutionFetcher.

    Args:
        api_key: Google AI API key

    Returns:
        Initialized SolutionFetcher instance
    """
    return SolutionFetcher(api_key=api_key)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        exit(1)

    async def test_solution_fetcher():
        print("=" * 70)
        print("Solution Fetcher - Test Suite")
        print("=" * 70)

        fetcher = create_solution_fetcher(api_key)

        # Test problem
        problem = """A rod of linear mass density 'λ' and length 'L' is bent to form
a ring of radius 'R'. Find the moment of inertia of the ring about any of its diameter."""

        print(f"\nProblem: {problem}")
        print("\nFetching solution...")

        solution, source = await fetcher.fetch_solution(problem)

        print(f"\nSource: {source}")
        print(f"Summary: {fetcher.get_solution_summary(solution)}")

        if solution:
            print("\nFull Solution:")
            if "solution_steps" in solution:
                for i, step in enumerate(solution['solution_steps'], 1):
                    print(f"  {i}. {step}")
            elif "solution_text" in solution:
                print(solution['solution_text'])

        print("\n" + "=" * 70)

    asyncio.run(test_solution_fetcher())
