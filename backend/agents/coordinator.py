"""
Coordinator Agent

Top-level agent that routes student requests to appropriate specialist agents.
Acts as the main entry point for the multi-agent tutoring system.
"""

from google import genai
from google.genai import types
from typing import Optional, Dict, Any, Tuple
import json


class CoordinatorAgent:
    """
    Coordinator agent that routes requests to specialist sub-agents.

    This agent:
    - Analyzes student requests to determine intent
    - Routes to appropriate specialist (SocraticTutor, SolutionValidator, PhysicsCalculator)
    - Maintains conversation context
    - Provides seamless multi-agent experience
    """

    def __init__(
        self,
        api_key: str,
        socratic_tutor=None,
        solution_validator=None,
        physics_calculator=None,
        model: str = "gemini-2.5-flash-lite"
    ):
        """
        Initialize the Coordinator agent.

        Args:
            api_key: Google AI API key
            socratic_tutor: SocraticTutorAgent instance
            solution_validator: SolutionValidatorAgent instance
            physics_calculator: PhysicsCalculatorAgent instance
            model: Model to use (default: gemini-2.5-flash-lite)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.socratic_tutor = socratic_tutor
        self.solution_validator = solution_validator
        self.physics_calculator = physics_calculator
        self.system_instruction = self._create_system_instruction()
        self.conversation_history = []

    def _create_system_instruction(self) -> str:
        """Create the system instruction for the coordinator agent."""
        return """You are a JEECoordinator Agent - the main interface for a JEE Physics tutoring system.

Your Role:
- Analyze student requests to understand their intent
- Route requests to the appropriate specialist agent
- Provide a seamless, intelligent tutoring experience
- Maintain friendly, encouraging communication

Available Specialist Agents:
1. **SocraticTutor** - Use for:
   - Student wants to learn/understand concepts
   - Requests for practice problems
   - Needs guidance solving problems
   - Wants hints or help
   - General tutoring/teaching needs

2. **SolutionValidator** - Use for:
   - Student wants solution checked
   - "Is my answer correct?"
   - "Can you verify my work?"
   - Needs feedback on completed solution
   - Validation requests

3. **PhysicsCalculator** - Use for:
   - Direct calculation requests
   - "Calculate force when..."
   - Quick numerical problems
   - No teaching context needed
   - Student just needs a calculation done

Routing Decision Process:
1. Identify the student's primary need
2. Choose the most appropriate specialist
3. Route the entire request to that agent
4. Let the specialist handle the interaction

Key Phrases to Recognize:
- "practice problem", "help me solve", "I don't understand" → SocraticTutor
- "check my answer", "is this correct", "verify my solution" → SolutionValidator
- "calculate", "what is the force", "find the energy" → PhysicsCalculator

Important:
- You are a router, not a teacher - let specialists do their job
- Don't teach or validate yourself - delegate immediately
- Keep routing decisions invisible to the student
- Make the experience feel seamless

Response Format:
When routing, simply provide a natural transition like:
- "Let me help you understand this concept..." (then route to SocraticTutor)
- "I'll check your solution..." (then route to SolutionValidator)
- "Let me calculate that for you..." (then route to PhysicsCalculator)"""

    def process_request(
        self,
        student_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a student request and route to appropriate agent.

        Args:
            student_message: Student's message
            context: Optional context (problem, topic, etc.)

        Returns:
            Dictionary with agent response and metadata
        """
        try:
            # Analyze intent and determine routing
            agent_choice, confidence = self._route_request(student_message, context)

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "message": student_message,
                "context": context,
                "routed_to": agent_choice
            })

            # Route to appropriate agent
            if agent_choice == "socratic_tutor":
                response = self._route_to_socratic_tutor(student_message, context)
            elif agent_choice == "solution_validator":
                response = self._route_to_solution_validator(student_message, context)
            elif agent_choice == "physics_calculator":
                response = self._route_to_physics_calculator(student_message, context)
            else:
                response = "I apologize, but I'm having trouble understanding your request. Could you please rephrase?"

            # Add response to history
            self.conversation_history.append({
                "role": "agent",
                "agent": agent_choice,
                "response": response
            })

            return {
                "response": response,
                "agent_used": agent_choice,
                "confidence": confidence,
                "success": True
            }

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "agent_used": "none",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    def _route_request(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, float]:
        """
        Determine which agent should handle the request.

        Args:
            message: Student's message
            context: Optional context

        Returns:
            Tuple of (agent_name, confidence_score)
        """
        message_lower = message.lower()

        # Keywords for each agent
        validator_keywords = [
            "check", "verify", "correct", "is this right", "validate",
            "review my", "look at my", "is my answer", "feedback on my"
        ]

        calculator_keywords = [
            "calculate", "compute", "find the", "what is the value",
            "solve for", "determine the", "evaluate"
        ]

        tutor_keywords = [
            "help", "understand", "explain", "teach", "practice",
            "hint", "confused", "don't get", "how do i", "guide me",
            "problem", "stuck", "learn"
        ]

        # Score each agent
        validator_score = sum(1 for kw in validator_keywords if kw in message_lower)
        calculator_score = sum(1 for kw in calculator_keywords if kw in message_lower)
        tutor_score = sum(1 for kw in tutor_keywords if kw in message_lower)

        # Special case: If context includes "student_solution", likely validation
        if context and "student_solution" in context:
            validator_score += 3

        # Special case: If message is very short and numerical, likely calculation
        if len(message.split()) < 15 and any(kw in message_lower for kw in calculator_keywords):
            calculator_score += 2

        # Determine winner
        scores = {
            "solution_validator": validator_score,
            "physics_calculator": calculator_score,
            "socratic_tutor": tutor_score
        }

        # Default to SocraticTutor if unclear
        if max(scores.values()) == 0:
            return "socratic_tutor", 0.5

        agent = max(scores, key=scores.get)
        confidence = scores[agent] / (sum(scores.values()) + 0.01)  # Avoid division by zero

        return agent, confidence

    def _route_to_socratic_tutor(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Route request to SocraticTutor."""
        if self.socratic_tutor is None:
            return "The tutoring system is currently unavailable. Please try again later."

        return self.socratic_tutor.teach(message, context)

    def _route_to_solution_validator(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Route request to SolutionValidator."""
        if self.solution_validator is None:
            return "The solution validation system is currently unavailable. Please try again later."

        # Extract problem and solution from context if available
        if context:
            problem = context.get("problem", "")
            student_solution = context.get("student_solution", message)
        else:
            problem = "Please check this solution"
            student_solution = message

        return self.solution_validator.validate(problem, student_solution, context)

    def _route_to_physics_calculator(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Route request to PhysicsCalculator."""
        if self.physics_calculator is None:
            return "The calculation system is currently unavailable. Please try again later."

        return self.physics_calculator.calculate(message)

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary of conversation history.

        Returns:
            Summary with agent usage statistics
        """
        if not self.conversation_history:
            return {
                "total_interactions": 0,
                "agent_usage": {},
                "conversation_length": 0
            }

        agent_usage = {}
        for entry in self.conversation_history:
            if entry.get("role") == "agent":
                agent = entry.get("agent", "unknown")
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        return {
            "total_interactions": len([e for e in self.conversation_history if e.get("role") == "user"]),
            "agent_usage": agent_usage,
            "conversation_length": len(self.conversation_history)
        }

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def create_coordinator(
    api_key: str,
    socratic_tutor=None,
    solution_validator=None,
    physics_calculator=None
) -> CoordinatorAgent:
    """
    Factory function to create a CoordinatorAgent.

    Args:
        api_key: Google AI API key
        socratic_tutor: SocraticTutorAgent instance
        solution_validator: SolutionValidatorAgent instance
        physics_calculator: PhysicsCalculatorAgent instance

    Returns:
        Initialized CoordinatorAgent
    """
    return CoordinatorAgent(
        api_key=api_key,
        socratic_tutor=socratic_tutor,
        solution_validator=solution_validator,
        physics_calculator=physics_calculator
    )


# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from physics_calculator import create_physics_calculator
    from socratic_tutor import create_socratic_tutor
    from solution_validator import create_solution_validator

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        exit(1)

    print("=" * 70)
    print("Coordinator Agent - Test Suite")
    print("=" * 70)

    # Create all specialist agents
    calculator = create_physics_calculator(api_key)
    tutor = create_socratic_tutor(api_key, physics_calculator=calculator)
    validator = create_solution_validator(api_key, physics_calculator=calculator)

    # Create coordinator with all specialists
    coordinator = create_coordinator(
        api_key=api_key,
        socratic_tutor=tutor,
        solution_validator=validator,
        physics_calculator=calculator
    )

    # Test 1: Request for help (should route to SocraticTutor)
    print("\n" + "=" * 70)
    print("Test 1: Request for Help (Route to SocraticTutor)")
    print("=" * 70)
    request1 = "I need help understanding Newton's laws"
    print(f"\nStudent: {request1}")
    result1 = coordinator.process_request(request1)
    print(f"\nRouted to: {result1['agent_used']}")
    print(f"Confidence: {result1['confidence']:.2f}")
    print(f"\nResponse:\n{result1['response']}")

    # Test 2: Practice problem request (should route to SocraticTutor)
    print("\n" + "=" * 70)
    print("Test 2: Practice Problem Request (Route to SocraticTutor)")
    print("=" * 70)
    request2 = "Can I get a practice problem on kinematics?"
    print(f"\nStudent: {request2}")
    result2 = coordinator.process_request(request2)
    print(f"\nRouted to: {result2['agent_used']}")
    print(f"Confidence: {result2['confidence']:.2f}")
    print(f"\nResponse:\n{result2['response']}")

    # Test 3: Solution validation (should route to SolutionValidator)
    print("\n" + "=" * 70)
    print("Test 3: Solution Validation (Route to SolutionValidator)")
    print("=" * 70)
    request3 = "Can you check if my answer is correct?"
    context3 = {
        "problem": "Calculate force when m=5kg, a=10m/s²",
        "student_solution": "F = ma = 5 × 10 = 50 N"
    }
    print(f"\nStudent: {request3}")
    print(f"Context: Problem + Solution provided")
    result3 = coordinator.process_request(request3, context=context3)
    print(f"\nRouted to: {result3['agent_used']}")
    print(f"Confidence: {result3['confidence']:.2f}")
    print(f"\nResponse:\n{result3['response'][:300]}...")  # Truncate for readability

    # Test 4: Direct calculation (should route to PhysicsCalculator)
    print("\n" + "=" * 70)
    print("Test 4: Direct Calculation (Route to PhysicsCalculator)")
    print("=" * 70)
    request4 = "Calculate the force when mass is 5 kg and acceleration is 10 m/s²"
    print(f"\nStudent: {request4}")
    result4 = coordinator.process_request(request4)
    print(f"\nRouted to: {result4['agent_used']}")
    print(f"Confidence: {result4['confidence']:.2f}")
    print(f"\nResponse:\n{result4['response']}")

    # Test 5: Verification request (should route to SolutionValidator)
    print("\n" + "=" * 70)
    print("Test 5: Verify My Work (Route to SolutionValidator)")
    print("=" * 70)
    request5 = "Can you verify my solution? I got F = 500 N for m=5kg, a=10m/s²"
    context5 = {
        "problem": "Calculate force when m=5kg, a=10m/s²",
        "student_solution": "F = ma = 5 × 10 = 500 N"
    }
    print(f"\nStudent: {request5}")
    result5 = coordinator.process_request(request5, context=context5)
    print(f"\nRouted to: {result5['agent_used']}")
    print(f"Confidence: {result5['confidence']:.2f}")
    print(f"\nResponse:\n{result5['response'][:300]}...")  # Truncate for readability

    # Test 6: Ambiguous request (should default to SocraticTutor)
    print("\n" + "=" * 70)
    print("Test 6: Ambiguous Request (Default to SocraticTutor)")
    print("=" * 70)
    request6 = "Physics is hard"
    print(f"\nStudent: {request6}")
    result6 = coordinator.process_request(request6)
    print(f"\nRouted to: {result6['agent_used']}")
    print(f"Confidence: {result6['confidence']:.2f}")
    print(f"\nResponse:\n{result6['response']}")

    # Test 7: Hint request (should route to SocraticTutor)
    print("\n" + "=" * 70)
    print("Test 7: Hint Request (Route to SocraticTutor)")
    print("=" * 70)
    request7 = "I'm stuck on this problem, can you give me a hint?"
    print(f"\nStudent: {request7}")
    result7 = coordinator.process_request(request7)
    print(f"\nRouted to: {result7['agent_used']}")
    print(f"Confidence: {result7['confidence']:.2f}")
    print(f"\nResponse:\n{result7['response']}")

    # Summary
    print("\n" + "=" * 70)
    print("Conversation Summary")
    print("=" * 70)
    summary = coordinator.get_conversation_summary()
    print(f"\nTotal Interactions: {summary['total_interactions']}")
    print(f"Conversation Length: {summary['conversation_length']} exchanges")
    print("\nAgent Usage:")
    for agent, count in summary['agent_usage'].items():
        print(f"  - {agent}: {count} times")

    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nCoordinator Features Demonstrated:")
    print("  ✓ Intent analysis and routing")
    print("  ✓ Routes to SocraticTutor (teaching/help)")
    print("  ✓ Routes to SolutionValidator (verification)")
    print("  ✓ Routes to PhysicsCalculator (calculations)")
    print("  ✓ Context-aware routing")
    print("  ✓ Conversation history tracking")
    print("  ✓ Agent usage statistics")
    print("  ✓ Seamless multi-agent experience")
    print("=" * 70)
