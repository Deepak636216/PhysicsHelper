"""
Physics Calculator Agent

Specialized agent for performing physics calculations with step-by-step work.
Uses gemini-2.0-flash-exp model for precise calculations.
"""

from google import genai
from google.genai import types


class PhysicsCalculatorAgent:
    """
    Agent specialized in physics calculations with detailed step-by-step solutions.

    This agent:
    - Performs all types of physics calculations
    - Shows work step-by-step
    - Includes units in every step
    - Verifies arithmetic accuracy
    - Uses format: Formula → Given → Calculation → Final Answer
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Physics Calculator agent.

        Args:
            api_key: Google AI API key
            model: Model to use (default: gemini-2.0-flash-exp)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.system_instruction = self._create_system_instruction()

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

    def calculate(self, problem: str) -> str:
        """
        Perform a physics calculation.

        Args:
            problem: The physics problem or calculation request

        Returns:
            Detailed step-by-step solution
        """
        try:
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

        except Exception as e:
            return f"Error performing calculation: {str(e)}"

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
