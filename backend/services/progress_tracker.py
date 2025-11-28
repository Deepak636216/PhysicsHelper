"""
Hybrid Progress Tracking System

Combines lightweight real-time tracking with on-demand deep LLM evaluation.
- Real-time: Fast heuristics updated with each message
- On-demand: Accurate LLM evaluation when solution/advanced hints requested
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from google import genai


class LightweightProgressTracker:
    """
    Fast, lightweight progress tracking using simple heuristics.
    Updated in real-time with each message (no LLM calls).
    """

    def __init__(self):
        self.physics_keywords = {
            'high_value': [
                'theorem', 'law', 'principle', 'equation', 'formula',
                'derive', 'integration', 'differentiation', 'substitution'
            ],
            'medium_value': [
                'mass', 'velocity', 'acceleration', 'force', 'energy',
                'momentum', 'torque', 'inertia', 'axis', 'symmetry'
            ],
            'concept_indicators': [
                'because', 'therefore', 'since', 'so', 'thus',
                'apply', 'using', 'considering'
            ]
        }

    def update_progress(
        self,
        session_state: Dict[str, Any],
        new_message: str,
        ground_truth: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Update progress metrics based on new user message.
        Fast heuristic-based calculation.

        Returns updated session state with progress metrics
        """

        # Initialize progress if not exists or is empty
        if 'lightweight_progress' not in session_state or not session_state.get('lightweight_progress'):
            session_state['lightweight_progress'] = {
                'message_count': 0,
                'keywords_mentioned': [],
                'concept_indicators_used': 0,
                'formulas_attempted': 0,
                'questions_asked': 0,
                'heuristic_score': 0
            }

        progress = session_state['lightweight_progress']

        # Double check all required keys exist (in case of partial initialization)
        if 'message_count' not in progress:
            progress['message_count'] = 0
        if 'keywords_mentioned' not in progress:
            progress['keywords_mentioned'] = []
        if 'concept_indicators_used' not in progress:
            progress['concept_indicators_used'] = 0
        if 'formulas_attempted' not in progress:
            progress['formulas_attempted'] = 0
        if 'questions_asked' not in progress:
            progress['questions_asked'] = 0
        if 'heuristic_score' not in progress:
            progress['heuristic_score'] = 0
        message_lower = new_message.lower()

        # Update metrics
        progress['message_count'] += 1

        # Check for keywords
        for keyword in self.physics_keywords['high_value']:
            if keyword in message_lower and keyword not in progress['keywords_mentioned']:
                progress['keywords_mentioned'].append(keyword)

        for keyword in self.physics_keywords['medium_value']:
            if keyword in message_lower and keyword not in progress['keywords_mentioned']:
                progress['keywords_mentioned'].append(keyword)

        # Check for reasoning indicators
        for indicator in self.physics_keywords['concept_indicators']:
            if indicator in message_lower:
                progress['concept_indicators_used'] += 1
                break  # Count once per message

        # Check for formulas (contains =, *, /, ^, or mathematical symbols)
        if any(symbol in new_message for symbol in ['=', '*', '/', '^', '²', '³', '√']):
            progress['formulas_attempted'] += 1

        # Check for questions (engaged thinking)
        if '?' in new_message:
            progress['questions_asked'] += 1

        # Calculate heuristic score (0-100)
        score = self._calculate_heuristic_score(progress, ground_truth)
        progress['heuristic_score'] = score

        session_state['lightweight_progress'] = progress
        return session_state

    def _calculate_heuristic_score(
        self,
        progress: Dict[str, Any],
        ground_truth: Optional[Dict]
    ) -> int:
        """
        Calculate progress score using lightweight heuristics.
        Returns 0-100 score.
        """

        score = 0

        # 1. Message engagement (max 25 points)
        # More messages = more engagement, capped at 15 messages
        message_score = min(25, (progress['message_count'] / 15) * 25)
        score += message_score

        # 2. Keywords mentioned (max 30 points)
        # Presence of high-value physics keywords
        keyword_score = min(30, len(progress['keywords_mentioned']) * 5)
        score += keyword_score

        # 3. Reasoning indicators (max 20 points)
        # Student explaining their thinking
        reasoning_score = min(20, progress['concept_indicators_used'] * 4)
        score += reasoning_score

        # 4. Formula attempts (max 15 points)
        # Student trying calculations
        formula_score = min(15, progress['formulas_attempted'] * 5)
        score += formula_score

        # 5. Questions asked (max 10 points)
        # Engaged curiosity
        question_score = min(10, progress['questions_asked'] * 3)
        score += question_score

        return min(100, int(score))

    def should_trigger_deep_evaluation(self, session_state: Dict[str, Any]) -> bool:
        """
        Determine if we need expensive LLM evaluation.
        Use lightweight heuristic first to avoid unnecessary cost.
        """

        if 'lightweight_progress' not in session_state:
            return True  # No data, need deep eval

        progress = session_state['lightweight_progress']
        score = progress['heuristic_score']

        # If clearly below or above threshold, skip deep eval
        if score < 30:
            return False  # Clearly not ready
        elif score > 70:
            return False  # Clearly ready
        else:
            return True  # Borderline 30-70%, need accurate evaluation


class DeepProgressEvaluator:
    """
    Accurate LLM-based progress evaluation.
    Used on-demand when solution requested or borderline cases.
    Includes caching to prevent duplicate evaluations.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.evaluation_cache = {}  # Cache by conversation hash

    def evaluate_progress(
        self,
        conversation_history: List[Dict[str, str]],
        ground_truth: Dict[str, Any],
        problem_statement: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Deep evaluation using LLM to compare conversation with ground truth.
        Returns detailed progress analysis.
        """

        # Check cache first
        cache_key = self._get_cache_key(conversation_history)
        if use_cache and cache_key in self.evaluation_cache:
            cached_result = self.evaluation_cache[cache_key]
            cached_result['from_cache'] = True
            return cached_result

        # Step 1: Summarize student conversation
        student_summary = self._summarize_conversation(conversation_history)

        # Step 2: Compare with ground truth
        evaluation = self._compare_with_ground_truth(
            student_summary,
            ground_truth,
            problem_statement,
            conversation_history
        )

        # Cache result
        evaluation['from_cache'] = False
        evaluation['evaluated_at'] = datetime.now().isoformat()
        self.evaluation_cache[cache_key] = evaluation

        return evaluation

    def _get_cache_key(self, conversation_history: List[Dict[str, str]]) -> str:
        """Generate unique hash for conversation state"""
        conversation_text = json.dumps(conversation_history, sort_keys=True)
        return hashlib.md5(conversation_text.encode()).hexdigest()

    def _summarize_conversation(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Summarize student's understanding from conversation.
        Focuses only on user messages.
        """

        # Extract user messages only
        user_messages = [
            msg['content'] for msg in conversation_history
            if msg.get('role') == 'user' and msg['content'].lower() not in ['hint', 'solution', 'solution please']
        ]

        if not user_messages:
            return "Student has not provided substantive responses yet."

        prompt = f"""Summarize the student's physics understanding from their messages.

Student Messages:
{json.dumps(user_messages, indent=2)}

Provide a concise summary covering:
1. Physics concepts/theorems mentioned
2. Formulas or equations attempted
3. Relationships or principles identified
4. Understanding demonstrated through explanations
5. Calculations or derivations attempted

Format: Structured bullet points (not conversational).
Keep it brief but comprehensive."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'temperature': 0.3,
                    'max_output_tokens': 400
                }
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Summarization error: {e}")
            return "Unable to summarize conversation."

    def _compare_with_ground_truth(
        self,
        student_summary: str,
        ground_truth: Dict[str, Any],
        problem_statement: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Compare student understanding with ground truth solution.
        Returns progress percentage and detailed breakdown.
        """

        # Build prompt for evaluation
        prompt = f"""You are evaluating a physics student's progress.

**Problem:**
{problem_statement}

**Correct Solution (Ground Truth):**
Key Concepts: {json.dumps(ground_truth.get('key_concepts', []))}
Solution Steps: {json.dumps(ground_truth.get('solution_steps', []))}
Final Answer: {ground_truth.get('final_answer', 'N/A')}

**Student's Understanding:**
{student_summary}

**Evaluate Progress:**

1. **Concept Coverage (40% weight):**
   - How many key concepts identified?
   - Score: 0-100

2. **Approach Correctness (30% weight):**
   - Correct method/theorem?
   - Score: 0-100

3. **Calculation Progress (30% weight):**
   - Correct formulas attempted?
   - Score: 0-100

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "concept_score": 0-100,
  "approach_score": 0-100,
  "calculation_score": 0-100,
  "overall_progress": weighted_average,
  "covered_concepts": ["concept1"],
  "missing_concepts": ["concept2"],
  "understanding_level": "beginner|intermediate|advanced",
  "feedback": "Brief encouraging feedback"
}}

Be fair. 50%+ means student grasps core approach and key concepts."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'temperature': 0.2,
                    'max_output_tokens': 500
                }
            )

            # Parse JSON response
            result_text = response.text.strip()

            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('\n', 1)[1]
                result_text = result_text.rsplit('```', 1)[0]

            result = json.loads(result_text)

            # Validate and return
            return {
                'concept_score': result.get('concept_score', 25),
                'approach_score': result.get('approach_score', 25),
                'calculation_score': result.get('calculation_score', 25),
                'overall_progress': result.get('overall_progress', 25),
                'covered_concepts': result.get('covered_concepts', []),
                'missing_concepts': result.get('missing_concepts', []),
                'understanding_level': result.get('understanding_level', 'beginner'),
                'feedback': result.get('feedback', 'Continue working on the problem.')
            }

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"Response text: {response.text}")
            # Fallback to conservative estimate
            return self._fallback_evaluation(student_summary, ground_truth)
        except Exception as e:
            print(f"⚠️ Evaluation error: {e}")
            return self._fallback_evaluation(student_summary, ground_truth)

    def _fallback_evaluation(
        self,
        student_summary: str,
        ground_truth: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback evaluation if LLM fails"""

        # Simple keyword matching fallback
        summary_lower = student_summary.lower()
        key_concepts = ground_truth.get('key_concepts', [])

        matched = sum(1 for concept in key_concepts if concept.lower() in summary_lower)
        progress = int((matched / max(len(key_concepts), 1)) * 100) if key_concepts else 25

        return {
            'concept_score': progress,
            'approach_score': 25,
            'calculation_score': 25,
            'overall_progress': max(25, progress),
            'covered_concepts': [],
            'missing_concepts': key_concepts,
            'understanding_level': 'beginner',
            'feedback': 'Continue working through the problem step by step.'
        }


class HybridProgressTracker:
    """
    Combines lightweight real-time tracking with deep LLM evaluation.
    Best of both worlds: fast updates + accurate evaluation when needed.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        self.lightweight_tracker = LightweightProgressTracker()
        self.deep_evaluator = DeepProgressEvaluator(api_key, model)

    def update_realtime_progress(
        self,
        session_state: Dict[str, Any],
        user_message: str,
        ground_truth: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Fast real-time update (no LLM call).
        Called after each user message.
        """
        return self.lightweight_tracker.update_progress(
            session_state,
            user_message,
            ground_truth
        )

    def get_accurate_progress(
        self,
        conversation_history: List[Dict[str, str]],
        ground_truth: Dict[str, Any],
        problem_statement: str,
        session_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get accurate progress using LLM evaluation.
        Uses caching and lightweight heuristic to minimize cost.
        """

        # Check if deep evaluation is needed
        if not self.lightweight_tracker.should_trigger_deep_evaluation(session_state):
            # Use heuristic score
            heuristic = session_state.get('lightweight_progress', {})
            return {
                'overall_progress': heuristic.get('heuristic_score', 25),
                'method': 'heuristic',
                'feedback': 'Keep working through the problem!',
                'covered_concepts': [],
                'missing_concepts': ground_truth.get('key_concepts', [])
            }

        # Run deep evaluation
        evaluation = self.deep_evaluator.evaluate_progress(
            conversation_history,
            ground_truth,
            problem_statement
        )
        evaluation['method'] = 'deep_llm'
        return evaluation


def create_progress_tracker(api_key: str) -> HybridProgressTracker:
    """Factory function to create progress tracker"""
    return HybridProgressTracker(api_key=api_key)
