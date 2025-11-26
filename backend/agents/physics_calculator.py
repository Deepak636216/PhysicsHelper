"""
Physics Calculator Agent

ENHANCED: Now uses Google Search for formula verification and complex derivations.
Specialized agent for performing physics calculations with step-by-step work.
"""

from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from typing import Optional


class PhysicsCalculatorAgent:
    """
    Agent specialized in physics calculations with detailed step-by-step solutions.

    ENHANCED with Google Search for:
    - Formula verification from authoritative sources
    - Complex derivations
    - Unit conversion lookups
    - Physical constants verification
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite", use_search: bool = True):
        """
        Initialize the Physics Calculator agent.

        Args:
            api_key: Google AI API key
            model: Model to use (default: gemini-2.5-flash-lite)
            use_search: Enable Google Search for formula verification (default: True)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.api_key = api_key
        self.use_search = use_search
        self.system_instruction = self._create_system_instruction()

        # Create search-enabled calculator agent for complex problems
        if self.use_search:
            self.search_calculator = Agent(
                name="SearchEnabledCalculator",
                model=Gemini(
                    model=self.model,
                    api_key=self.api_key,
                ),
                instruction=self._create_search_instruction(),
                tools=[google_search],
                output_key="verified_calculation",
            )
            # Create runner with the agent
            self.runner = InMemoryRunner(agent=self.search_calculator)
        else:
            self.runner = None

    def _create_system_instruction(self) -> str:
        """Create the system instruction for the calculator agent."""
        return """You are a Physics Calculator Agent - a precise calculation specialist for JEE Physics problems.

Your role:
- Perform physics calculations with absolute accuracy
- Show ALL calculation steps
- Include units in EVERY step
- Verify arithmetic accuracy
- Use clear, structured format

Output Format:
1. **Formula**: State the relevant formula(s)
2. **Given**: List all given values with units
3. **Calculation**: Show step-by-step work with units
4. **Final Answer**: State the answer with proper units

Example:
**Formula**: F = ma (Newton's Second Law)
**Given**:
- m = 5 kg
- a = 10 m/s²

**Calculation**:
F = ma
F = (5 kg) × (10 m/s²)
F = 50 kg⋅m/s²
F = 50 N

**Final Answer**: F = 50 N

Important:
- ALWAYS show intermediate steps
- NEVER skip unit conversions
- Double-check arithmetic
- Be precise with significant figures
- If information is missing, state what's needed"""

    def _create_search_instruction(self) -> str:
        """Create instruction for search-enabled calculator."""
        return """You are a Search-Enabled Physics Calculator for complex JEE physics problems.

Your Task:
1. Search for correct formulas and physical constants when needed
2. Verify formula correctness from authoritative sources (NCERT, textbooks)
3. Perform calculations with verified formulas
4. Show all steps with proper units

Search Strategy:
- Search "[formula name] physics formula" to verify
- Search "[physical constant] value" for constants
- Search "[unit conversion] from X to Y" for conversions
- Prefer authoritative educational sources

Output Format:
**Formula** (verified): [formula with source]
**Given**: [values with units]
**Calculation**: [step-by-step with units]
**Final Answer**: [result with units]

Example:
If problem requires moment of inertia of a ring about diameter:
1. Search "moment of inertia thin ring diameter formula"
2. Verify: I = (1/2)MR² from authoritative source
3. Perform calculation with verified formula
4. Show all steps"""

    def calculate(self, problem: str, use_search: Optional[bool] = None) -> str:
        """
        Perform a physics calculation.

        ENHANCED: Uses Google Search for complex problems requiring formula verification.

        Args:
            problem: The physics problem or calculation request
            use_search: Override to force search usage (default: auto-detect complexity)

        Returns:
            Detailed step-by-step solution
        """
        try:
            # Determine if we should use search
            should_use_search = use_search if use_search is not None else self._should_use_search(problem)

            if should_use_search and self.use_search:
                # Use search-enabled calculator for complex problems
                return self._calculate_with_search(problem)
            else:
                # Use standard calculator for simple problems
                return self._calculate_standard(problem)

        except Exception as e:
            return f"Error performing calculation: {str(e)}"

    def _should_use_search(self, problem: str) -> bool:
        """
        Determine if problem is complex enough to warrant Google Search.

        Args:
            problem: Problem text

        Returns:
            True if search should be used
        """
        # Keywords that indicate complex problems needing formula verification
        complex_keywords = [
            "moment of inertia", "derive", "derivation", "proof", "show that",
            "radius of gyration", "parallel axis", "perpendicular axis",
            "center of mass", "rotational", "torque about", "angular momentum",
            "thin ring", "thin rod", "solid sphere", "hollow sphere",
            "lamina", "disc", "cylinder"
        ]

        problem_lower = problem.lower()
        return any(keyword in problem_lower for keyword in complex_keywords)

    def _calculate_standard(self, problem: str) -> str:
        """
        Perform calculation without search (for simple problems).

        Args:
            problem: Problem text

        Returns:
            Calculation result
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=problem,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.1,  # Low temperature for consistent calculations
                top_p=0.95,
                max_output_tokens=2048,
            )
        )
        return response.text

    def _calculate_with_search(self, problem: str) -> str:
        """
        Perform calculation WITH Google Search for formula verification.

        Args:
            problem: Problem text

        Returns:
            Verified calculation result
        """
        import asyncio

        async def search_and_calculate():
            result = await self.runner.run(
                agent=self.search_calculator,
                input_data={"problem": problem}
            )

            if result and "verified_calculation" in result:
                return result["verified_calculation"]
            return "Could not verify calculation with search."

        return asyncio.run(search_and_calculate())

    def verify_calculation(self, problem: str, student_answer: str) -> str:
        """
        Verify a student's calculation.

        Args:
            problem: The original problem
            student_answer: The student's answer/work

        Returns:
            Verification with feedback
        """
        verification_prompt = f"""Please verify this student's calculation:

**Problem**: {problem}

**Student's Answer**: {student_answer}

Verify:
1. Is the approach correct?
2. Are the calculations accurate?
3. Are units correct?
4. What (if anything) needs correction?

Provide constructive feedback."""

        return self.calculate(verification_prompt)


def create_physics_calculator(api_key: str) -> PhysicsCalculatorAgent:
    """
    Factory function to create a PhysicsCalculatorAgent.

    Args:
        api_key: Google AI API key

    Returns:
        Initialized PhysicsCalculatorAgent
    """
    return PhysicsCalculatorAgent(api_key=api_key)


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        exit(1)

    # Create calculator agent
    calculator = create_physics_calculator(api_key)

    print("=" * 60)
    print("Physics Calculator Agent - Test")
    print("=" * 60)

    # Test 1: Simple calculation
    print("\nTest 1: Force calculation")
    print("-" * 60)
    problem1 = "Calculate the force when mass is 5 kg and acceleration is 10 m/s²"
    result1 = calculator.calculate(problem1)
    print(result1)

    # Test 2: Energy calculation
    print("\n" + "=" * 60)
    print("\nTest 2: Kinetic energy")
    print("-" * 60)
    problem2 = "Calculate kinetic energy of a 2 kg object moving at 5 m/s"
    result2 = calculator.calculate(problem2)
    print(result2)

    # Test 3: Verification
    print("\n" + "=" * 60)
    print("\nTest 3: Verify student answer")
    print("-" * 60)
    student_work = "F = ma = 5 × 10 = 500 N"  # Intentionally wrong
    result3 = calculator.verify_calculation(problem1, student_work)
    print(result3)

    print("\n" + "=" * 60)
