"""
Solution Validator Agent

Validates student solutions and provides constructive feedback.
Delegates calculation verification to PhysicsCalculator sub-agent.
"""

from google import genai
from google.genai import types
from typing import Optional, Dict, Any
import json


class SolutionValidatorAgent:
    """
    Agent specialized in validating student solutions with constructive feedback.

    This agent:
    - Checks conceptual approach first (method correctness)
    - Verifies calculations using PhysicsCalculator sub-agent
    - Identifies specific errors with clear explanations
    - Provides constructive, encouraging feedback
    - Acknowledges correct parts before addressing errors
    """

    def __init__(
        self,
        api_key: str,
        physics_calculator=None,
        model: str = "gemini-2.5-flash-lite"
    ):
        """
        Initialize the Solution Validator agent.

        Args:
            api_key: Google AI API key
            physics_calculator: PhysicsCalculatorAgent instance for verification
            model: Model to use (default: gemini-2.5-flash-lite)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.calculator = physics_calculator
        self.system_instruction = self._create_system_instruction()

    def _create_system_instruction(self) -> str:
        """Create the system instruction for the solution validator agent."""
        return """You are a SolutionValidator Agent - an expert evaluator of JEE Physics solutions.

Your Validation Philosophy:
- Check conceptual approach BEFORE arithmetic
- Be thorough but constructive
- Acknowledge correct work enthusiastically
- Identify specific errors, not just "wrong"
- Explain WHY something is incorrect
- Guide toward correction without solving for student

Your Validation Process:
1. **Conceptual Analysis** (Most Important)
   - Is the chosen method/formula appropriate?
   - Does the approach show understanding of physics principles?
   - Are the problem-solving steps logical?

2. **Calculation Verification**
   - Are arithmetic operations correct?
   - Are units handled properly throughout?
   - Are conversions done correctly?
   - Is significant figure handling appropriate?

3. **Final Answer Check**
   - Is the final answer reasonable (order of magnitude)?
   - Are units correct and clearly stated?
   - Is the answer format appropriate?

Feedback Structure:
1. **Acknowledge Strengths**: Start with what's correct
2. **Identify Issues**: Specific errors with clear explanations
3. **Explain Corrections**: Why the error occurred and how to fix
4. **Encourage**: End with positive reinforcement

Response Format:
```
✅ **Strengths**:
- [List correct aspects of solution]

⚠️ **Issues Found**:
1. [Specific error with explanation]
2. [Another error if applicable]

💡 **Corrections**:
- [How to fix each issue]

🎯 **Corrected Solution**:
[Show correct approach if needed]

📝 **Feedback**:
[Encouraging message with learning points]
```

Key Principles:
- ALWAYS start with positives
- Be specific: "Your multiplication is incorrect: 5×10=50, not 500"
- Be encouraging: "Great approach! Just watch the arithmetic"
- Focus on learning: "This shows you understand the concept, now practice the calculations"
- Never be discouraging or harsh
- Provide the correct answer for learning

Example Validation:
Student Solution: "F = ma = 5 × 10 = 500 N"

Your Response:
✅ **Strengths**:
- Correctly identified Newton's Second Law (F = ma)
- Properly substituted the given values

⚠️ **Issues Found**:
1. Arithmetic Error: 5 × 10 = 50, not 500

💡 **Corrections**:
- Double-check your multiplication: 5 × 10 = 50

🎯 **Corrected Solution**:
F = ma = (5 kg) × (10 m/s²) = 50 N

📝 **Feedback**:
Your method is spot-on! You clearly understand Newton's Second Law.
Just be careful with arithmetic - a simple calculation error changed
your answer by a factor of 10. Keep up the good work!"""

    def validate(
        self,
        problem: str,
        student_solution: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Validate a student's solution.

        Args:
            problem: The original physics problem
            student_solution: Student's complete solution/answer
            context: Optional context (expected answer, topic, etc.)

        Returns:
            Detailed validation feedback
        """
        try:
            # Build validation prompt
            validation_prompt = self._build_validation_prompt(
                problem, student_solution, context
            )

            # Generate validation
            response = self.client.models.generate_content(
                model=self.model,
                contents=validation_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3,  # Low-medium temp for consistent validation
                    top_p=0.95,
                    max_output_tokens=1536,
                )
            )

            return response.text

        except Exception as e:
            return f"Error during validation: {str(e)}"

    def _build_validation_prompt(
        self,
        problem: str,
        student_solution: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the validation prompt."""
        prompt_parts = [
            "Please validate this student's solution:\n",
            f"**Problem**: {problem}\n",
            f"**Student's Solution**: {student_solution}\n"
        ]

        if context:
            if "expected_answer" in context:
                prompt_parts.append(f"**Expected Answer**: {context['expected_answer']}\n")
            if "topic" in context:
                prompt_parts.append(f"**Topic**: {context['topic']}\n")

        prompt_parts.append("\nProvide comprehensive validation following the structured format.")

        return "\n".join(prompt_parts)

    def validate_with_calculator(
        self,
        problem: str,
        student_solution: str
    ) -> str:
        """
        Validate solution using PhysicsCalculator for verification.

        Args:
            problem: The original problem
            student_solution: Student's solution

        Returns:
            Validation feedback with calculator verification
        """
        if self.calculator is None:
            return self.validate(problem, student_solution)

        try:
            # Get correct solution from calculator
            correct_solution = self.calculator.calculate(problem)

            # Add calculator result to context
            validation_prompt = f"""Please validate this student's solution:

**Problem**: {problem}

**Student's Solution**: {student_solution}

**Correct Solution** (for reference):
{correct_solution}

Provide comprehensive validation comparing the student's work with the correct solution."""

            # Generate validation
            response = self.client.models.generate_content(
                model=self.model,
                contents=validation_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3,
                    top_p=0.95,
                    max_output_tokens=1536,
                )
            )

            return response.text

        except Exception as e:
            return f"Error during validation with calculator: {str(e)}"

    def quick_check(
        self,
        student_answer: str,
        correct_answer: str,
        problem: Optional[str] = None
    ) -> str:
        """
        Quick check if student's final answer matches correct answer.

        Args:
            student_answer: Student's final answer
            correct_answer: The correct answer
            problem: Optional problem description for context

        Returns:
            Quick feedback (correct/incorrect with brief explanation)
        """
        try:
            check_prompt = f"""Quick answer check:

Student's Answer: {student_answer}
Correct Answer: {correct_answer}
"""
            if problem:
                check_prompt += f"Problem: {problem}\n"

            check_prompt += "\nIs the student's answer correct? Provide brief feedback (2-3 sentences)."

            response = self.client.models.generate_content(
                model=self.model,
                contents=check_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3,
                    max_output_tokens=256,
                )
            )

            return response.text

        except Exception as e:
            return f"Error during quick check: {str(e)}"

    def validate_approach(
        self,
        problem: str,
        student_approach: str
    ) -> str:
        """
        Validate only the conceptual approach, not calculations.

        Args:
            problem: The problem statement
            student_approach: Student's described approach/method

        Returns:
            Feedback on approach validity
        """
        try:
            approach_prompt = f"""Validate the student's problem-solving approach:

**Problem**: {problem}

**Student's Approach**: {student_approach}

Evaluate ONLY the conceptual approach and method. Don't check arithmetic.
Is the method correct? Are they using the right physics principles?"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=approach_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3,
                    max_output_tokens=512,
                )
            )

            return response.text

        except Exception as e:
            return f"Error validating approach: {str(e)}"

    def identify_common_mistakes(
        self,
        problem: str,
        student_solution: str
    ) -> Dict[str, Any]:
        """
        Identify common physics mistakes in solution.

        Args:
            problem: The problem
            student_solution: Student's solution

        Returns:
            Dictionary of identified mistake categories
        """
        mistake_categories = {
            "conceptual_errors": [],
            "arithmetic_errors": [],
            "unit_errors": [],
            "sign_errors": [],
            "formula_errors": []
        }

        try:
            # This is a simplified version - could be enhanced with pattern matching
            validation = self.validate(problem, student_solution)

            # Parse validation for common error patterns
            if "formula" in validation.lower() or "equation" in validation.lower():
                mistake_categories["formula_errors"].append("Potential formula issue detected")

            if "unit" in validation.lower():
                mistake_categories["unit_errors"].append("Unit handling needs attention")

            if "arithmetic" in validation.lower() or "calculation" in validation.lower():
                mistake_categories["arithmetic_errors"].append("Arithmetic error detected")

            return mistake_categories

        except Exception as e:
            return {"error": str(e)}


def create_solution_validator(api_key: str, physics_calculator=None) -> SolutionValidatorAgent:
    """
    Factory function to create a SolutionValidatorAgent.

    Args:
        api_key: Google AI API key
        physics_calculator: Optional PhysicsCalculatorAgent instance

    Returns:
        Initialized SolutionValidatorAgent
    """
    return SolutionValidatorAgent(api_key=api_key, physics_calculator=physics_calculator)


# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from physics_calculator import create_physics_calculator

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        exit(1)

    print("=" * 70)
    print("Solution Validator Agent - Test Suite")
    print("=" * 70)

    # Create calculator sub-agent
    calculator = create_physics_calculator(api_key)

    # Create solution validator with calculator
    validator = create_solution_validator(api_key, physics_calculator=calculator)

    # Test 1: Validate incorrect solution (arithmetic error)
    print("\n" + "=" * 70)
    print("Test 1: Validate Solution with Arithmetic Error")
    print("=" * 70)
    problem1 = "Calculate the force when mass is 5 kg and acceleration is 10 m/s²"
    wrong_solution1 = "F = ma = 5 × 10 = 500 N"
    print(f"\nProblem: {problem1}")
    print(f"Student's Solution: {wrong_solution1}")
    validation1 = validator.validate(problem1, wrong_solution1)
    print(f"\nValidation:\n{validation1}")

    # Test 2: Validate correct solution
    print("\n" + "=" * 70)
    print("Test 2: Validate Correct Solution")
    print("=" * 70)
    problem2 = "Calculate the force when mass is 5 kg and acceleration is 10 m/s²"
    correct_solution2 = "F = ma = (5 kg) × (10 m/s²) = 50 N"
    print(f"\nProblem: {problem2}")
    print(f"Student's Solution: {correct_solution2}")
    validation2 = validator.validate(problem2, correct_solution2)
    print(f"\nValidation:\n{validation2}")

    # Test 3: Validate with calculator verification
    print("\n" + "=" * 70)
    print("Test 3: Validate with PhysicsCalculator Verification")
    print("=" * 70)
    problem3 = "A ball of mass 2 kg is thrown with initial velocity 10 m/s. What is its kinetic energy?"
    student_solution3 = "KE = (1/2)mv² = (1/2) × 2 × 10 = 10 J"  # Missing squaring of velocity
    print(f"\nProblem: {problem3}")
    print(f"Student's Solution: {student_solution3}")
    validation3 = validator.validate_with_calculator(problem3, student_solution3)
    print(f"\nValidation:\n{validation3}")

    # Test 4: Quick answer check
    print("\n" + "=" * 70)
    print("Test 4: Quick Answer Check")
    print("=" * 70)
    student_ans4 = "50 N"
    correct_ans4 = "50 N"
    print(f"\nStudent Answer: {student_ans4}")
    print(f"Correct Answer: {correct_ans4}")
    quick_check4 = validator.quick_check(student_ans4, correct_ans4)
    print(f"\nQuick Check:\n{quick_check4}")

    # Test 5: Quick check - wrong answer
    print("\n" + "=" * 70)
    print("Test 5: Quick Check - Incorrect Answer")
    print("=" * 70)
    student_ans5 = "500 N"
    correct_ans5 = "50 N"
    print(f"\nStudent Answer: {student_ans5}")
    print(f"Correct Answer: {correct_ans5}")
    quick_check5 = validator.quick_check(student_ans5, correct_ans5)
    print(f"\nQuick Check:\n{quick_check5}")

    # Test 6: Validate approach only
    print("\n" + "=" * 70)
    print("Test 6: Validate Conceptual Approach")
    print("=" * 70)
    problem6 = "Find the time it takes for a ball to hit the ground when dropped from 20m height"
    approach6 = "I'll use the equation h = (1/2)gt² and solve for t"
    print(f"\nProblem: {problem6}")
    print(f"Student's Approach: {approach6}")
    approach_validation6 = validator.validate_approach(problem6, approach6)
    print(f"\nApproach Validation:\n{approach_validation6}")

    # Test 7: Wrong approach
    print("\n" + "=" * 70)
    print("Test 7: Validate Incorrect Approach")
    print("=" * 70)
    problem7 = "Calculate force when mass is 5 kg and acceleration is 10 m/s²"
    wrong_approach7 = "I'll use the kinetic energy formula KE = (1/2)mv²"
    print(f"\nProblem: {problem7}")
    print(f"Student's Approach: {wrong_approach7}")
    approach_validation7 = validator.validate_approach(problem7, wrong_approach7)
    print(f"\nApproach Validation:\n{approach_validation7}")

    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nSolution Validator Features Demonstrated:")
    print("  ✓ Full solution validation (conceptual + arithmetic)")
    print("  ✓ PhysicsCalculator integration for verification")
    print("  ✓ Quick answer checking")
    print("  ✓ Approach-only validation")
    print("  ✓ Constructive feedback with structured format")
    print("  ✓ Error identification and correction guidance")
    print("  ✓ Positive reinforcement for correct work")
    print("=" * 70)
