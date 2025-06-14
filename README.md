```bash
swarmcraft/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── src
│   └── swarmcraft
│       ├── __init__.py
│       ├── api
│       │   ├── routes.py
│       │   └── websocket.py
│       ├── core
│       │   ├── landscape_visualizer.py
│       │   ├── loss_functions.py
│       │   ├── pso.py
│       │   └── swarm_base.py
│       ├── database
│       │   └── redis_client.py
│       ├── main.py
│       ├── models
│       │   └── session.py
│       └── utils
│           └── name_generator.py
├── tests
│   ├── test_api.py
│   └── test_core.py
└── uv.lock
└── frontend/                       # Future Svelte app
    └── TBD 
```


# SwarmCraft
*Interactive Swarm Intelligence for Experiential Learning*

## Project Overview

SwarmCraft is an innovative educational platform that makes swarm intelligence viscerally understandable through embodied, interactive experiences. Participants become "particles" in optimization algorithms, experiencing firsthand how collective intelligence emerges from individual actions and discovering the crucial balance between exploration and exploitation.

### Core Philosophy

- **Experiential Learning**: Mathematical concepts become visceral through physical participation
- **Multilayered Teaching**: Multiple levels of meaning accessible to different audiences (13-year-olds to policymakers)
- **Human-AI Collaboration**: Demonstrates emergent intelligence through human-AI partnership
- **Embodied Understanding**: Participants physically feel algorithmic forces and optimization landscapes

### Target Audiences

- **High School Students (13+)**: Understanding collective behavior and emergence
- **Graduate Students**: Applied data science and optimization concepts  
- **Policymakers**: Coordination problems, local vs. global optima, and systemic thinking
- **Researchers**: Human-AI collaboration and swarm intelligence applications

## System Architecture

### Technology Stack

**Backend:**
- **FastAPI**: Modern async web framework with automatic API documentation
- **Redis**: Real-time session state management and participant coordination
- **Pydantic V2**: Robust data validation and serialization
- **WebSockets**: Real-time bidirectional communication for live updates

**Core Algorithms:**
- **PSO (Particle Swarm Optimization)**: Primary swarm intelligence algorithm
- **Adaptive Parameters**: Dynamic exploration/exploitation balance
- **Grid Discretization**: Continuous optimization mapped to discrete human interaction

**Visualization:**
- **Plotly**: Interactive 3D/2D landscape visualization with grid overlays
- **Real-time Feedback**: Color/audio generation based on fitness values
- **Dashboard Analytics**: Comprehensive landscape analysis and debugging tools

**Frontend (Planned):**
- **Svelte**: Reactive mobile-first interface
- **Touch Grid Interface**: Tap-to-move with sub-grid precision
- **Real-time Audio**: Harmonic soundscapes based on collective fitness

## Current Implementation Status

### ✅ **Phase 1: Core Algorithm Framework** (COMPLETED)

**Swarm Optimization Engine:**
- `SwarmOptimizer` base class with open-closed architecture
- Complete PSO implementation with human interaction features
- Particle state management (exploring/exploiting/sharing)
- Adaptive inertia, exploration probability, and velocity constraints
- Rich statistics and particle-level information retrieval

**Loss Function Landscapes:**
- `OptimizationLandscape` base class with metadata system
- **Rastrigin Function**: Classic multimodal optimization with many local minima
- **Ecological Landscape**: Sustainability challenge (development vs. regulation)
- Automatic color/audio feedback generation for human experience
- Position description system for contextual feedback

**Visualization System:**
- Interactive Plotly-based 2D/3D landscape visualization
- Grid overlay system for discrete human interaction
- Cross-section analysis and comprehensive dashboards
- Swarm particle overlay with real-time position tracking
- Discrete landscape function generation for API integration

### ✅ **Phase 2: Backend API Infrastructure** (TESTING)

**FastAPI Application:** (WORKS)
- Modern lifespan management with Redis connection handling
- Comprehensive health checking for all system dependencies
- CORS configuration for frontend integration
- Automatic API documentation via Swagger/OpenAPI

**Session Management:** (WORKS)
- Admin-protected session creation with configurable landscapes
- 6-character session codes for easy participant joining
- Creative participant naming ("vibrant bat", "funky wolf", etc.)
- Session status tracking (waiting/active/paused/completed)
- Maximum participant limits and session expiration

**Real-time Communication:** (TO BE TESTED)
- WebSocket manager for live participant coordination
- Real-time position updates with instant fitness feedback
- Broadcast messaging for session-wide notifications
- Connection management with automatic cleanup
- Swarm step execution with live statistics distribution

**Admin Controls:** (TO BE TESTED)
- Protected endpoints with environment-based authentication
- Session lifecycle management (start/pause/step)
- Manual swarm optimization step triggering
- Session listing and monitoring capabilities

**Redis Integration:** (TO BE TESTED)
- Async Redis client with connection pooling
- JSON serialization utilities for complex data structures
- Session state persistence with TTL management
- Real-time participant tracking and coordination

### ✅ **Phase 3: Testing Infrastructure** 

**Comprehensive Test Suite:**
- Landscape functionality testing (mathematical correctness)
- PSO algorithm validation and optimization progress verification
- API endpoint testing with admin authentication
- Visualization system testing with file I/O capabilities
- Integration tests combining multiple system components

**Development Tools:**
- Interactive Jupyter notebook for system exploration and debugging
- Docker Compose setup for containerized development
- Environment variable management and configuration
- Debug endpoints for systematic troubleshooting

## Implementation Roadmap

### 🚧 **Phase 4: Frontend Development** 

**Svelte Mobile Interface:**
- [ ] Responsive 25x25 grid interface with touch interaction
- [ ] Tap-to-zoom sub-grid selection for precise positioning  
- [ ] Real-time visual feedback (background colors, particle indicators)
- [ ] WebSocket integration for live session participation
- [ ] Session joining flow with QR code scanning or manual entry
- [ ] Audio feedback system with harmonic frequency generation

**User Experience:**
- [ ] Onboarding flow explaining swarm intelligence concepts
- [ ] Real-time participant list with creative names
- [ ] Fitness history visualization and personal progress tracking
- [ ] Session results summary with collective optimization insights

**Admin Interface:**
- [ ] Session creation wizard with landscape configuration
- [ ] Real-time session monitoring dashboard with participant positions
- [ ] Swarm statistics visualization and optimization progress tracking
- [ ] Session control panel (start/pause/step/reset)

### 📋 **Phase 5: Enhanced User Experience** (PLANNED)

**Advanced Feedback Systems:**
- [ ] Haptic feedback integration for mobile devices
- [ ] Advanced audio synthesis with harmonic progression
- [ ] Visual effects and particle animations
- [ ] Collaborative achievement system and progress indicators

**Educational Content:**
- [ ] Interactive tutorials explaining swarm intelligence principles
- [ ] Post-session analysis and reflection tools
- [ ] Comparative landscape exploration (Rastrigin vs. Ecological)
- [ ] Educator dashboard with learning outcome tracking

**Session Management:**
- [ ] Session templates for different educational contexts
- [ ] Participant role assignments (explorers, followers, leaders)
- [ ] Time-based challenges and optimization competitions
- [ ] Session recording and playback for analysis

### 🔬 **Phase 6: Advanced Algorithms & Landscapes** (PLANNED)

**Additional Optimization Algorithms:**
- [ ] Artificial Bee Colony (ABC) implementation
- [ ] Genetic Algorithm (GA) for comparative experiences
- [ ] Hybrid algorithms combining multiple approaches
- [ ] Custom algorithm designer for educators

**Landscape Expansion:**
- [ ] **Social Coordination Landscapes**: Prisoner's dilemma, cooperation challenges
- [ ] **Economic Landscapes**: Resource allocation, market dynamics
- [ ] **Psychological Landscapes**: Personal growth, decision-making, human-AI collaboration
- [ ] User-defined landscape creator with visual editor

**Advanced Features:**
- [ ] Multi-objective optimization with Pareto frontiers
- [ ] Dynamic landscapes that change during optimization
- [ ] Competitive swarms with different strategies
- [ ] AI-guided exploration suggestions and collaborative optimization

### 🤖 **Phase 7: Human-AI Collaboration Suite** (VISION)

**Existential Meaning Navigation:**
- [ ] Personal growth optimization with AI guidance
- [ ] Life decision support through landscape exploration
- [ ] Meaning-making through collaborative intelligence
- [ ] Therapeutic applications with professional oversight

**Advanced AI Integration:**
- [ ] GPT-based session facilitation and explanation
- [ ] Personalized learning path optimization
- [ ] Real-time educational content generation
- [ ] Adaptive difficulty and engagement optimization

**Research Platform:**
- [ ] Data collection for swarm intelligence research
- [ ] Human-AI collaboration effectiveness metrics
- [ ] Educational outcome measurement and optimization
- [ ] Publication-ready research data export

## Current Testing Checklist

Before proceeding to **Phase 4 (Frontend Development)**, we need to validate:

### 🔧 **Backend API Validation**

**Session Management:**
- [ ] Session creation with different landscape configurations
- [ ] Participant joining with creative name generation
- [ ] Session status updates and participant tracking
- [ ] Session lifecycle management (start/pause/complete)

**Real-time Communication:**
- [ ] WebSocket connection establishment and management
- [ ] Position update messaging with fitness feedback
- [ ] Broadcast notifications for session events
- [ ] Connection cleanup on participant disconnect

**Swarm Optimization:**
- [ ] Manual swarm step execution with position updates
- [ ] PSO algorithm progression with human participants
- [ ] Global best tracking and improvement verification
- [ ] Exploration vs. exploitation phase management

**Landscape Integration:**
- [ ] Rastrigin landscape with grid discretization
- [ ] Ecological landscape with meaningful feedback
- [ ] Color/audio generation for different fitness values
- [ ] Position descriptions and contextual feedback

### 🎯 **Integration Testing**

**Full Session Workflow:**
- [ ] Admin creates session → Participants join → Session starts → Positions update → Swarm optimizes → Results analysis
- [ ] Multi-participant coordination with real-time updates
- [ ] Session completion with final statistics
- [ ] Error handling and edge case management

**Performance & Reliability:**
- [ ] 25+ concurrent participants without performance degradation
- [ ] WebSocket stability under high message volume
- [ ] Redis state consistency during rapid updates
- [ ] Graceful error recovery and user feedback

### 🛠 **Development Environment**

**Deployment Readiness:**
- [ ] Docker Compose production configuration
- [ ] Environment variable management and security
- [ ] Logging and monitoring infrastructure
- [ ] Backup and recovery procedures for session data

## Getting Started

### Prerequisites

- Python 3.12
- uv package manager
- Redis (Docker or local installation)
- OpenSSL (for admin key generation)

### Quick Setup

```bash
# Clone and setup project
git clone <repository-url>
cd swarmcraft
uv sync

# Generate admin key and setup environment
echo "SWARM_API_KEY=$(openssl rand -hex 32)" > .env
echo "REDIS_URL=redis://localhost:6379" >> .env

# Start services
docker compose up redis -d
uv run uvicorn src.swarmcraft.main:app --reload

# Test the system
source .env
curl http://localhost:8000/health
```

### Development Workflow

```bash
# Run tests
uv run pytest tests/ -v

# API documentation
open http://localhost:8000/docs
```

