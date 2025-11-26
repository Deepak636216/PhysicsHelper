"""
JEE-Helper FastAPI Backend

Main application that integrates multi-agent system with Session and Memory services.
"""

import os
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


@app.on_event("startup")
async def startup_event():
    """Initialize services and agents on startup."""
    global session_service, memory_bank, coordinator_agent

    print("🚀 Starting JEE-Helper API...")

    # Initialize services
    session_service = SessionService(session_timeout_minutes=60)
    memory_bank = MemoryBank(storage_dir="backend/data/memory")

    print("✅ Services initialized")

    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not found")
        return

    # Initialize agents
    try:
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

        # 4. Process through coordinator
        result = coordinator_agent.process_request(request.message, context)

        # 5. Update session
        session_service.increment_interaction(session_id)
        session_service.record_agent_usage(session_id, result['agent_used'])
        session_service.add_to_history(session_id, {
            "role": "user",
            "message": request.message,
            "agent": result['agent_used']
        })
        session_service.add_to_history(session_id, {
            "role": "agent",
            "message": result['response'],
            "agent": result['agent_used']
        })

        # 6. Get session summary for metadata
        summary = session_service.get_session_summary(session_id)

        # 7. Return response
        return {
            "session_id": session_id,
            "response": result['response'],
            "agent_used": result['agent_used'],
            "confidence": result['confidence'],
            "success": result['success'],
            "metadata": {
                "interaction_count": summary['interaction_count'],
                "agents_used": summary['agents_used'],
                "tools_used": summary['tools_used'],
                "hints_provided": summary['hints_provided']
            }
        }

    except Exception as e:
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
