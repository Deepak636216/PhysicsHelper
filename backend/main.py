"""
JEE-Helper FastAPI Backend

Main application that integrates multi-agent system with Session and Memory services.
"""

import os
import traceback
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import services
from services.session_service import SessionService
from services.memory_bank import MemoryBank
from services.solution_fetcher import create_solution_fetcher
from services.progress_tracker import create_progress_tracker
from services.conversation_logger import ConversationLogger

# Import agents
from agents.physics_calculator import create_physics_calculator
from agents.socratic_tutor import create_socratic_tutor
from agents.solution_validator import create_solution_validator
from agents.coordinator import create_coordinator

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="JEE-Helper API",
    description="Multi-Agent Physics Tutoring System",
    version="1.0.0"
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services and agents (initialized on startup)
session_service: Optional[SessionService] = None
memory_bank: Optional[MemoryBank] = None
coordinator_agent = None
progress_tracker = None
conversation_logger: Optional[ConversationLogger] = None


# Pydantic models for request/response
class ChatRequest(BaseModel):
    student_id: str
    message: str
    topic: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_used: str
    confidence: float
    success: bool
    metadata: dict


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict


class TopicResponse(BaseModel):
    topics: dict
    total_problems: int


class HintRequest(BaseModel):
    student_id: str
    session_id: str


class HintResponse(BaseModel):
    success: bool
    hint: Optional[str] = None
    hint_level: int
    hints_used: int
    hints_remaining: int
    message: Optional[str] = None


class SolutionRequest(BaseModel):
    student_id: str
    session_id: str


class SolutionResponse(BaseModel):
    solution_unlocked: bool
    progress_percentage: int
    solution: Optional[str] = None
    final_answer: Optional[str] = None
    feedback: str
    covered_concepts: list
    missing_concepts: list
    evaluation_method: str


class ConversationLogRequest(BaseModel):
    session_id: str
    student_id: str
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    messages: list
    interactions: list
    hints_requested: int
    solution_requested: bool
    metadata: dict
    final_metadata: Optional[dict] = None


class LogAnalyticsResponse(BaseModel):
    total_sessions: int
    total_messages: int
    total_hints_requested: int
    total_solutions_requested: int
    avg_messages_per_session: float
    avg_session_duration_seconds: float
    sessions_by_date: dict
    unique_students: int


@app.on_event("startup")
async def startup_event():
    """Initialize services and agents on startup."""
    global session_service, memory_bank, coordinator_agent, progress_tracker, conversation_logger

    print("🚀 Starting JEE-Helper API...")

    # Initialize services
    session_service = SessionService(session_timeout_minutes=60)
    memory_bank = MemoryBank(storage_dir="backend/data/memory")
    conversation_logger = ConversationLogger(log_dir="backend/data/conversation_logs")

    print("✅ Services initialized")

    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not found")
        return

    # Initialize agents
    try:
        # Create progress tracker
        progress_tracker = create_progress_tracker(api_key)
        print("✅ Progress tracker initialized")

        # Create solution fetcher (with Google Search)
        solution_fetcher = create_solution_fetcher(api_key)
        print("✅ Solution fetcher initialized (with Google Search)")

        # Create specialist agents
        calculator = create_physics_calculator(api_key)
        tutor = create_socratic_tutor(api_key, physics_calculator=calculator)
        validator = create_solution_validator(api_key, physics_calculator=calculator)

        # Create coordinator with solution fetcher
        coordinator_agent = create_coordinator(
            api_key=api_key,
            socratic_tutor=tutor,
            solution_validator=validator,
            physics_calculator=calculator,
            solution_fetcher=solution_fetcher
        )
        print("✅ Multi-agent system initialized with ground truth fetching")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")

    print("🎉 JEE-Helper API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down JEE-Helper API...")
    if session_service:
        cleaned = session_service.cleanup_inactive_sessions()
        print(f"✅ Cleaned up {cleaned} inactive sessions")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "JEE-Helper API",
        "version": "1.0.0",
        "description": "Multi-Agent Physics Tutoring System",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "topics": "/api/topics",
            "session": "/api/session/{session_id}",
            "profile": "/api/student/{student_id}/profile"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "session_service": session_service is not None,
            "memory_bank": memory_bank is not None,
            "coordinator": coordinator_agent is not None
        }
    }


@app.get("/api/topics", response_model=TopicResponse)
async def get_topics():
    """Get available physics topics."""
    # Load from problem index
    from pathlib import Path
    import json

    index_path = Path("backend/data/extracted/problems_index.json")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Problem index not found")

    with open(index_path, 'r') as f:
        index_data = json.load(f)

    return {
        "topics": index_data.get("topics", {}),
        "total_problems": index_data.get("total_problems", 0)
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes student messages through multi-agent system.

    Flow:
    1. Get or create session
    2. Load student profile
    3. Process through coordinator
    4. Update session and memory
    5. Return response
    """
    if not coordinator_agent:
        raise HTTPException(status_code=503, detail="Agent system not initialized")

    try:
        # 1. Get or create session
        if request.session_id:
            session = session_service.get_session(request.session_id)
            if not session:
                # Session expired, create new one
                session_id = session_service.create_student_session(
                    request.student_id,
                    request.topic
                )
            else:
                # Use existing session
                session_id = request.session_id
        else:
            # Create new session
            session_id = session_service.create_student_session(
                request.student_id,
                request.topic
            )

        # 2. Load student profile
        profile = memory_bank.get_student_profile(request.student_id)
        if not profile:
            profile = memory_bank.create_student_profile(request.student_id)

        # 3. Build context
        context = request.context or {}
        context["student_profile"] = profile
        context["session_id"] = session_id
        if request.topic:
            context["topic"] = request.topic

        # 4. Store original problem if this is first message
        session = session_service.get_session(session_id)
        if session["state"]["interaction_count"] == 0:
            session_service.set_original_problem(session_id, request.message)

        # 5. Process through coordinator
        result = coordinator_agent.process_request(request.message, context)

        # 6. Store ground truth if fetched
        if 'ground_truth' in context and context['ground_truth']:
            session_service.set_ground_truth(session_id, context['ground_truth'])

        # 7. Update session
        session_service.increment_interaction(session_id)
        session_service.record_agent_usage(session_id, result['agent_used'])
        session_service.add_to_history(session_id, {
            "role": "user",
            "content": request.message,
            "agent": result['agent_used']
        })
        session_service.add_to_history(session_id, {
            "role": "assistant",
            "content": result['response'],
            "agent": result['agent_used']
        })

        # 8. Update real-time progress tracking
        session = session_service.get_session(session_id)
        if progress_tracker and session:
            ground_truth = session["state"].get("ground_truth")
            updated_session_state = progress_tracker.update_realtime_progress(
                session_state=session["state"],
                user_message=request.message,
                ground_truth=ground_truth
            )
            # Only update the lightweight_progress field
            session_service.update_session(session_id, {
                "lightweight_progress": updated_session_state.get("lightweight_progress")
            })

        # 9. Get session summary for metadata
        summary = session_service.get_session_summary(session_id)
        session = session_service.get_session(session_id)
        hints_remaining = session_service.get_hints_remaining(session_id)
        lightweight_progress = session["state"].get("lightweight_progress", {})

        # Use accurate progress if available (from deep evaluation), otherwise use heuristic
        last_accurate_progress = session["state"].get("last_accurate_progress")
        progress_score = last_accurate_progress if last_accurate_progress is not None else lightweight_progress.get("heuristic_score", 0)

        # 10. Return response (WITHOUT agent naming in response text)
        return {
            "session_id": session_id,
            "response": result['response'],  # Clean response, no agent prefix
            "agent_used": result['agent_used'],  # Keep in metadata for logging
            "confidence": result['confidence'],
            "success": result['success'],
            "metadata": {
                "interaction_count": summary['interaction_count'],
                "agents_used": summary['agents_used'],
                "tools_used": summary['tools_used'],
                "hints_provided": summary['hints_provided'],
                "hints_used": session["state"]["hints_used"],
                "hints_remaining": hints_remaining,
                "progress_score": progress_score
            }
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return session


@app.get("/api/student/{student_id}/profile")
async def get_student_profile(student_id: str):
    """Get student learning profile."""
    profile = memory_bank.get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Get learning stats
    stats = memory_bank.get_learning_stats(student_id)

    return {
        "profile": profile,
        "stats": stats
    }


@app.get("/api/student/{student_id}/sessions")
async def get_student_sessions(student_id: str):
    """Get all active sessions for a student."""
    sessions = session_service.get_student_sessions(student_id)
    return {
        "student_id": student_id,
        "active_sessions": sessions,
        "count": len(sessions)
    }


@app.post("/api/request-hint", response_model=HintResponse)
async def request_hint(request: HintRequest):
    """
    Request a progressive hint (max 3 hints per session).

    Hint Levels:
    1. General direction / theorem hint
    2. Formula structure / key relationship
    3. Detailed step / almost complete guidance
    """
    if not coordinator_agent:
        raise HTTPException(status_code=503, detail="Agent system not initialized")

    try:
        # Get session
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")

        # Check hint limit
        hints_remaining = session_service.get_hints_remaining(request.session_id)
        if hints_remaining <= 0:
            return {
                "success": False,
                "hint": None,
                "hint_level": session["state"]["hints_used"],
                "hints_used": session["state"]["hints_used"],
                "hints_remaining": 0,
                "message": "You've used all 3 hints! Try to solve it or request the solution."
            }

        # Increment hint counter
        session_service.increment_hints_used(request.session_id)
        session = session_service.get_session(request.session_id)
        hint_level = session["state"]["hints_used"]

        # Generate progressive hint based on level and ground truth
        ground_truth = session["state"].get("ground_truth")
        conversation_history = session["state"]["conversation_history"]

        hint = _generate_progressive_hint(
            level=hint_level,
            ground_truth=ground_truth,
            conversation_history=conversation_history
        )

        # Add hint to conversation history
        session_service.add_to_history(request.session_id, {
            "role": "system",
            "content": f"Hint {hint_level}/3: {hint}",
            "type": "hint"
        })

        return {
            "success": True,
            "hint": hint,
            "hint_level": hint_level,
            "hints_used": hint_level,
            "hints_remaining": 3 - hint_level,
            "message": None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error providing hint: {str(e)}")


@app.post("/api/request-solution", response_model=SolutionResponse)
async def request_solution(request: SolutionRequest):
    """
    Request solution unlock based on progress.

    Progressive Unlock:
    - < 40%: Locked, show encouragement
    - 40-49%: Show partial solution (concepts + approach)
    - >= 50%: Full solution unlocked
    """
    if not coordinator_agent or not progress_tracker:
        raise HTTPException(status_code=503, detail="Agent system not initialized")

    try:
        # Get session
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")

        # Get ground truth
        ground_truth = session["state"].get("ground_truth")
        if not ground_truth:
            # No ground truth available, allow solution
            return {
                "solution_unlocked": True,
                "progress_percentage": 100,
                "solution": "Solution is available (no verification data).",
                "final_answer": "N/A",
                "feedback": "No ground truth available for this problem.",
                "covered_concepts": [],
                "missing_concepts": [],
                "evaluation_method": "no_ground_truth"
            }

        # Get conversation history and original problem
        conversation_history = session["state"]["conversation_history"]
        original_problem = session["state"].get("original_problem", "Unknown problem")

        # Evaluate progress using hybrid tracker
        evaluation = progress_tracker.get_accurate_progress(
            conversation_history=conversation_history,
            ground_truth=ground_truth,
            problem_statement=original_problem,
            session_state=session["state"]
        )

        progress = evaluation['overall_progress']

        # Progressive unlock based on progress
        if progress >= 50:
            # Full solution unlocked
            detailed_solution = ground_truth.get('detailed_solution', 'Solution not available')
            final_answer = ground_truth.get('final_answer', 'N/A')

            # Store accurate progress in session for future reference
            session_service.update_session(request.session_id, {
                "last_accurate_progress": progress
            })

            return {
                "solution_unlocked": True,
                "progress_percentage": progress,
                "solution": detailed_solution,
                "final_answer": final_answer,
                "feedback": evaluation.get('feedback', f"Great work! You've completed {progress}% of the solution."),
                "covered_concepts": evaluation.get('covered_concepts', []),
                "missing_concepts": evaluation.get('missing_concepts', []),
                "evaluation_method": evaluation.get('method', 'deep_llm')
            }

        elif progress >= 40:
            # Partial solution (concepts + approach only)
            key_concepts = ground_truth.get('key_concepts', [])
            solution_steps = ground_truth.get('solution_steps', [])

            partial_solution = "**Key Concepts:**\n"
            partial_solution += "\n".join([f"- {concept}" for concept in key_concepts])
            partial_solution += "\n\n**Approach:**\n"
            partial_solution += "\n".join([f"{i+1}. {step}" for i, step in enumerate(solution_steps[:2])])
            partial_solution += "\n\n*Complete the problem to unlock the full solution (need 50% progress).*"

            # Store accurate progress in session for future reference
            session_service.update_session(request.session_id, {
                "last_accurate_progress": progress
            })

            return {
                "solution_unlocked": False,
                "progress_percentage": progress,
                "solution": partial_solution,
                "final_answer": None,
                "feedback": f"You're at {progress}%! Here are the key concepts and approach. Try to complete the solution.",
                "covered_concepts": evaluation.get('covered_concepts', []),
                "missing_concepts": evaluation.get('missing_concepts', []),
                "evaluation_method": evaluation.get('method', 'deep_llm')
            }

        else:
            # Locked - need more progress
            missing = evaluation.get('missing_concepts', [])
            encouragement = f"You're at {progress}%. "
            if missing:
                encouragement += f"Try exploring: {', '.join(missing[:2])}."
            else:
                encouragement += "Keep working through the problem step by step!"

            # Store accurate progress in session for future reference
            session_service.update_session(request.session_id, {
                "last_accurate_progress": progress
            })

            return {
                "solution_unlocked": False,
                "progress_percentage": progress,
                "solution": None,
                "final_answer": None,
                "feedback": encouragement,
                "covered_concepts": evaluation.get('covered_concepts', []),
                "missing_concepts": missing,
                "evaluation_method": evaluation.get('method', 'deep_llm')
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating solution request: {str(e)}")


def _generate_progressive_hint(
    level: int,
    ground_truth: Optional[dict],
    conversation_history: list
) -> str:
    """Generate progressive hint based on level (1-3)."""

    if not ground_truth:
        generic_hints = [
            "Think about the fundamental principles that apply to this problem.",
            "Consider the relationships between the given quantities and what you need to find.",
            "Try breaking down the problem into smaller steps and solve each part systematically."
        ]
        return generic_hints[min(level-1, 2)]

    key_concepts = ground_truth.get('key_concepts', [])
    solution_steps = ground_truth.get('solution_steps', [])

    if level == 1:
        # Level 1: General direction / theorem
        if key_concepts:
            return f"💡 Hint 1: Think about {key_concepts[0]}. This is a key concept for solving this problem."
        return "💡 Hint 1: Consider which fundamental theorem or principle applies to this scenario."

    elif level == 2:
        # Level 2: Formula structure / key relationship
        if len(solution_steps) > 0:
            return f"💡 Hint 2: {solution_steps[0]}. What formula or relationship does this suggest?"
        elif len(key_concepts) > 1:
            return f"💡 Hint 2: You'll need to combine {key_concepts[0]} with {key_concepts[1]}."
        return "💡 Hint 2: Think about the mathematical relationship between the quantities involved."

    else:  # level == 3
        # Level 3: Detailed step / almost complete
        if len(solution_steps) > 1:
            return f"💡 Hint 3: After {solution_steps[0]}, the next step is to {solution_steps[1]}."
        elif len(key_concepts) > 2:
            return f"💡 Hint 3: Apply {key_concepts[2]} to connect the pieces together."
        return "💡 Hint 3: You're very close! Set up the equation and solve step by step."


@app.post("/api/log-conversation")
async def log_conversation(request: ConversationLogRequest):
    """
    Log a conversation session for analysis

    Stores conversation data including messages, interactions, hints, and metadata
    """
    if not conversation_logger:
        raise HTTPException(status_code=503, detail="Conversation logger not initialized")

    try:
        log_data = request.dict()
        filepath = conversation_logger.log_conversation(log_data)

        return {
            "success": True,
            "message": "Conversation logged successfully",
            "filepath": filepath
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging conversation: {str(e)}")


@app.get("/api/conversation-logs")
async def get_conversation_logs(limit: Optional[int] = 50):
    """Get all conversation logs (most recent first)"""
    if not conversation_logger:
        raise HTTPException(status_code=503, detail="Conversation logger not initialized")

    try:
        logs = conversation_logger.get_all_logs(limit=limit)
        return {
            "success": True,
            "count": len(logs),
            "logs": logs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")


@app.get("/api/conversation-logs/student/{student_id}")
async def get_student_logs(student_id: str, limit: Optional[int] = 20):
    """Get conversation logs for a specific student"""
    if not conversation_logger:
        raise HTTPException(status_code=503, detail="Conversation logger not initialized")

    try:
        logs = conversation_logger.get_logs_by_student(student_id, limit=limit)
        return {
            "success": True,
            "student_id": student_id,
            "count": len(logs),
            "logs": logs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student logs: {str(e)}")


@app.get("/api/conversation-analytics", response_model=LogAnalyticsResponse)
async def get_conversation_analytics():
    """Get analytics summary of all conversations"""
    if not conversation_logger:
        raise HTTPException(status_code=503, detail="Conversation logger not initialized")

    try:
        analytics = conversation_logger.get_analytics_summary()
        return analytics

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))

    print("=" * 70)
    print("Starting JEE-Helper API Server")
    print("=" * 70)
    print(f"Port: {port}")
    print(f"Docs: http://localhost:{port}/docs")
    print(f"Health: http://localhost:{port}/api/health")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=port)
