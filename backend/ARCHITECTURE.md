# Architecture

This document provides a comprehensive overview of the multi-agent debate system architecture.

## System Overview

The multi-agent debate system is a FastAPI-based backend that orchestrates structured discussions between multiple AI agents. The system uses **LiteLLM** as a unified gateway, supporting cloud providers (Claude, GPT-4) and local models (Ollama/Llama 2, Mistral) with seamless mixing. Real-time updates are delivered via WebSockets.

**High-Level Flow:**
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

## Core Concepts

### Agents
Independent AI entities with their own reasoning and response generation. Each agent has:
- **Model Configuration**: LLM provider (Anthropic/OpenAI) and specific model
- **Role**: `FOR` or `AGAINST` the debate proposition
- **Identity**: Name and personality for consistent argumentation
- **Parameters**: Temperature, max tokens, system prompts

Agents are stateless - all context comes from debate history passed to them on each turn.

### Debates
Structured discussions where multiple agents take turns presenting arguments. Each debate includes:
- **Topic/Proposition**: The statement being debated
- **Participating Agents**: 2+ agents with different perspectives
- **Structure**: Configurable number of rounds
- **State**: Current round, turn order, conversation history
- **Judging**: Optional AI judge evaluates arguments and determines winner

**Debate Lifecycle:**
1. `PENDING` - Created, not started
2. `RUNNING` - Agents taking turns
3. `JUDGING` - Judge evaluating (if enabled)
4. `COMPLETE` - Finished with results

### Orchestrator
The backend service managing debate flow and coordinating all components:
- **Debate Initialization**: Validates config, creates state
- **Turn Management**: Executes agent turns sequentially
- **Prompt Building**: Formats context with history and instructions
- **Response Validation**: Ensures agent outputs are well-formed
- **Event Broadcasting**: Emits updates for real-time UI
- **Error Handling**: Automatic retries with exponential backoff

## Component Layers

### Data Layer (Pydantic Models)

**Located in:** `backend/models/`

Pydantic models provide data validation, serialization, and API contracts:

- **`llm.py`**:
  - `ModelProvider`: Enum for LLM providers (ANTHROPIC, OPENAI)
  - `LLMConfig`: Model selection, API keys, provider-specific settings

- **`agent.py`**:
  - `AgentRole`: Enum for debate positions (FOR, AGAINST)
  - `AgentConfig`: Agent identity, role, LLM config, temperature

- **`debate.py`**:
  - `DebateConfig`: Topic, agents, rounds, judge settings
  - `DebateState`: Current state, history, status tracking
  - `DebateStatus`: Lifecycle enum (PENDING, RUNNING, JUDGING, COMPLETE)

- **`message.py`**:
  - `Message`: Agent responses with metadata (timestamp, turn number)

- **`judge.py`**:
  - `JudgeResult`: Winner, scores (0-10), reasoning

- **`api.py`**:
  - Request/response schemas for REST endpoints

**Design Pattern:** All models use Pydantic for automatic validation and JSON serialization, ensuring type safety across API boundaries.

### Service Layer

**Located in:** `backend/services/`

Business logic and core functionality:

#### LLM Clients (`services/llm/`)
Unified abstraction over multiple LLM providers using **LiteLLM**:

- **`base.py`**: `BaseLLMClient` abstract interface
- **`litellm_client.py`**: Unified client for all providers via LiteLLM
- **`factory.py`**: `create_llm_client(config)` factory function

**Unified Client Architecture:**
The system uses [LiteLLM](https://docs.litellm.ai/) as a gateway to access all LLM providers through a single, consistent interface. This eliminates the need for provider-specific client code.

**Provider Format:** `"provider/model_name"` (e.g., `"anthropic/claude-sonnet-4-5-20250929"`)

**Supported Providers:**
- **Anthropic**: Claude models (`anthropic/claude-sonnet-4-5-20250929`)
- **OpenAI**: GPT models (`openai/gpt-4o`)
- **Ollama**: Local models (`ollama/llama2`, `ollama/mistral`) - runs locally, no API key required
- **Extensible**: Any provider supported by LiteLLM can be added without code changes

**Interface:**
```python
async def send_message(
    system_prompt: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int
) -> str
```

**Adding New Providers:**
To add a new LLM provider (e.g., Google Gemini, Cohere):
1. Add model entry to `provider_catalog.py`
2. Update frontend model selector (no backend code changes needed)

This architecture enables:
- ✅ Agent-level model mixing (mix cloud and local models in same debate)
- ✅ Zero-code provider addition
- ✅ Consistent error handling across all providers
- ✅ Local model support for privacy and cost savings

#### Prompt Builder (`prompt_builder.py`)
Context formatting and instruction generation:

- **`build_debater_prompt()`**: System prompts for debate agents
- **`build_judge_prompt()`**: Evaluation instructions for judges
- **`format_history_for_context()`**: Conversation history formatting

Prompts include debate metadata (round, topic, role) and full message history for coherent multi-turn discussions.

#### Agent Orchestrator (`agent_orchestrator.py`)
Executes individual agent turns:

- Creates LLM client for agent's configured model
- Builds prompts with current debate context
- Sends request to LLM API
- Handles retries on failure (up to 3 attempts with exponential backoff)
- Validates and returns response

**Retry Logic:** 1s, 2s, 4s delays on temporary failures (rate limiting, network errors).

#### Debate Manager (`debate_manager.py`)
Orchestrates complete debates:

- **Initialization**: Validates config, creates initial state
- **Turn Execution**: Iterates through agents × rounds
- **History Tracking**: Maintains full conversation context
- **Judge Invocation**: Evaluates debate when enabled
- **Event Emission**: Broadcasts updates via callback system
- **Error Recovery**: Handles agent failures gracefully

**Event Types:**
- `DEBATE_STARTED`
- `TURN_STARTED`
- `TURN_COMPLETED`
- `DEBATE_JUDGING`
- `DEBATE_COMPLETE`
- `ERROR`

### API Layer

**Located in:** `backend/routers/`

FastAPI REST and WebSocket endpoints:

#### REST Endpoints (`routers/debates.py`)
- `POST /api/debates` - Create debate
- `GET /api/debates` - List debates
- `GET /api/debates/{id}` - Get debate details
- `GET /api/debates/{id}/status` - Get current status
- `POST /api/debates/{id}/start` - Start debate (async background task)
- `DELETE /api/debates/{id}` - Delete debate

**Async Execution:** Debates run in `BackgroundTasks` to prevent HTTP timeouts on long debates (can take minutes with multiple rounds).

#### WebSocket (`routers/websocket.py`)
- `WS /ws/{debate_id}` - Real-time debate updates

WebSocket broadcasts all debate events as JSON messages:
```json
{
  "type": "TURN_COMPLETED",
  "agent_id": "agent_1",
  "content": "Agent response...",
  "timestamp": "2024-02-13T10:30:00Z",
  "turn": 1,
  "round": 1
}
```

**Connection Management:** WebSocket manager maintains active connections per debate and broadcasts events to all connected clients.

### Storage Layer

**Located in:** `backend/storage/`

#### In-Memory Store (`memory_store.py`)
Current implementation using thread-safe in-memory dictionaries:

- **`DebateRepository`**: CRUD operations for debates
- **Thread Safety**: Uses locks for concurrent access
- **Fast Access**: O(1) lookups, ideal for development/testing

**Repository Pattern:** Abstract storage interface enables future migration to databases without changing business logic.

## Design Decisions

### Multi-Model LLM Support

**Decision:** Allow different LLM providers and models per agent.

**Rationale:**
- Enables diverse perspectives (Claude vs GPT-4 reasoning styles)
- Users can optimize cost/performance per agent
- Demonstrates real multi-model orchestration

**Trade-offs:**
- More complex client management
- Different rate limits per provider
- Requires multiple API keys

**Implementation:** Factory pattern + abstract base class ensures consistent interface across providers.

### Event-Driven Architecture

**Decision:** Emit events at each debate milestone for real-time UI updates.

**Rationale:**
- Long debates (minutes) need progress feedback
- WebSocket connection enables live experience
- Decouples debate logic from communication layer

**Trade-offs:**
- Additional complexity in event handling
- WebSocket connection management overhead
- Must handle client disconnects gracefully

**Implementation:** DebateManager emits events via callback, WebSocket broadcasts to connected clients.

### Asynchronous Execution

**Decision:** Run debates in FastAPI BackgroundTasks, not in request handlers.

**Rationale:**
- HTTP requests timeout after 30s, but debates can take minutes
- Frontend needs immediate response (debate created, starting)
- Backend processes debate asynchronously

**Trade-offs:**
- No direct error feedback in response
- Errors reported via WebSocket events instead
- Client must handle async lifecycle

**Implementation:** `POST /api/debates/{id}/start` returns immediately, debate runs in background, status available via GET and WebSocket.

### Repository Pattern

**Decision:** Abstract storage behind repository interface.

**Rationale:**
- Current in-memory store simple for development
- Future needs: PostgreSQL for persistence, multi-user support
- Repository pattern enables migration without rewriting services

**Trade-offs:**
- Additional abstraction layer
- Slightly more code than direct storage access

**Implementation:** `DebateRepository` defines interface, `MemoryDebateRepository` implements in-memory version.

## Key Architectural Patterns

### Dependency Injection
FastAPI's dependency system provides:
- Database/storage access
- Shared configuration
- Request-scoped resources

### Factory Pattern
`create_llm_client()` creates provider-specific clients from `LLMConfig`.

### Strategy Pattern
`BaseLLMClient` interface allows swapping LLM providers at runtime.

### Observer Pattern
Event emission enables multiple consumers (WebSocket, logging, metrics).

## Future Considerations

### Database Migration
**When:** Multi-user support, debate persistence required

**Options:**
- PostgreSQL with SQLAlchemy ORM
- Debate history, user accounts, access control
- Minimal changes: update `DebateRepository` implementation

### Authentication/Authorization
**When:** Public deployment or multi-tenant use

**Needs:**
- User accounts and API keys
- Debate ownership and visibility controls
- Rate limiting per user

### Token Streaming
**When:** Better UX for long agent responses

**Approach:**
- Stream LLM tokens as they're generated
- WebSocket sends incremental updates
- Requires streaming support in LLM clients

### Prompt Caching
**When:** Optimize cost/latency for repeated contexts

**Approach:**
- Cache formatted debate history
- Anthropic prompt caching for repeated context
- Reduce tokens on each agent turn

### Debate Templates
**When:** Common debate structures (Oxford style, Lincoln-Douglas, etc.)

**Approach:**
- Predefined round structures and rules
- Template-based prompt generation
- Custom evaluation criteria per format

### Multi-Language Support
**When:** International users

**Approach:**
- Detect debate language
- Localized prompts and UI
- Language-specific judge evaluation

## Component Dependencies

```
main.py (FastAPI app)
  ├── routers/
  │   ├── debates.py → services/debate_manager
  │   └── websocket.py → services/debate_manager
  │
  └── services/
      ├── debate_manager.py → agent_orchestrator, storage
      ├── agent_orchestrator.py → llm/*, prompt_builder
      ├── prompt_builder.py → models/*
      └── llm/
          ├── factory.py → anthropic_client, openai_client
          ├── anthropic_client.py → base
          └── openai_client.py → base
```

**Dependency Flow:** API → Services → Storage/External APIs

**Key Principle:** Services depend on abstractions (interfaces), not concrete implementations.

## Testing Strategy

### Unit Tests
- Model validation (Pydantic schemas)
- Prompt building (no external calls)
- Repository operations (in-memory)

### Integration Tests
- LLM client interactions (with real APIs)
- Debate manager orchestration
- End-to-end debate flows

### Manual Tests
- WebSocket connectivity
- Error handling scenarios
- Multi-provider debates

**Coverage:** 97% (150 tests) - see backend/README.md for details.

---

**Last Updated:** 2024-02-13

For API reference, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
