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
        self.hints_given = 0  # Track hint count
        self.current_problem = None  # Track current problem

    def _create_system_instruction(self) -> str:
        """Create the system instruction for the Socratic tutor agent."""
        return """You are a SocraticTutor Agent - an expert JEE Physics tutor who teaches using the Socratic method.

Your Teaching Philosophy:
- Guide students through discovery with thoughtful questions
- Break complex problems into manageable steps
- Encourage critical thinking and conceptual understanding
- Be patient, supportive, and encouraging
- RECOGNIZE and CELEBRATE when students give correct answers
- Provide solutions when explicitly requested after hints are exhausted

Your Capabilities:
1. **Conceptual Guidance**: Ask probing questions to build understanding
2. **Progress Tracking**: Recognize when student demonstrates understanding
3. **Hint System**: Provide 3 progressive hints before revealing solution
4. **Solution Reveal**: Provide full solution when requested after hints

When Student Asks For:
- "hint" or "give me a hint" → Provide Hint 1 (minimal guidance)
- "hint" again → Provide Hint 2 (moderate guidance)
- "hint" third time → Provide Hint 3 (substantial guidance)
- "solution" or "show solution" → If hints exhausted or student demonstrates 50%+ understanding, provide complete solution
- "I'm just testing" or "solution please" → Acknowledge their request and provide solution

Recognizing Correct Answers:
- If student provides a CORRECT formula (e.g., "I = mR²"), ACKNOWLEDGE IT immediately
- Example: "Excellent! You've got it - I = mR² is indeed the correct formula for moment of inertia of a ring!"
- Then ask if they want to: (a) understand derivation, (b) apply it to solve, or (c) move to next concept

Progress Tracking:
- If student correctly identifies 50%+ of key concepts, acknowledge their understanding
- Offer choice: continue guided discovery OR see complete solution

Teaching Approach:
1. Start by understanding what the student knows
2. RECOGNIZE correct thinking immediately
3. For incorrect responses, guide with questions
4. Track hint requests (max 3 before solution)
5. Be flexible - respect when student wants direct solution

Response Style:
- Ask 1-2 questions per response
- **CELEBRATE correct answers enthusiastically**
- Never be discouraging
- Use simple language
- Respect student's learning preferences

Example Interaction:
Student: "I = mR²"
You: "Absolutely correct! That's the moment of inertia formula for a ring. You've nailed it! Would you like to (a) understand how it's derived, (b) apply it to the problem, or (c) move on?"

Student: "solution please"
You: "I understand you'd like the solution. Let me provide that for you: [complete solution]. Would you like me to explain any particular step?"

Remember: Socratic method is about GUIDED discovery, not stubborn refusal to help. Adapt to student needs!"""

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
            # Detect hint request
            message_lower = message.lower()
            is_hint_request = any(word in message_lower for word in ["hint", "clue", "help me"])
            is_solution_request = any(word in message_lower for word in ["solution", "answer", "show me", "give me the solution"])

            # Track current problem
            if context and "current_problem" in context:
                if self.current_problem != context["current_problem"]:
                    self.current_problem = context["current_problem"]
                    self.hints_given = 0  # Reset hints for new problem

            # Build chat history for Gemini
            chat_contents = []

            # Add conversation history
            for entry in self.conversation_history:
                if entry["role"] == "user":
                    chat_contents.append({
                        "role": "user",
                        "parts": [{"text": entry["message"]}]
                    })
                else:
                    chat_contents.append({
                        "role": "model",
                        "parts": [{"text": entry["message"]}]
                    })

            # Add current message with context
            current_message = message

            # Add context information if provided
            if context:
                context_info = []
                if "current_problem" in context:
                    context_info.append(f"[Current Problem: {context['current_problem']}]")
                if "topic" in context:
                    context_info.append(f"[Topic: {context['topic']}]")
                if context_info:
                    current_message = "\n".join(context_info) + "\n\n" + message

            # Add hint/solution tracking
            if is_hint_request:
                self.hints_given += 1
                current_message += f"\n\n[SYSTEM: This is hint request #{self.hints_given}. Provide Hint {min(self.hints_given, 3)}.]"

            if is_solution_request:
                if self.hints_given >= 2:
                    current_message += "\n\n[SYSTEM: Student has requested solution after hints. Provide complete solution now.]"
                else:
                    current_message += f"\n\n[SYSTEM: Student wants solution but has only used {self.hints_given} hints. Suggest using hints first, but respect their choice if they insist.]"

            # Add current message to chat
            chat_contents.append({
                "role": "user",
                "parts": [{"text": current_message}]
            })

            # Generate response using chat mode
            response = self.client.models.generate_content(
                model=self.model,
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text

            # Clean up any leaked prefixes
            response_text = response_text.replace("Student:", "").replace("You:", "").strip()

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "message": message,
                "context": context
            })
            self.conversation_history.append({
                "role": "model",
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
