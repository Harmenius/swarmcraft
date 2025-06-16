# SwarmCraft
*Interactive Swarm Intelligence for Experiential Learning*

## Project Overview

SwarmCraft is an innovative educational platform that makes swarm intelligence viscerally understandable through embodied, interactive experiences. Participants become "particles" in optimization algorithms, experiencing firsthand how collective intelligence emerges from individual actions and discovering the crucial balance between exploration and exploitation.

### Core Philosophy

- **Experiential Learning**: Mathematical concepts become visceral through physical participation.
- **Multilayered Teaching**: Multiple levels of meaning accessible to different audiences (13-year-olds to policymakers).
- **Human-AI Collaboration**: Demonstrates emergent intelligence through human-AI partnership.
- **Embodied Understanding**: Participants physically feel algorithmic forces and optimization landscapes.

### Target Audiences

- **High School Students (13+)**: Understanding collective behavior and emergence.
- **Graduate Students**: Applied data science and optimization concepts.
- **Policymakers**: Coordination problems, local vs. global optima, and systemic thinking.
- **Researchers**: Human-AI collaboration and swarm intelligence applications.

## System Architecture

### Technology Stack

**Backend:**
- **FastAPI**: Modern async web framework with automatic API documentation.
- **Redis**: Real-time session state management and participant coordination.
- **Pydantic V2**: Robust data validation and serialization.
- **WebSockets**: Real-time bidirectional communication for live updates.

**Core Algorithms:**
- **PSO (Particle Swarm Optimization)**: Primary swarm intelligence algorithm.
- **Adaptive Parameters**: Dynamic exploration/exploitation balance.
- **Grid Discretization**: Continuous optimization mapped to discrete human interaction.

**Visualization:**
- **Plotly**: Interactive 3D/2D landscape visualization with grid overlays.
- **Real-time Feedback**: Color/audio generation based on fitness values.
- **Dashboard Analytics**: Comprehensive landscape analysis and debugging tools.

**Frontend (Planned):**
- **Svelte**: Reactive mobile-first interface.
- **Touch Grid Interface**: Tap-to-move with sub-grid precision.
- **Real-time Audio**: Harmonic soundscapes based on collective fitness.

## Current Implementation Status

### ✅ **Phase 1: Core Algorithm Framework** (COMPLETED)

The underlying swarm intelligence engine and visualization tools are complete and tested. This includes the `SwarmOptimizer` base class, a full-featured `PSO` implementation, and multiple `OptimizationLandscape` options like Rastrigin and the Ecological Challenge.

### ✅ **Phase 2: Backend API Infrastructure** (COMPLETED)

The FastAPI application is fully functional. This includes robust, stateful session management using Redis, admin-protected endpoints for controlling the simulation (create, start, step, list, close), and real-time WebSocket communication for pushing updates to clients.

### ✅ **Phase 3: End-to-End Testing & Validation** (COMPLETED)

The system has been validated from end to end. The `test_core.py` and `test_api.py` suites ensure backend correctness. A minimal HTML/JS test client has been used to verify the full application loop, from session creation to real-time participant updates on the grid.

## Implementation Roadmap

### 🔬 **Phase 4: Algorithm Tuning & Refinement** (IN PROGRESS)

Based on testing with the minimal client, the next step is to fine-tune the algorithm's behavior to create a better user experience before building the full frontend.
- [ ] **Create a smooth loss surface**: Implement a simple, convex loss function (e.g., a quadratic bowl) to test basic convergence without the complexity of local minima.
- [ ] **Tune for Fast Convergence**: Find a mix of PSO parameters and landscape settings that allow the swarm to reliably converge in ~5-10 steps. This is ideal for quick testing and live demonstrations.
- [ ] **Develop a Jupyter Notebook testing suite**: Use the existing notebook to interactively tweak landscape and PSO parameters and visualize the results immediately to find the optimal settings.
- [ ] **Validate in a Browser**: Port the "fast convergence" settings back to the `index.html` test client to ensure the experience is smooth and visually understandable.

### 🚧 **Phase 5: Frontend Development** (PLANNED)

**Svelte Mobile Interface:**
- [ ] Responsive 25x25 grid interface with touch interaction.
- [ ] Tap-to-zoom sub-grid selection for precise positioning.
- [ ] Real-time visual feedback (background colors, particle indicators).
- [ ] WebSocket integration for live session participation.
- [ ] Session joining flow with QR code scanning or manual entry.
- [ ] Audio feedback system with harmonic frequency generation.

**User Experience:**
- [ ] Onboarding flow explaining swarm intelligence concepts.
- [ ] Real-time participant list with creative names.
- [ ] Fitness history visualization and personal progress tracking.
- [ ] Session results summary with collective optimization insights.

**Admin Interface:**
- [ ] Session creation wizard with landscape configuration.
- [ ] Real-time session monitoring dashboard with participant positions.
- [ ] Swarm statistics visualization and optimization progress tracking.
- [ ] Session control panel (start/pause/step/reset).

### 📋 **Phase 6: Enhanced User Experience** (PLANNED)

**Advanced Feedback Systems:**
- [ ] Haptic feedback integration for mobile devices.
- [ ] Advanced audio synthesis with harmonic progression.
- [ ] Visual effects and particle animations.
- [ ] Collaborative achievement system and progress indicators.

**Educational Content:**
- [ ] Interactive tutorials explaining swarm intelligence principles.
- [ ] Post-session analysis and reflection tools.
- [ ] Comparative landscape exploration (Rastrigin vs. Ecological).
- [ ] Educator dashboard with learning outcome tracking.

**Session Management:**
- [ ] Session templates for different educational contexts.
- [ ] Participant role assignments (explorers, followers, leaders).
- [ ] Time-based challenges and optimization competitions.
- [ ] Session recording and playback for analysis.

### 🔬 **Phase 7: Advanced Algorithms & Landscapes** (PLANNED)

**Additional Optimization Algorithms:**
- [ ] Artificial Bee Colony (ABC) implementation.
- [ ] Genetic Algorithm (GA) for comparative experiences.
- [ ] Hybrid algorithms combining multiple approaches.
- [ ] Custom algorithm designer for educators.

**Landscape Expansion:**
- [ ] **Social Coordination Landscapes**: Prisoner's dilemma, cooperation challenges.
- [ ] **Economic Landscapes**: Resource allocation, market dynamics.
- [ ] **Psychological Landscapes**: Personal growth, decision-making, human-AI collaboration.
- [ ] User-defined landscape creator with visual editor.

**Advanced Features:**
- [ ] Multi-objective optimization with Pareto frontiers.
- [ ] Dynamic landscapes that change during optimization.
- [ ] Competitive swarms with different strategies.
- [ ] AI-guided exploration suggestions and collaborative optimization.

### 🤖 **Phase 8: Human-AI Collaboration Suite** (VISION)

**Existential Meaning Navigation:**
- [ ] Personal growth optimization with AI guidance.
- [ ] Life decision support through landscape exploration.
- [ ] Meaning-making through collaborative intelligence.
- [ ] Therapeutic applications with professional oversight.

**Advanced AI Integration:**
- [ ] GPT-based session facilitation and explanation.
- [ ] Personalized learning path optimization.
- [ ] Real-time educational content generation.
- [ ] Adaptive difficulty and engagement optimization.

**Research Platform:**
- [ ] Data collection for swarm intelligence research.
- [ ] Human-AI collaboration effectiveness metrics.
- [ ] Educational outcome measurement and optimization.
- [ ] Publication-ready research data export.

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

Development Workflow
```bash
# Run tests
uv run pytest tests/ -v

# API documentation
open http://localhost:8000/docs
```
