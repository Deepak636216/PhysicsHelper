# JEE-Helper: Multi-Agent Physics Tutor

AI-powered physics tutoring system for JEE preparation using Google ADK multi-agent architecture.

## Overview

JEE-Helper is an intelligent physics tutor that uses multiple specialized AI agents to provide Socratic teaching, problem-solving guidance, and personalized learning experiences for JEE (Joint Entrance Examination) students.

### Key Features

- **Multi-Agent Architecture**: Coordinator, SocraticTutor, SolutionValidator, and PhysicsCalculator agents
- **MCP Tools**: Problem bank access via Model Context Protocol
- **Sessions & Memory**: Track student progress and personalize learning
- **Observability**: Comprehensive logging and metrics

## Technology Stack

- **AI**: Google Gemini 2.0 Flash (via Google ADK)
- **Backend**: FastAPI + Python 3.10+
- **Frontend**: React
- **Deployment**: Google Cloud Run (Free Tier)
- **Protocol**: MCP (Model Context Protocol)

## Project Status

**Current Sprint**: Foundation Complete ✅

- ✅ Backend structure and dependencies
- ✅ Problem bank indexing system
- ✅ PhysicsCalculator agent implementation
- ✅ MCP Problem Server with 4 tools
- ⏳ Remaining agents (SocraticTutor, SolutionValidator, Coordinator)
- ⏳ Sessions & Memory services
- ⏳ FastAPI backend
- ⏳ Deployment setup

See [PROGRESS.md](docs/PROGRESS.md) for detailed status.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Google AI API Key ([Get one here](https://aistudio.google.com/))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Deepak636216/JEE-Helper.git
cd JEE-Helper

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp backend/.env.example backend/.env
# Edit .env and add your GOOGLE_API_KEY

# 4. Test setup
cd backend
python test_gemini_connection.py
```

Expected output:
```
✅ GOOGLE_API_KEY found
✅ Genai client initialized successfully
✅ API call successful!
✅ All checks passed! You're ready to proceed.
```

## What's Built So Far

### 1. Problem Bank System

Index and search physics problems by topic and difficulty:

```bash
# Create/update problem index
cd backend
python scripts/index_problems.py

# Test problem tools
python mcp_servers/problem_tools.py
```

**Available Topics**: Kinematics, Dynamics, Energy, and more

### 2. PhysicsCalculator Agent

AI agent that performs precise physics calculations with step-by-step work:

```python
from agents.physics_calculator import create_physics_calculator

calculator = create_physics_calculator(api_key)
result = calculator.calculate("Calculate force when m=5kg, a=10m/s²")
print(result)
```

Output:
```
**Formula**: F = ma
**Given**: m = 5 kg, a = 10 m/s²
**Calculation**: F = (5 kg) × (10 m/s²) = 50 N
**Final Answer**: F = 50 N
```

### 3. MCP Problem Server

Four tools for accessing the problem bank:

- `get_problem` - Get specific problem by ID or filters
- `search_problems` - Search by keywords
- `get_random_problem` - Random practice problem
- `list_topics` - Available topics and statistics

```bash
# Test all tools
cd backend
python mcp_servers/problem_tools.py
```

## Project Structure

```
JEE-Helper/
├── backend/
│   ├── agents/              # AI agents
│   │   └── physics_calculator.py
│   ├── data/
│   │   ├── problems/        # Problem bank JSON files
│   │   └── extracted/       # Generated index
│   ├── mcp_servers/         # MCP tools
│   │   ├── problem_server.py
│   │   └── problem_tools.py
│   ├── scripts/
│   │   └── index_problems.py
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── SETUP.md            # Setup instructions
│   └── PROGRESS.md         # Development progress
├── US.md                   # User stories & specs
└── README.md
```

## Multi-Agent Architecture

```
CoordinatorAgent
│
├── SocraticTutor (with MCP tools)
│   ├── Tool: problem_mcp
│   └── Sub-Agent: PhysicsCalculator ✅
│
├── SolutionValidator
│   └── Sub-Agent: PhysicsCalculator ✅
│
└── PhysicsCalculator ✅
    └── Specialized calculations
```

Legend: ✅ = Implemented, ⏳ = In Progress

## Development Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] Project setup and structure
- [x] Problem bank indexing
- [x] PhysicsCalculator agent
- [x] MCP Problem Server

### Phase 2: Multi-Agent System (In Progress)
- [ ] SocraticTutor agent
- [ ] SolutionValidator agent
- [ ] Coordinator agent
- [ ] Agent integration tests

### Phase 3: Infrastructure
- [ ] Session management
- [ ] Memory bank (student profiles)
- [ ] Observability (logging + metrics)

### Phase 4: Backend API
- [ ] FastAPI endpoints
- [ ] Chat interface
- [ ] Session persistence

### Phase 5: Deployment
- [ ] Docker configuration
- [ ] Google Cloud Run deployment
- [ ] Monitoring setup

### Phase 6: Frontend
- [ ] React chat interface
- [ ] Topic selection
- [ ] Session management UI

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Progress Report](docs/PROGRESS.md) - Development status and metrics
- [User Stories](US.md) - Complete feature specifications
- Architecture Docs (Coming soon)
- API Documentation (Coming soon)

## Testing

All implemented components include tests:

```bash
cd backend

# Test problem indexing
python scripts/index_problems.py

# Test problem tools
python mcp_servers/problem_tools.py

# Test physics calculator (requires API key)
python agents/physics_calculator.py
```

## Contributing

This is a course project. Contributions welcome after initial submission.

## License

MIT License (to be added)

## Repository

https://github.com/Deepak636216/JEE-Helper

## Contact

For questions about the project, see the GitHub repository.

---

**Last Updated**: November 24, 2025
**Status**: Foundation Complete - Ready for Agent Development
**Next Milestone**: Complete Multi-Agent System
