"""
Socratic Tutor Agent

Expert JEE Physics tutor that teaches using the Socratic method.
Uses MCP tools to access problem bank and delegates calculations to PhysicsCalculator.
"""

from google import genai
from google.genai import types
from typing import Optional
import json


class SocraticTutorAgent:
    """
    Agent specialized in Socratic teaching for JEE Physics.

    This agent:
    - Guides students through questions (never gives direct answers)
    - Breaks complex problems into smaller steps
    - Uses MCP tools to access problem bank
    - Delegates calculations to PhysicsCalculator sub-agent
    - Encourages critical thinking and discovery
    """

    def __init__(
        self,
        api_key: str,
        physics_calculator=None,
        model: str = "gemini-2.5-flash-lite"
    ):
        """
        Initialize the Socratic Tutor agent.

        Args:
            api_key: Google AI API key
            physics_calculator: PhysicsCalculatorAgent instance for delegation
            model: Model to use (default: gemini-2.0-flash-exp)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.calculator = physics_calculator
        self.system_instruction = self._create_system_instruction()
        self.conversation_history = []

    def _create_system_instruction(self) -> str:
        """Create the system instruction for the Socratic tutor agent."""
        return """You are a SocraticTutor Agent - an expert JEE Physics tutor who teaches using the Socratic method.

Your Teaching Philosophy:
- NEVER give direct answers or complete solutions
- Guide students through discovery with thoughtful questions
- Break complex problems into manageable steps
- Encourage critical thinking and conceptual understanding
- Be patient, supportive, and encouraging

Your Capabilities:
1. **Conceptual Guidance**: Ask probing questions to build understanding
2. **Problem Access**: Can recommend problems from the problem bank
3. **Calculation Support**: Can verify calculations (but prefer guiding student to solve)
4. **Hint Provision**: Give strategic hints that lead to discovery

When Student Asks For:
- "Practice problem" → Suggest topics/difficulties, guide problem selection
- "Help solving" → Ask what they understand, guide with questions
- "Is this correct?" → Ask them to explain their reasoning first
- "Calculate this" → Guide them through the steps, or delegate if verification needed
- "Hint" → Give minimal hint that prompts thinking

Teaching Approach:
1. Start by understanding what the student knows
2. Identify gaps in understanding
3. Ask questions that lead to those insights
4. Build on correct thinking
5. Gently correct misconceptions with questions

Response Style:
- Ask 1-2 questions per response
- Acknowledge correct thinking enthusiastically
- Never be discouraging
- Use simple language
- Include relevant physics concepts
- Encourage experimentation

Example Interaction:
Student: "How do I solve this kinematics problem?"
You: "Great question! Let's think about this together. What information does the problem give you? And what are you trying to find?"

Student: "I have velocity and time, need distance"
You: "Perfect! You've identified the known and unknown. Now, what relationship connects distance, velocity, and time? Have you seen any formulas that relate these?"

Remember: You're a guide, not a solution provider. The goal is student discovery and understanding!"""

    def teach(self, message: str, context: Optional[dict] = None) -> str:
        """
        Respond to student message using Socratic method.

        Args:
            message: Student's message/question
            context: Optional context (current problem, topic, etc.)

        Returns:
            Socratic response guiding the student
        """
        try:
            # Build conversation context
            conversation_context = self._build_context(message, context)

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "message": message,
                "context": context
            })

            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=conversation_context,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,  # Higher temperature for varied teaching responses
                    top_p=0.95,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text

            # Add to conversation history
            self.conversation_history.append({
                "role": "agent",
                "message": response_text
            })

            return response_text

        except Exception as e:
            return f"I apologize, I encountered an error: {str(e)}. Let's try again!"

    def _build_context(self, message: str, context: Optional[dict] = None) -> str:
        """Build conversation context for the model."""
        context_parts = []

        # Add current message
        context_parts.append(f"Student: {message}")

        # Add context if provided
        if context:
            if "current_problem" in context:
                context_parts.append(f"\nCurrent Problem: {context['current_problem']}")
            if "topic" in context:
                context_parts.append(f"\nTopic: {context['topic']}")
            if "student_attempt" in context:
                context_parts.append(f"\nStudent's Attempt: {context['student_attempt']}")

        # Add recent conversation history (last 3 exchanges)
        if len(self.conversation_history) > 0:
            recent_history = self.conversation_history[-6:]  # Last 3 exchanges (user + agent)
            history_text = "\n\nRecent Conversation:\n"
            for entry in recent_history:
                role = "Student" if entry["role"] == "user" else "You"
                history_text += f"{role}: {entry['message']}\n"
            context_parts.append(history_text)

        return "\n".join(context_parts)

    def delegate_calculation(self, problem: str) -> str:
        """
        Delegate a calculation to PhysicsCalculator sub-agent.

        Args:
            problem: Physics calculation problem

        Returns:
            Calculation result from PhysicsCalculator
        """
        if self.calculator is None:
            return "I don't have access to a calculator right now. Can you try solving it step by step?"

        try:
            result = self.calculator.calculate(problem)
            return result
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    def verify_student_work(self, problem: str, student_answer: str) -> str:
        """
        Use PhysicsCalculator to verify student's work.

        Args:
            problem: Original problem
            student_answer: Student's answer/work

        Returns:
            Verification feedback wrapped in Socratic style
        """
        if self.calculator is None:
            return "Let me review your work. Can you explain your reasoning behind each step?"

        try:
            # Get verification from calculator
            verification = self.calculator.verify_calculation(problem, student_answer)

            # Wrap in Socratic style
            socratic_response = f"""Let me help you check your work.

{verification}

Now, based on this feedback, what do you think about your approach? Where could you improve?"""

            return socratic_response
        except Exception as e:
            return f"I had trouble verifying that. Can you walk me through your steps?"

    def suggest_problem(self, topic: Optional[str] = None, difficulty: Optional[str] = None) -> str:
        """
        Suggest a practice problem (in real implementation, would use MCP tool).

        Args:
            topic: Physics topic (e.g., 'kinematics', 'dynamics')
            difficulty: Problem difficulty ('easy', 'medium', 'hard')

        Returns:
            Socratic response suggesting practice
        """
        response = "Great! Practice is key to mastery. "

        if topic:
            response += f"You're interested in {topic}. "
        else:
            response += "What topic would you like to practice? (kinematics, dynamics, energy, etc.) "

        if difficulty:
            response += f"I can find you a {difficulty} level problem. "
        else:
            response += "What difficulty level do you feel comfortable with: easy, medium, or hard? "

        response += "\n\nBefore we start, what concepts in this topic are you most confident with? And which ones do you find challenging?"

        return response

    def provide_hint(self, problem: str, hint_level: int = 1) -> str:
        """
        Provide graduated hints using Socratic method.

        Args:
            problem: The problem student is working on
            hint_level: Level of hint (1=minimal, 2=moderate, 3=substantial)

        Returns:
            Socratic hint response
        """
        hints = {
            1: "Let's start with the basics. What physical quantities are mentioned in the problem? What are you trying to find?",
            2: "Good thinking! Now, what physics principles or laws might apply here? Have you learned any formulas that connect these quantities?",
            3: "You're on the right track! Let me ask: if you write down the formula and identify all the known values, what would you need to calculate next?"
        }

        hint = hints.get(hint_level, hints[1])
        return f"Here's something to think about:\n\n{hint}\n\nTake your time and try working through it. What's your next step?"

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def create_socratic_tutor(api_key: str, physics_calculator=None) -> SocraticTutorAgent:
    """
    Factory function to create a SocraticTutorAgent.

    Args:
        api_key: Google AI API key
        physics_calculator: Optional PhysicsCalculatorAgent instance

    Returns:
        Initialized SocraticTutorAgent
    """
    return SocraticTutorAgent(api_key=api_key, physics_calculator=physics_calculator)


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
    print("Socratic Tutor Agent - Test Suite")
    print("=" * 70)

    # Create calculator sub-agent
    calculator = create_physics_calculator(api_key)

    # Create Socratic tutor with calculator
    tutor = create_socratic_tutor(api_key, physics_calculator=calculator)

    # Test 1: Request for practice problem
    print("\n" + "=" * 70)
    print("Test 1: Student Requests Practice Problem")
    print("=" * 70)
    message1 = "I want to practice kinematics problems"
    print(f"\nStudent: {message1}")
    response1 = tutor.teach(message1, context={"topic": "kinematics"})
    print(f"\nTutor: {response1}")

    # Test 2: Student asks for help with calculation
    print("\n" + "=" * 70)
    print("Test 2: Student Needs Help with Calculation")
    print("=" * 70)
    message2 = "I need to calculate force when mass is 5 kg and acceleration is 10 m/s²"
    print(f"\nStudent: {message2}")
    response2 = tutor.teach(message2)
    print(f"\nTutor: {response2}")

    # Test 3: Delegate calculation to sub-agent
    print("\n" + "=" * 70)
    print("Test 3: Delegate Calculation to PhysicsCalculator")
    print("=" * 70)
    calculation_problem = "Calculate the force when mass is 5 kg and acceleration is 10 m/s²"
    print(f"\nDelegating: {calculation_problem}")
    calc_result = tutor.delegate_calculation(calculation_problem)
    print(f"\nPhysicsCalculator Result:\n{calc_result}")

    # Test 4: Student asks for a hint
    print("\n" + "=" * 70)
    print("Test 4: Student Requests Hint")
    print("=" * 70)
    message4 = "Can you give me a hint for solving projectile motion problems?"
    print(f"\nStudent: {message4}")
    hint = tutor.provide_hint("projectile motion problem", hint_level=1)
    print(f"\nTutor: {hint}")

    # Test 5: Verify student work
    print("\n" + "=" * 70)
    print("Test 5: Verify Student's Work")
    print("=" * 70)
    problem = "Calculate force when m=5kg, a=10m/s²"
    student_work = "F = ma = 5 × 10 = 500 N"  # Intentionally wrong
    print(f"\nProblem: {problem}")
    print(f"Student's Answer: {student_work}")
    verification = tutor.verify_student_work(problem, student_work)
    print(f"\nTutor Feedback:\n{verification}")

    # Test 6: Suggest problem
    print("\n" + "=" * 70)
    print("Test 6: Suggest Practice Problem")
    print("=" * 70)
    suggestion = tutor.suggest_problem(topic="dynamics", difficulty="medium")
    print(f"\nTutor: {suggestion}")

    # Test 7: Multi-turn conversation
    print("\n" + "=" * 70)
    print("Test 7: Multi-turn Conversation")
    print("=" * 70)
    tutor.clear_history()  # Start fresh

    turn1 = "I'm confused about Newton's second law"
    print(f"\nStudent: {turn1}")
    resp1 = tutor.teach(turn1)
    print(f"\nTutor: {resp1}")

    turn2 = "It relates force and acceleration?"
    print(f"\nStudent: {turn2}")
    resp2 = tutor.teach(turn2)
    print(f"\nTutor: {resp2}")

    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nSocratic Tutor Features Demonstrated:")
    print("  ✓ Socratic teaching method (guided questions)")
    print("  ✓ Context awareness")
    print("  ✓ Sub-agent delegation (PhysicsCalculator)")
    print("  ✓ Hint provision with graduated levels")
    print("  ✓ Work verification with constructive feedback")
    print("  ✓ Problem suggestion")
    print("  ✓ Multi-turn conversation memory")
    print("=" * 70)
