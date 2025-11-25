# **JEE-Helper MVP: Refined User Stories (Flow & Metadata Only)**

## **Project Overview**

**Project Name**: JEE-Helper Multi-Agent Physics Tutor  
**Technology Stack**: Google ADK, FastAPI, React, Google AI Studio (Gemini API)  
**Deployment**: Google Cloud Run (Free Tier)  
**Repository**: https://github.com/Deepak636216/JEE-Helper  

**Goal**: Convert to Google ADK multi-agent architecture with 4+ features: Multi-Agent System, Tools (MCP), Sessions & Memory, Observability

**Key Simplification**: 
- ✅ Gemini has built-in physics knowledge (no formula DB needed)
- ✅ Use AI agent for calculations (no hardcoded logic)
- ✅ Only need MCP server for existing problem bank

---

## **Multi-Agent Architecture**

```
CoordinatorAgent (gemini-2.0-flash-exp)
│
├── SocraticTutor (gemini-2.0-flash-exp)
│   ├── Tool: problem_mcp (MCP Problem Server)
│   └── Sub-Agent: PhysicsCalculator
│
├── SolutionValidator (gemini-2.0-flash-exp)
│   └── Sub-Agent: PhysicsCalculator
│
└── PhysicsCalculator (gemini-2.0-flash-exp)
    └── Specialized calculation agent
```

---

## **Epic 1: Project Setup & Data Preparation**

### **Story 1.1: Environment Setup**
**Goal**: Configure development environment with Google ADK

**Tasks**:
- Install dependencies: `google-adk`, `google-genai`, `fastapi`, `uvicorn`, `mcp`
- Configure `.env` with `GOOGLE_API_KEY`
- Test Gemini API connection
- Document setup process

**Files**:
- `backend/requirements.txt` (create)
- `backend/.env.example` (create)
- `docs/SETUP.md` (create)

**Environment Variables**:
```
GOOGLE_API_KEY=<your_api_key>
PORT=8080
ENVIRONMENT=development
```

---

### **Story 1.2: Index Existing Problem Bank**
**Goal**: Create searchable index of existing problem JSON files

**Tasks**:
- Scan `backend/data/problems/` directory
- Parse all JSON problem files
- Create unified `problems_index.json`
- Analyze structure: topics, difficulties, problem counts
- Document problem data structure

**Input**: `backend/data/problems/*.json`  
**Output**: `backend/data/extracted/problems_index.json`

**Expected Index Structure**:
```json
{
  "total_problems": 150,
  "topics": {
    "kinematics": 45,
    "dynamics": 38,
    "energy": 32,
    "...": "..."
  },
  "difficulties": {
    "easy": 50,
    "medium": 70,
    "hard": 30
  },
  "problems": [
    {
      "id": "prob_001",
      "topic": "kinematics",
      "difficulty": "medium",
      "question": "...",
      "solution": "...",
      "hints": ["..."],
      "answer": "..."
    }
  ]
}
```

**Files**:
- `backend/scripts/index_problems.py` (create)
- `backend/data/extracted/problems_index.json` (generated)
- `docs/DATA_STRUCTURE.md` (create)

---

## **Epic 2: Multi-Agent System Implementation**

### **Story 2.1: Create Physics Calculator Agent**
**Goal**: AI agent that performs physics calculations with step-by-step work

**Agent Specification**:
- **Name**: PhysicsCalculator
- **Model**: gemini-2.0-flash-exp
- **Role**: Precise calculation specialist
- **Capabilities**: All physics calculations, shows work step-by-step
- **Tools**: None (pure LLM reasoning)
- **Sub-agents**: None

**Instruction Focus**:
- Identify correct formula
- Show all calculation steps
- Include units in every step
- Verify arithmetic accuracy
- Format: Formula → Given → Calculation → Final Answer

**Files**:
- `backend/agents/physics_calculator.py` (create)
- `tests/test_physics_calculator.py` (create)

---

### **Story 2.2: Create MCP Problem Server**
**Goal**: MCP server that serves problems from indexed database

**Server Specification**:
- **Name**: jee-problem-server
- **Protocol**: MCP (stdio transport)
- **Data Source**: `problems_index.json`

**Exposed Tools**:

1. **get_problem**
   - Description: Get specific problem by ID or all problems for topic
   - Parameters: `problem_id` (optional), `topic` (optional), `difficulty` (optional)
   - Returns: Problem details (question, hints, NOT solution initially)

2. **search_problems**
   - Description: Search problems by keywords
   - Parameters: `query` (required), `topic` (optional), `difficulty` (optional), `limit` (default 5)
   - Returns: List of matching problems

3. **get_random_problem**
   - Description: Get random practice problem
   - Parameters: `topic` (optional), `difficulty` (optional)
   - Returns: Single random problem

4. **list_topics**
   - Description: Get all available topics
   - Parameters: None
   - Returns: Topics with problem counts

**Files**:
- `backend/mcp_servers/problem_server.py` (create)
- `tests/test_mcp_server.py` (create)
- `docs/MCP_SERVER.md` (create)

**Testing**: Should be runnable standalone via `python -m backend.mcp_servers.problem_server`

---

### **Story 2.3: Create Socratic Tutor Agent**
**Goal**: Main teaching agent using Socratic method with MCP access

**Agent Specification**:
- **Name**: SocraticTutor
- **Model**: gemini-2.0-flash-exp
- **Role**: Expert JEE Physics tutor, guides via questions
- **Tools**: `problem_mcp` (MCP connection to problem server)
- **Sub-agents**: `PhysicsCalculator` (for delegating calculations)

**Instruction Focus**:
- NEVER give direct answers
- Ask probing questions
- Break problems into steps
- Use MCP tool to find practice problems
- Delegate calculations to PhysicsCalculator
- Patient and encouraging

**Key Behaviors**:
- Student asks for practice → Use MCP `search_problems` or `get_random_problem`
- Student needs calculation verified → Delegate to PhysicsCalculator
- Student stuck → Ask guiding questions, don't solve

**Files**:
- `backend/agents/socratic_tutor.py` (create)
- `tests/test_socratic_tutor.py` (create)

---

### **Story 2.4: Create Solution Validator Agent**
**Goal**: Agent that validates student solutions and provides feedback

**Agent Specification**:
- **Name**: SolutionValidator
- **Model**: gemini-2.0-flash-exp
- **Role**: Validates solutions, gives constructive feedback
- **Tools**: None
- **Sub-agents**: `PhysicsCalculator` (for verifying calculations)

**Instruction Focus**:
- Check approach/method first (conceptual)
- Verify calculations via PhysicsCalculator
- Identify specific errors
- Provide constructive feedback
- Acknowledge correct parts

**Key Behaviors**:
- Always validate approach before numbers
- Use PhysicsCalculator to verify numerical work
- Specific feedback, not just "wrong"
- Suggest how to fix errors

**Files**:
- `backend/agents/solution_validator.py` (create)
- `tests/test_solution_validator.py` (create)

---

### **Story 2.5: Create Coordinator Agent**
**Goal**: Top-level agent that routes requests to appropriate sub-agents

**Agent Specification**:
- **Name**: JEECoordinator
- **Model**: gemini-2.0-flash-exp
- **Role**: Routes student requests to correct specialist
- **Tools**: None
- **Sub-agents**: `SocraticTutor`, `SolutionValidator`

**Routing Logic**:
- "I need practice problems" → SocraticTutor
- "How do I solve this?" → SocraticTutor
- "Is my answer correct?" → SolutionValidator
- "Can you check my solution?" → SolutionValidator
- "Give me hints" → SocraticTutor

**Files**:
- `backend/agents/coordinator.py` (create)
- `backend/agents/factory.py` (create - initializes all agents)
- `tests/test_coordinator.py` (create)

---

### **Story 2.6: Create Sequential Learning Workflow (Optional)**
**Goal**: Structured workflow for problem-solving (bonus feature)

**Workflow Steps**:
1. **Understanding** → Help student understand problem
2. **Analysis** → Identify needed concepts/formulas
3. **Guidance** → Guide through solution (SocraticTutor)
4. **Validation** → Verify solution (SolutionValidator)

**Agent Specification**:
- **Name**: ProblemSolvingWorkflow
- **Type**: SequentialAgent
- **Sub-agents**: 4 step-specific agents

**Usage**: Optional, only when student explicitly requests structured guidance

**Files**:
- `backend/workflows/learning_workflow.py` (create)
- `tests/test_workflow.py` (create)

---

## **Epic 3: Sessions & Memory Management**

### **Story 3.1: Implement Session Service**
**Goal**: Track student conversations with context persistence

**Session Service**:
- Base: ADK's `InMemorySessionService`
- Wrapper: `JEESessionService` with student metadata
- Session lifetime: 1 hour of inactivity

**Session State Structure**:
```json
{
  "session_id": "student_123_1234567890",
  "student_id": "student_123",
  "created_at": "2024-11-24T10:00:00Z",
  "last_active": "2024-11-24T10:15:00Z",
  "state": {
    "current_topic": "kinematics",
    "current_problem_id": null,
    "interaction_count": 5,
    "hints_provided": 2,
    "tools_used": ["problem_mcp"],
    "conversation_history": []
  }
}
```

**Key Methods**:
- `create_student_session(student_id, topic)`
- `get_session(session_id)`
- `update_session(session_id, updates)`
- `cleanup_inactive_sessions()`

**Files**:
- `backend/services/session_service.py` (create)
- `tests/test_session_service.py` (create)

---

### **Story 3.2: Implement Memory Bank**
**Goal**: Store student learning profiles and history

**Memory Bank**:
- Type: Simple file-based JSON storage
- Storage location: `backend/data/memory/`
- Auto-save on updates

**Student Profile Structure**:
```json
{
  "student_id": "student_123",
  "created_at": "2024-11-01T00:00:00Z",
  "topic_mastery": {
    "kinematics": {
      "level": "intermediate",
      "problems_attempted": 15,
      "problems_correct": 10,
      "weak_areas": ["circular_motion"],
      "strong_areas": ["linear_motion"],
      "last_practiced": "2024-11-23"
    }
  },
  "session_history": [
    {
      "session_id": "sess_001",
      "date": "2024-11-20",
      "topic": "kinematics",
      "problems_attempted": 3,
      "hints_used": 2,
      "duration_minutes": 45
    }
  ],
  "preferences": {
    "difficulty_level": "medium",
    "learning_pace": "moderate"
  }
}
```

**Key Methods**:
- `store(key, value, metadata)`
- `retrieve(key)`
- `update(key, updates)`
- `create_student_profile(student_id)`
- `get_student_profile(student_id)`
- `update_session_history(student_id, session_data)`

**Files**:
- `backend/services/memory_bank.py` (create)
- `backend/data/memory/` (directory, gitignored)
- `tests/test_memory_bank.py` (create)

---

### **Story 3.3: Integrate Memory with Agents**
**Goal**: Load student history into agent context for personalization

**Integration Points**:

**Before Agent Execution**:
```python
# 1. Load student profile from memory
profile = memory_bank.get_student_profile(student_id)

# 2. Add to session state
session.state["student_profile"] = profile

# 3. Agent automatically has access via session context
```

**After Agent Execution**:
```python
# Update memory with session results
memory_bank.update_session_history(student_id, {
    "session_id": session.id,
    "date": now,
    "topic": session.state.get("current_topic"),
    "problems_attempted": X,
    "hints_used": Y,
    "duration_minutes": Z
})
```

**Agent Context Engineering**:
- Agents read `session.state["student_profile"]` automatically
- Use history to personalize: difficulty selection, hints, encouragement

**Files to Modify**:
- `backend/agents/coordinator.py`
- `backend/services/session_service.py`

---

## **Epic 4: Observability & Logging**

### **Story 4.1: Implement Structured Logging**
**Goal**: Comprehensive JSON-based logging for monitoring and debugging

**Logging Configuration**:
- Format: Structured JSON
- Log files: `app.log`, `agent.log`, `error.log`
- Rotation: Max 10MB per file, keep 5 backups
- Location: `backend/logs/` (gitignored)

**Log Entry Format**:
```json
{
  "timestamp": "2024-11-24T10:15:30.123Z",
  "level": "INFO",
  "logger": "JEEHelper.agents.coordinator",
  "message": "Agent interaction completed",
  "extra": {
    "session_id": "student_123_1234567890",
    "agent_name": "SocraticTutor",
    "student_id": "student_123",
    "duration_seconds": 2.345,
    "tools_used": ["problem_mcp"],
    "sub_agents_called": ["PhysicsCalculator"],
    "success": true
  }
}
```

**What to Log**:
- All agent interactions (start/end)
- All tool calls (parameters + results)
- All sub-agent delegations
- All errors with stack traces
- Session creation/retrieval
- Memory operations

**Files**:
- `backend/observability/logging_config.py` (create)
- `backend/observability/logger.py` (create)
- `backend/logs/` (directory, gitignored)

---

### **Story 4.2: Implement Metrics Collection**
**Goal**: Track system performance and usage statistics

**Metrics to Track**:
```json
{
  "timestamp": "2024-11-24T10:00:00Z",
  "window": "1_hour",
  "interactions": {
    "total": 1500,
    "successful": 1450,
    "failed": 50,
    "average_duration_seconds": 2.3
  },
  "agents": {
    "coordinator": 1500,
    "socratic_tutor": 1200,
    "solution_validator": 800,
    "physics_calculator": 950
  },
  "tools": {
    "problem_mcp": {
      "calls": 800,
      "get_problem": 300,
      "search_problems": 400,
      "get_random_problem": 100
    }
  },
  "sessions": {
    "active": 45,
    "created": 150,
    "total_duration_minutes": 6750
  },
  "topics": {
    "kinematics": 450,
    "dynamics": 380,
    "energy": 320
  }
}
```

**Key Methods**:
- `increment_counter(metric_name)`
- `record_duration(metric_name, duration)`
- `get_metrics()` → Returns current metrics
- `save_metrics()` → Persist to JSON every 100 interactions

**Persistence**: `backend/data/metrics/metrics.json`

**Files**:
- `backend/observability/metrics_collector.py` (create)
- `backend/data/metrics/` (directory)
- `tests/test_metrics.py` (create)

---

### **Story 4.3: Create Observability Wrapper**
**Goal**: Automatically wrap all agent executions with logging and metrics

**Wrapper Responsibilities**:
- Log interaction start (agent, session, student)
- Execute agent
- Measure duration
- Log interaction end (success/failure, tools used)
- Collect metrics
- Handle errors (log + re-raise)

**Usage Pattern**:
```python
with ObservabilityWrapper(agent_name, session_id) as obs:
    result = agent.execute(message)
    obs.record_tools_used(result.tools)
    obs.record_success()
```

**Files**:
- `backend/observability/wrapper.py` (create)
- `tests/test_observability.py` (create)

---

## **Epic 5: FastAPI Backend**

### **Story 5.1: Create FastAPI Application Structure**
**Goal**: REST API to expose multi-agent system

**FastAPI Configuration**:
- CORS: Allow all origins (for development)
- Docs: Auto-generated at `/docs` and `/redoc`
- Error handling: Global exception middleware
- Request validation: Pydantic models

**API Endpoints**:

1. **GET /**
   - Description: API information
   - Response: `{"name": "JEE-Helper API", "version": "1.0.0", "status": "running"}`

2. **GET /api/health**
   - Description: Health check
   - Response: `{"status": "healthy", "timestamp": "..."}`

3. **GET /api/topics**
   - Description: List available physics topics
   - Response: `{"topics": [{"name": "kinematics", "count": 45}, ...]}`

4. **POST /api/chat**
   - Description: Main chat endpoint (see Story 5.2)

5. **GET /api/session/{session_id}**
   - Description: Get session information
   - Response: Session state object

6. **GET /api/metrics**
   - Description: System metrics
   - Response: Current metrics object

7. **GET /api/student/{student_id}/profile**
   - Description: Get student profile
   - Response: Student profile object

**Files**:
- `backend/main.py` (create)
- `backend/api/__init__.py` (create)
- `backend/api/models.py` (create - Pydantic models)
- `backend/api/middleware.py` (create)
- `backend/api/routes/chat.py` (create)
- `backend/api/routes/topics.py` (create)
- `backend/api/routes/sessions.py` (create)
- `backend/api/routes/metrics.py` (create)

---

### **Story 5.2: Implement Chat Endpoint**
**Goal**: Main endpoint that processes student messages through multi-agent system

**Endpoint**: `POST /api/chat`

**Request Model**:
```json
{
  "student_id": "student_123",
  "message": "Can you give me a practice problem on kinematics?",
  "topic": "kinematics",
  "session_id": "student_123_1234567890"
}
```

**Request Fields**:
- `student_id` (required, string): Student identifier
- `message` (required, string): Student's message
- `topic` (optional, string): Current topic context
- `session_id` (optional, string): Existing session ID (creates new if omitted)

**Response Model**:
```json
{
  "session_id": "student_123_1234567890",
  "responses": [
    "Let me find you a good kinematics problem...",
    "Here's a problem on projectile motion: ..."
  ],
  "agent_used": "SocraticTutor",
  "tools_used": ["problem_mcp"],
  "sub_agents_called": [],
  "duration_seconds": 2.34,
  "success": true,
  "metadata": {
    "hints_provided_this_session": 2,
    "problems_attempted_this_session": 1
  }
}
```

**Error Response**:
```json
{
  "session_id": null,
  "responses": [],
  "success": false,
  "error": "Error message",
  "error_type": "validation_error|agent_error|system_error"
}
```

**Endpoint Logic Flow**:
1. Validate request
2. Create/retrieve session
3. Load student profile from memory
4. Add profile to session state
5. Wrap agent execution with observability
6. Execute coordinator agent with message
7. Extract responses, tools used, sub-agents called
8. Update session state
9. Update memory (session history)
10. Collect metrics
11. Return response

**HTTP Status Codes**:
- 200: Success
- 400: Invalid request
- 500: Server error

**Files**:
- `backend/api/routes/chat.py` (create)
- `backend/api/models.py` (update with ChatRequest/ChatResponse)
- `backend/api/dependencies.py` (create - dependency injection)

---

### **Story 5.3: Implement Dependency Injection**
**Goal**: Proper lifecycle management for agents, services, and connections

**Dependencies to Inject**:
- Coordinator agent (singleton)
- Session service (singleton)
- Memory bank (singleton)
- Metrics collector (singleton)
- Logger (singleton)

**Lifecycle Events**:
- **Startup**: Initialize agents, load memory, start MCP server
- **Shutdown**: Cleanup sessions, save metrics, stop MCP server

**Files**:
- `backend/api/dependencies.py` (create)
- `backend/api/startup.py` (create)
- `backend/main.py` (update with lifespan events)

---

## **Epic 6: Testing & Quality Assurance**

### **Story 6.1: Write Unit Tests**
**Goal**: Test individual components in isolation

**Test Coverage Areas**:

1. **Physics Calculator Agent**
   - Test various calculations
   - Verify step-by-step output
   - Test error handling

2. **MCP Problem Server**
   - Test each tool independently
   - Test search functionality
   - Test filtering (topic, difficulty)
   - Test random problem selection

3. **Session Service**
   - Test session creation
   - Test session retrieval
   - Test state updates
   - Test cleanup

4. **Memory Bank**
   - Test CRUD operations
   - Test profile creation
   - Test session history updates
   - Test file persistence

5. **Metrics Collector**
   - Test counter increments
   - Test duration recording
   - Test metrics retrieval
   - Test persistence

**Test Files**:
- `tests/conftest.py` (create - pytest fixtures)
- `tests/test_physics_calculator.py`
- `tests/test_mcp_server.py`
- `tests/test_session_service.py`
- `tests/test_memory_bank.py`
- `tests/test_metrics.py`
- `tests/fixtures/sample_problems.json` (create)

**Target**: >75% code coverage

---

### **Story 6.2: Write Integration Tests**
**Goal**: Test complete end-to-end flows

**Test Scenarios**:

1. **Complete Chat Flow**
   - Send message → Get response
   - Verify session creation
   - Verify memory update
   - Verify metrics recorded

2. **Multi-Agent Delegation**
   - Request problem → Verify SocraticTutor used
   - Request validation → Verify SolutionValidator used
   - Request calculation → Verify PhysicsCalculator delegated

3. **Session Persistence**
   - Create session
   - Send multiple messages
   - Verify state accumulates
   - Verify context maintained

4. **Memory Integration**
   - Create student profile
   - Complete sessions
   - Verify history updated
   - Verify profile retrieved in next session

5. **Error Scenarios**
   - Invalid student ID
   - Invalid message
   - Agent failure
   - MCP server unavailable

**Test Files**:
- `tests/test_integration.py` (create)
- `tests/test_api.py` (create)
- `tests/test_end_to_end.py` (create)

**Testing Approach**:
- Use FastAPI TestClient for API tests
- Mock external API calls (Gemini) for predictable tests
- Use real MCP server in integration tests
- Test with sample student profiles

---

### **Story 6.3: Create Testing Documentation**
**Goal**: Document testing approach and how to run tests

**Documentation Contents**:
- Testing philosophy
- How to run tests (`pytest`, `pytest --cov`)
- Test organization
- Writing new tests
- CI/CD integration (future)

**Files**:
- `docs/TESTING.md` (create)
- `pytest.ini` (create - pytest configuration)
- `.coveragerc` (create - coverage configuration)

---

## **Epic 7: Deployment to Google Cloud**

### **Story 7.1: Create Deployment Configuration**
**Goal**: Dockerize application for Cloud Run deployment

**Docker Configuration**:
- Base image: `python:3.10-slim`
- Multi-stage build (reduce size)
- Non-root user for security
- Health check endpoint
- Port: 8080 (Cloud Run requirement)

**Files to Create**:

1. **Dockerfile**
   - Install dependencies
   - Copy application code
   - Set environment variables
   - Expose port 8080
   - Run with uvicorn

2. **.dockerignore**
   - Exclude: tests, docs, logs, `__pycache__`, `.git`, `.env`

3. **cloudbuild.yaml**
   - Build Docker image
   - Tag with commit SHA
   - Push to Container Registry

4. **.gcloudignore**
   - Similar to .dockerignore for gcloud deployments

**Files**:
- `Dockerfile` (create)
- `.dockerignore` (create)
- `cloudbuild.yaml` (create)
- `.gcloudignore` (create)
- `docs/DEPLOYMENT.md` (create)

---

### **Story 7.2: Deploy to Google Cloud Run**
**Goal**: Deploy application to Cloud Run on free tier

**Deployment Steps**:

1. **Enable Required APIs**
   - Cloud Run API
   - Cloud Build API
   - Container Registry API

2. **Build Container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/jee-helper-adk
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy jee-helper \
     --image gcr.io/PROJECT_ID/jee-helper-adk \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --max-instances 10 \
     --set-env-vars GOOGLE_API_KEY=xxx
   ```

**Cloud Run Configuration**:
- Memory: 2GB
- CPU: 2 vCPU
- Max instances: 10 (auto-scaling)
- Region: us-central1
- Allow unauthenticated: Yes (for demo)
- Environment variables: `GOOGLE_API_KEY`

**Cost Estimate**:
- Within free tier (2M requests/month)
- Estimated: $0/month for MVP usage

**Verification**:
- Test health endpoint
- Test chat endpoint
- Monitor Cloud Logging

**Files**:
- `docs/DEPLOYMENT.md` (update with deployment URL)

---

### **Story 7.3: Setup Cloud Monitoring**
**Goal**: Configure monitoring and alerting on Google Cloud

**Monitoring Setup**:

1. **Cloud Logging Integration**
   - Application logs automatically captured
   - Filter by severity: ERROR, WARNING, INFO

2. **Create Log-based Metrics**
   - Request count
   - Error rate
   - Average response time
   - Agent usage distribution

3. **Setup Alerts**
   - Error rate > 5%
   - Response time > 10 seconds
   - Available memory < 20%

4. **Create Dashboard**
   - Requests per minute
   - Error rate
   - Response time (p50, p95, p99)
   - Active sessions

**Google Cloud Free Tier**:
- 50 GB logs ingestion/month (free)
- Basic monitoring (free)

**Files**:
- `docs/MONITORING.md` (create)

---

## **Epic 8: Frontend Integration**

### **Story 8.1: Update Frontend API Client**
**Goal**: Update React app to use new backend API

**API Client Updates**:

**Base Configuration**:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';
```

**API Methods to Implement**:
1. `sendMessage(studentId, message, topic, sessionId)`
2. `getTopics()`
3. `getSession(sessionId)`
4. `getStudentProfile(studentId)`

**Error Handling**:
- Network errors
- API errors (4xx, 5xx)
- Timeout handling
- Retry logic (optional)

**Files to Modify**:
- `frontend/src/api/client.js`
- `frontend/.env.example` (add `REACT_APP_API_URL`)

---

### **Story 8.2: Update Chat Component**
**Goal**: Integrate new API and display enhanced features

**Component Updates**:

**State Management**:
- `messages` (conversation history)
- `sessionId` (current session)
- `loading` (API call in progress)
- `error` (error message)
- `currentTopic` (selected topic)

**Features to Implement**:
1. Display conversation history
2. Show loading indicator during API calls
3. Display error messages gracefully
4. Show tools used (optional, badge)
5. Topic selector dropdown
6. Session persistence (localStorage)

**UI Enhancements**:
- Different styling for student vs agent messages
- Timestamp on messages
- "Tools used" badges (MCP, Calculator)
- Typing indicator

**Files to Modify**:
- `frontend/src/components/Chat.jsx`
- `frontend/src/components/Message.jsx` (create)
- `frontend/src/components/TopicSelector.jsx` (create)

---

### **Story 8.3: Add Topic Selection**
**Goal**: Allow students to select physics topic before chatting

**Implementation**:
- Fetch topics from `/api/topics` on component mount
- Display dropdown/buttons for topic selection
- Send selected topic with each message
- Display current topic in UI

**Files to Modify**:
- `frontend/src/components/TopicSelector.jsx`
- `frontend/src/components/Chat.jsx`

---

## **Epic 9: Documentation & Final Polish**

### **Story 9.1: Create Comprehensive Documentation**
**Goal**: Complete project documentation for submission

**Documentation Files**:

1. **README.md**
   - Project overview
   - Features
   - Multi-agent architecture diagram
   - Setup instructions
   - API documentation
   - Deployment guide
   - Screenshots

2. **ARCHITECTURE.md**
   - System design overview
   - Multi-agent hierarchy diagram
   - Data flow diagrams
   - Technology stack details
   - Design decisions and rationale

3. **API.md**
   - All endpoint specifications
   - Request/response examples
   - Error codes
   - Authentication (future)

4. **FEATURES_COMPLIANCE.md**
   - Feature 1: Multi-Agent System ✅
   - Feature 2: Tools (MCP) ✅
   - Feature 3: Sessions & Memory ✅
   - Feature 4: Observability ✅
   - Code references for each feature
   - Screenshots/diagrams

5. **MCP_SERVER.md**
   - MCP server specification
   - Available tools
   - How to run standalone
   - Testing guide

**Files**:
- `README.md` (update)
- `docs/ARCHITECTURE.md` (create)
- `docs/API.md` (create)
- `docs/FEATURES_COMPLIANCE.md` (create)
- `docs/MCP_SERVER.md` (already created)

---

### **Story 9.2: Create Demo Script**
**Goal**: Standalone script demonstrating multi-agent capabilities

**Demo Scenarios**:

1. **Practice Problem Request**
   - Student: "Give me a kinematics problem"
   - Shows: Coordinator → SocraticTutor → MCP tool usage

2. **Calculation Verification**
   - Student: "Calculate force when m=5kg, a=10m/s²"
   - Shows: Coordinator → SocraticTutor → PhysicsCalculator delegation

3. **Solution Validation**
   - Student: "Is F=50N correct for m=5kg, a=10m/s²?"
   - Shows: Coordinator → SolutionValidator → PhysicsCalculator

4. **Session Persistence**
   - Multiple messages in same session
   - Shows: Context maintained, hints counted

5. **Memory Integration**
   - Shows: Student profile loaded, personalized responses

**Demo Output**:
- Pretty-printed conversation
- Shows agent delegation
- Shows tool usage
- Shows session state
- Shows metrics

**Files**:
- `demo/demo_script.py` (create)
- `demo/README.md` (create)
- `demo/sample_conversations.md` (create)

---

### **Story 9.3: Create Submission Package**
**Goal**: Prepare everything for course submission

**Submission Checklist**:

✅ **Code Quality**
- All code committed to GitHub
- No secrets in repository
- Clean commit history
- .gitignore properly configured

✅ **Documentation**
- README with clear setup instructions
- Architecture documentation
- API documentation
- Features compliance document

✅ **Deployment**
- Deployed to Cloud Run
- Public URL accessible
- Health check working
- Sample requests tested

✅ **Demonstration**
- Demo script works
- Video demo (optional, 3-5 min)
- Screenshots of key features

✅ **Features Evidence**
- Multi-Agent System: Code + diagram
- MCP Tools: MCP server code + usage
- Sessions & Memory: Code + examples
- Observability: Logs + metrics + screenshots

**Files**:
- `SUBMISSION.md` (create - submission checklist)
- `docs/FEATURES_COMPLIANCE.md` (complete)
- `demo/` (complete)

---

## **Project Structure Overview**

```
JEE-Helper/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coordinator.py          # Coordinator agent
│   │   ├── socratic_tutor.py       # Socratic tutor agent
│   │   ├── solution_validator.py   # Solution validator agent
│   │   ├── physics_calculator.py   # Physics calculator agent
│   │   └── factory.py              # Agent initialization
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py               # Pydantic models
│   │   ├── middleware.py           # Error handling
│   │   ├── dependencies.py         # DI setup
│   │   ├── startup.py              # Lifecycle events
│   │   └── routes/
│   │       ├── chat.py             # Chat endpoint
│   │       ├── topics.py           # Topics endpoint
│   │       ├── sessions.py         # Sessions endpoint
│   │       └── metrics.py          # Metrics endpoint
│   │
│   ├── data/
│   │   ├── extracted/
│   │   │   └── problems_index.json # Generated index
│   │   ├── memory/                 # Student profiles (gitignored)
│   │   ├── metrics/                # Metrics data
│   │   ├── problems/               # Original problems (from repo)
│   │   └── textbooks/              # Original textbooks (from repo)
│   │
│   ├── logs/                       # Application logs (gitignored)
│   │   ├── app.log
│   │   ├── agent.log
│   │   └── error.log
│   │
│   ├── mcp_servers/
│   │   ├── __init__.py
│   │   └── problem_server.py       # MCP problem server
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging_config.py       # Logging setup
│   │   ├── logger.py               # Logger wrapper
│   │   ├── metrics_collector.py   # Metrics collection
│   │   └── wrapper.py              # Observability wrapper
│   │
│   ├── scripts/
│   │   └── index_problems.py       # Problem indexing script
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py      # Session management
│   │   └── memory_bank.py          # Memory service
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── learning_workflow.py    # Sequential workflow
│   │
│   ├── main.py                     # FastAPI app
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js           # API client
│   │   ├── components/
│   │   │   ├── Chat.jsx            # Main chat component
│   │   │   ├── Message.jsx         # Message component
│   │   │   └── TopicSelector.jsx   # Topic selector
│   │   └── App.jsx
│   └── .env.example                # Frontend env template
│
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_physics_calculator.py
│   ├── test_mcp_server.py
│   ├── test_session_service.py
│   ├── test_memory_bank.py
│   ├── test_metrics.py
│   ├── test_observability.py
│   ├── test_agents.py
│   ├── test_integration.py
│   ├── test_api.py
│   └── fixtures/
│       └── sample_problems.json
│
├── demo/
│   ├── demo_script.py              # Demo script
│   ├── README.md                   # Demo instructions
│   └── sample_conversations.md     # Sample outputs
│
├── docs/
│   ├── SETUP.md                    # Setup guide
│   ├── DATA_STRUCTURE.md           # Data format docs
│   ├── ARCHITECTURE.md             # System architecture
│   ├── API.md                      # API documentation
│   ├── FEATURES_COMPLIANCE.md      # Feature checklist
│   ├── MCP_SERVER.md               # MCP server docs
│   ├── TESTING.md                  # Testing guide
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── MONITORING.md               # Monitoring setup
│
├── Dockerfile                      # Docker configuration
├── .dockerignore
├── cloudbuild.yaml                 # Cloud Build config
├── .gcloudignore
├── pytest.ini                      # Pytest config
├── .coveragerc                     # Coverage config
├── .gitignore
├── README.md                       # Main project README
└── SUBMISSION.md                   # Submission checklist
```

---

## **Feature Compliance Summary**

| Feature | Components | Status |
|---------|-----------|--------|
| **1. Multi-Agent System** | Coordinator + 3 specialist agents (SocraticTutor, SolutionValidator, PhysicsCalculator) + Optional Sequential Workflow | ✅ |
| **2. Tools** | MCP Problem Server (4 tools: get_problem, search_problems, get_random_problem, list_topics) | ✅ |
| **3. Sessions & Memory** | InMemorySessionService + SimpleMemoryBank with student profiles | ✅ |
| **4. Observability** | Structured logging (3 files) + Metrics collection + ObservabilityWrapper | ✅ |

**Total: 4 Features Implemented ✅**  
*Exceeds minimum requirement of 3 features*

---

## **Implementation Timeline**

### **Week 1: Core Foundation**
- ✅ Epic 1: Setup + Problem Indexing (1 day)
- ✅ Epic 2: Multi-Agent System (4 days)
  - Physics Calculator Agent
  - MCP Problem Server
  - Socratic Tutor
  - Solution Validator
  - Coordinator
- ✅ Initial testing

### **Week 2: Infrastructure**
- ✅ Epic 3: Sessions & Memory (2 days)
- ✅ Epic 4: Observability (2 days)
- ✅ Epic 5: FastAPI Backend (2 days)
- ✅ Integration testing (1 day)

### **Week 3: Testing & Deployment**
- ✅ Epic 6: Testing (2 days)
- ✅ Epic 7: Deployment (2 days)
- ✅ Epic 8: Frontend Integration (1 day)
- ✅ Epic 9: Documentation (2 days)

**Total Duration: 3 weeks**

---

## **Key Simplifications from Original Plan**

1. ✅ **No PDF extraction** - Gemini has physics knowledge
2. ✅ **No formula database creation** - Gemini knows formulas
3. ✅ **AI-powered calculator** - No hardcoded calculation logic
4. ✅ **Simple file-based memory** - No database needed
5. ✅ **In-memory sessions** - Sufficient for MVP
6. ✅ **Only index existing problems** - No new problem creation

**Result**: Focus on multi-agent architecture and ADK features! 🎯