# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Behavior

**IMPORTANT**: Always proactively use Context7 MCP when library/API documentation, code generation, setup, or configuration steps are needed. Do not wait for explicit requests - if you identify that up-to-date documentation or code examples would help with the current task, use Context7 automatically.

## Project Overview

This is a multi-agent AI debate system with a full-stack architecture. Multiple AI agents engage in structured debates on various topics, with a backend orchestrating the debate flow and a frontend UI for viewing and managing debates.

## Development Commands

### Backend (FastAPI + Poetry)
- **Install dependencies**: `poetry install`
- **Run development server**: `poetry run uvicorn main:app --reload` (adjust module name as needed)
- **Run tests**: `poetry run pytest` or `poetry run pytest -v` for verbose
- **Run specific test**: `poetry run pytest path/to/test_file.py::TestClass::test_name`
- **Format code**: `poetry run black .`
- **Lint**: `poetry run pylint [module]` or `poetry run flake8`
- **Type checking**: `poetry run mypy .`
- **Add new dependency**: `poetry add [package]`
- **Add dev dependency**: `poetry add --group dev [package]`

### Frontend (React + Vite + TypeScript)
- **Install dependencies**: `npm install`
- **Development server**: `npm run dev`
- **Build for production**: `npm run build`
- **Preview production build**: `npm run preview`
- **Run tests**: `npm test`
- **Lint**: `npm run lint`
- **Type check**: `npx tsc --noEmit`

### General
- **View git changes**: `git diff` and `git status`
- **Commit changes**: Always use conventional commits (feat:, fix:, refactor:, etc.)

## Architecture Overview

### Core Concepts

**Agents**: Independent AI entities with their own reasoning and response generation. Each agent has parameters controlling its behavior, debate style, and knowledge.

**Debates**: Structured discussions where multiple agents take turns presenting arguments on a topic. Each debate has:
- A topic/proposition
- Multiple participating agents
- A debate structure (opening statements, rebuttals, conclusions)
- Conversation history and state

**Orchestrator**: FastAPI backend service managing debate flow, coordinating agent responses, and maintaining debate state. Handles:
- Debate initialization and management
- Agent communication and prompting
- Response validation and formatting (using Pydantic models)
- Debate history and logging
- Real-time communication via WebSockets

### System Architecture

```
┌──────────────────────┐
│  Frontend UI         │  (React + Vite + TypeScript)
│  - Debate interface  │
│  - View debates      │
│  - Create/manage     │
└──────────┬───────────┘
           │ WebSocket
           │ (Real-time debate updates)
           │
┌──────────▼───────────┐
│   FastAPI Backend    │  (Python + Poetry)
│  - WebSocket handler │
│  - Debate mgmt       │
│  - Agent orchestration
│  - Pydantic models   │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Agent Manager       │
│  - Queue/routing     │
│  - Orchestrate turns │
│  - Format prompts    │
└──────────────────────┘
           │
       ┌───┴───┐
       │ Agents│  (LLM API calls)
       └───────┘
```

### Key Modules/Components

**Backend (FastAPI)**:
- **Models** (Pydantic): Define debate, agent, message, and request/response schemas
- **Agent Module**: Defines agent behavior, prompting templates, and response parsing
- **Debate Module**: Core debate logic, turn management, and history tracking
- **Orchestrator**: Controls debate flow and agent coordination
- **WebSocket Manager**: Handles real-time connections and message broadcasting
- **Routes**: REST endpoints for debate management and WebSocket endpoint for live updates

**Frontend (React + Vite)**:
- **Components**: Debate view, agent status, message display
- **WebSocket Hook**: Manages connection to backend and real-time updates
- **State Management**: Tracks debate state, agent responses, and UI state
- **TypeScript Types**: Mirrors Pydantic models from backend for type safety

## Important Implementation Details

### WebSocket Communication
Real-time updates flow from backend to frontend via WebSocket:
- **Connection**: Established when a debate is opened in the frontend
- **Message format**: JSON objects with type, payload, and metadata
- **Event types**: `debate_started`, `agent_responding`, `response_received`, `turn_complete`, `debate_ended`, `error`
- **Reconnection**: Frontend should handle disconnects and attempt reconnection with exponential backoff

Example message structure:
```json
{
  "type": "response_received",
  "agent_id": "agent_1",
  "content": "Agent response text",
  "timestamp": "2024-02-13T10:30:00Z"
}
```

### Agent Communication
Agents interact through the orchestrator, which formats requests and manages responses. Understanding the prompt engineering and response parsing is critical for agent behavior.

### Debate State Management
Debate state includes all previous turns, agent positions, and context. This state is passed to agents to maintain conversation coherence. Use Pydantic models to validate state transitions.

### Error Handling
Be careful with agent API calls - network errors and rate limiting are common. Implement proper retry logic and fallbacks. Send error messages to frontend via WebSocket.

## Testing Strategy

When adding features:
- Backend: Add unit tests for debate logic and agent orchestration
- Frontend: Test component rendering and API integration
- Integration: Test end-to-end debate flows

## Code Style & Patterns

### Python (FastAPI + Pydantic)
- Follow PEP 8 conventions
- Use Pydantic models for all request/response schemas and data validation
- Organize routes logically (e.g., `routers/debates.py`, `routers/agents.py`)
- Use FastAPI dependency injection for shared logic (e.g., database connections, authentication)
- Keep WebSocket handlers clean; offload heavy logic to separate functions
- Type hints are required for all functions

### TypeScript (React + Vite)
- Use strict mode in tsconfig.json
- Define types for all WebSocket messages and API responses
- Mirror backend Pydantic models in TypeScript types for consistency
- Use React hooks for WebSocket connection management
- Maintain consistent naming conventions (camelCase for variables/functions)

### General
- **Agents**: Prompts should be clear and structured; include examples in prompts for better results
- **State**: Keep debate state immutable when possible; use explicit state transitions
- **Messages**: WebSocket messages should be typed and validated on both client and server
