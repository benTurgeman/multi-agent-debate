# Multi-Agent Debate Engine - Implementation Plan

## Context

Building a multi-agent AI debate system where multiple LLM instances (with configurable models) engage in structured debates. The system orchestrates turn-based discussions, maintains full conversation history, and uses a judge agent to evaluate and score participants at the end.

**Why this change:** Create a framework for AI-powered debates that can explore different perspectives on topics through specialized agents with unique stances, roles, and personalities. Support multiple LLM providers (Claude, OpenAI, etc.) with per-agent model selection.

**User Requirements:**
- Define debates with: topic, number of rounds, **N participants (2 or more)**
- Each participant = LLM API call with **selectable model** and custom system prompt (role, stance, persona)
- Agents take turns responding with full debate history as context
- Judge agent provides 0-10 scores and declares winner
- Export debate transcripts
- **Comprehensive unit testing throughout implementation**

**Scope:** Backend API only (REST + WebSocket for real-time updates)

---

## Architecture Overview

### Core Components

**Data Layer (Pydantic Models)**
- `ModelConfig`: LLM provider and model selection (e.g., "anthropic/claude-3-5-sonnet", "openai/gpt-4")
- `AgentConfig`: Defines participant parameters (model config, system prompt, stance, temperature, etc.)
- `DebateConfig`: Topic, rounds, **participant list (2+ agents)**, judge config
- `DebateState`: Current debate status, round tracking, full message history
- `Message`: Individual agent responses with metadata
- `JudgeResult`: Final scores (0-10), reasoning, and winner declaration

**Service Layer**
- `llm_client_base.py`: Abstract base class for LLM providers
- `anthropic_client.py`: Anthropic (Claude) implementation with retry logic
- `openai_client.py`: OpenAI (GPT) implementation with retry logic
- `llm_factory.py`: Factory to create appropriate LLM client based on model config
- `prompt_builder.py`: Constructs system prompts and formats debate history for context
- `agent_orchestrator.py`: Turn execution, determines next speaker, manages API calls via LLM factory
- `debate_manager.py`: High-level debate lifecycle, coordinates rounds, invokes judge, broadcasts WebSocket events

**API Layer**
- REST endpoints: Create, list, start, get, delete debates; export transcripts
- WebSocket endpoint: Real-time debate progress updates (`/api/ws/{debate_id}`)

**Storage**
- In-memory dictionary-based storage (thread-safe with asyncio locks)
- Repository pattern for future database migration

---

## File Structure

```
backend/
├── main.py                          # [MODIFY] Mount routers, add WebSocket
├── pyproject.toml                   # [MODIFY] Add LLM SDKs (anthropic, openai)
├── .env.example                     # [CREATE] API key template
├── models/
│   ├── __init__.py                  # [CREATE]
│   ├── llm.py                       # [CREATE] ModelConfig, ModelProvider enum
│   ├── agent.py                     # [CREATE] AgentConfig, AgentRole enum
│   ├── debate.py                    # [CREATE] DebateConfig, DebateState, DebateStatus enum
│   ├── message.py                   # [CREATE] Message, MessageHistory
│   ├── judge.py                     # [CREATE] JudgeResult, AgentScore
│   └── api.py                       # [CREATE] Request/Response schemas, WebSocketMessage
├── services/
│   ├── __init__.py                  # [CREATE]
│   ├── llm/
│   │   ├── __init__.py              # [CREATE]
│   │   ├── base.py                  # [CREATE] BaseLLMClient abstract class
│   │   ├── anthropic_client.py     # [CREATE] Anthropic implementation
│   │   ├── openai_client.py        # [CREATE] OpenAI implementation
│   │   └── factory.py               # [CREATE] LLM client factory
│   ├── prompt_builder.py            # [CREATE] System prompt construction
│   ├── agent_orchestrator.py       # [CREATE] Turn management
│   └── debate_manager.py            # [CREATE] Debate lifecycle orchestration
├── routers/
│   ├── __init__.py                  # [CREATE]
│   ├── debates.py                   # [CREATE] REST endpoints
│   └── websocket.py                 # [CREATE] WebSocket for real-time updates
├── core/
│   ├── __init__.py                  # [CREATE]
│   ├── config.py                    # [CREATE] Settings, API key loading
│   └── exceptions.py                # [CREATE] Custom exceptions
├── storage/
│   ├── __init__.py                  # [CREATE]
│   └── memory_store.py              # [CREATE] In-memory debate storage
└── tests/
    ├── __init__.py                  # [CREATE]
    ├── conftest.py                  # [CREATE] Pytest fixtures
    ├── test_models.py               # [CREATE] Test Pydantic models
    ├── test_llm_clients.py          # [CREATE] Test LLM client implementations
    ├── test_prompt_builder.py      # [CREATE] Test prompt construction
    ├── test_agent_orchestrator.py  # [CREATE] Test turn execution
    ├── test_debate_manager.py      # [CREATE] Test debate lifecycle
    ├── test_memory_store.py         # [CREATE] Test storage
    └── test_api.py                  # [CREATE] Test REST endpoints
```

---

## Critical Implementation Details

### 0. Multi-Model LLM Support

**Model Configuration:**
Each agent can use a different LLM provider and model. The `ModelConfig` specifies:
- `provider`: Enum value (ANTHROPIC, OPENAI, etc.)
- `model_name`: Specific model (e.g., "claude-3-5-sonnet-20241022", "gpt-4o")
- `api_key_env_var`: Environment variable name for API key (e.g., "ANTHROPIC_API_KEY")

**Example AgentConfig with Model Selection:**
```python
{
  "agent_id": "optimist",
  "model_config": {
    "provider": "anthropic",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key_env_var": "ANTHROPIC_API_KEY"
  },
  "role": "debater",
  "name": "Tech Optimist",
  "stance": "Pro",
  "system_prompt": "You are an optimistic technologist...",
  "temperature": 1.0,
  "max_tokens": 1024
}
```

**LLM Client Architecture:**

**Base Class (`services/llm/base.py`):**
```python
from abc import ABC, abstractmethod
from models.llm import ModelConfig

class BaseLLMClient(ABC):
    """Abstract base class for all LLM providers"""

    @abstractmethod
    async def send_message(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Send message to LLM and return response text"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for logging"""
        pass
```

**Anthropic Implementation (`services/llm/anthropic_client.py`):**
```python
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def send_message(self, system_prompt, messages, temperature, max_tokens):
        response = self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text

    def get_provider_name(self) -> str:
        return "anthropic"
```

**OpenAI Implementation (`services/llm/openai_client.py`):**
```python
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def send_message(self, system_prompt, messages, temperature, max_tokens):
        # OpenAI puts system prompt in messages array
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def get_provider_name(self) -> str:
        return "openai"
```

**Factory (`services/llm/factory.py`):**
```python
from models.llm import ModelConfig, ModelProvider
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from core.config import get_settings

def create_llm_client(model_config: ModelConfig) -> BaseLLMClient:
    """Factory method to create appropriate LLM client"""
    settings = get_settings()
    api_key = settings.get_api_key(model_config.api_key_env_var)

    if model_config.provider == ModelProvider.ANTHROPIC:
        return AnthropicClient(api_key, model_config.model_name)
    elif model_config.provider == ModelProvider.OPENAI:
        return OpenAIClient(api_key, model_config.model_name)
    else:
        raise ValueError(f"Unsupported provider: {model_config.provider}")
```

**Usage in Agent Orchestrator:**
```python
# In agent_orchestrator.py
from services.llm.factory import create_llm_client

async def execute_turn(debate_state: DebateState) -> Message:
    agent = get_next_agent(debate_state)

    # Create LLM client based on agent's model config
    llm_client = create_llm_client(agent.model_config)

    # Build prompts
    system_prompt = build_debater_prompt(agent, debate_state.config.topic, round_num)
    history_context = format_history_for_context(debate_state.history)

    # Call LLM (provider-agnostic)
    response = await llm_client.send_message(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": history_context}],
        temperature=agent.temperature,
        max_tokens=agent.max_tokens
    )

    # Create and return message
    return create_message(agent, response, round_num, turn_num)
```

**Key Benefits:**
- ✅ Each agent can use a different model (Claude 3.5 Sonnet, GPT-4o, etc.)
- ✅ Easy to add new providers (Gemini, Llama, etc.) by implementing BaseLLMClient
- ✅ Consistent interface across all providers
- ✅ Provider-specific retry logic and error handling

### 1. Debate Execution Flow

**Asynchronous Background Task Model:**
- `POST /api/debates/{id}/start` returns immediately (202 Accepted)
- Backend runs debate in asyncio background task
- Real-time updates pushed via WebSocket
- Prevents HTTP timeout on long-running debates

**Turn Loop (Sequential, supports N participants):**
```python
# turn_order is a list of agent_ids, can be 2, 3, 4, or more agents
for round_num in range(1, num_rounds + 1):
    for turn_num, agent_id in enumerate(turn_order):
        agent = get_agent_by_id(agent_id)

        # Create LLM client for this agent's model
        llm_client = create_llm_client(agent.model_config)

        # Build context with full debate history
        system_prompt = build_debater_prompt(agent, topic, round_num)
        history_context = format_history_for_context(debate_state.history)

        # Call LLM (provider-agnostic)
        response = await llm_client.send_message(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": history_context}],
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )

        # Store message and broadcast update
        message = create_message(agent, response, round_num, turn_num)
        debate_state.history.append(message)
        broadcast_ws("message_received", message)
```

**N-Participant Support:**
- Minimum: 2 agents (enforced by `min_length=2` in DebateConfig validation)
- Maximum: No hard limit, but practical limit ~5-10 for coherent debates
- Turn order cycles through all N agents each round
- Example with 3 agents: Round 1: A→B→C, Round 2: A→B→C, etc.
- Each agent sees all previous turns from all other agents in history

### 2. History Passing Strategy

Each agent receives full debate history formatted as:
```
DEBATE TOPIC: {topic}
ROUND: {current_round} of {total_rounds}

DEBATE HISTORY:
[Round 1, Turn 1] Agent A (Pro): {message content}
[Round 1, Turn 2] Agent B (Con): {message content}
[Round 2, Turn 1] Agent A (Pro): {message content}
...

YOUR TURN: Please provide your response as {agent_name} ({stance}).
```

**System Prompt Template:**
```
{custom_system_prompt_from_config}

DEBATE CONTEXT:
- Topic: {topic}
- Your stance: {stance}
- Current round: {round} of {total_rounds}

INSTRUCTIONS:
- Present clear arguments supporting your position
- Respond to opposing arguments from previous turns
- Maintain your persona and debate style
- Be persuasive but respectful
- Aim for 200-400 words
```

### 3. Judge Agent Implementation

**Invocation:** After all rounds complete, judge receives:
- Debate topic
- Complete message history
- Participant list with stances

**Judge System Prompt:**
```
You are an impartial debate judge.

DEBATE TOPIC: {topic}
PARTICIPANTS: {list with stances}

FULL TRANSCRIPT:
{all messages chronologically}

TASK:
1. Score each participant 0-10 on: argument quality, logic, evidence, rebuttals, persuasiveness
2. Provide reasoning for each score
3. Identify key arguments from each side
4. Declare winner (highest score)

Respond in JSON:
{
  "summary": "Overall debate analysis",
  "agent_scores": [
    {"agent_id": "...", "agent_name": "...", "score": 8.5, "reasoning": "..."}
  ],
  "winner_id": "...",
  "winner_name": "...",
  "key_arguments": ["...", "..."]
}
```

**Parsing:** Try JSON parse first, fallback to regex/LLM extraction if needed

### 4. WebSocket Event Types

- `debate_started`: Debate execution begins
- `round_started`: New round begins (payload: round_number)
- `agent_thinking`: Agent is preparing response (payload: agent_id, agent_name)
- `message_received`: Agent response received (payload: full Message object)
- `turn_complete`: Turn finished
- `round_complete`: Round finished
- `judging_started`: Judge is evaluating
- `judge_result`: Final judgment (payload: JudgeResult object)
- `debate_complete`: Entire debate finished
- `error`: Error occurred (payload: error_message, context)

### 5. Error Handling

**LLM API Errors:**
- Use `tenacity` library for exponential backoff retry (3 attempts)
- Retry on provider-specific errors:
  - Anthropic: `APIConnectionError`, `RateLimitError`
  - OpenAI: `APIError`, `RateLimitError`
- On failure: Set debate status to `FAILED`, broadcast error event, store error message
- Preserve all messages completed before failure

**Rate Limiting:**
- Provider-specific limits vary (Anthropic: ~50 req/min, OpenAI: depends on tier)
- For 3 agents, 5 rounds: 16 total API calls (well under most limits)
- Add sleep(1) between turns as safety margin
- Consider implementing per-provider rate limiters for production

### 6. Export Transcripts

**Endpoint:** `GET /api/debates/{id}/export?format={json|markdown|text}`

**JSON Format:** Full DebateState object serialized

**Markdown Format:**
```markdown
# Debate: {topic}
Date: {created_at}
Rounds: {num_rounds}
Status: {status}

## Participants
- **Agent A** (Pro): {system_prompt_summary}
- **Agent B** (Con): {system_prompt_summary}

## Debate Transcript

### Round 1
**Agent A (Pro):**
{message content}

**Agent B (Con):**
{message content}

### Round 2
...

## Judge's Decision
Winner: **{winner_name}**

{summary}

### Scores
- Agent A: 8.5/10 - {reasoning}
- Agent B: 7.2/10 - {reasoning}
```

**Text Format:** Similar to markdown but plain text, no formatting

---

## REST API Endpoints

```
POST   /api/debates              Create new debate (returns debate_id)
GET    /api/debates              List all debates
GET    /api/debates/{id}         Get debate details and full state
POST   /api/debates/{id}/start   Start debate execution (async, returns 202)
GET    /api/debates/{id}/status  Get current status (round, turn, message count)
GET    /api/debates/{id}/export  Export transcript (query param: format=json|markdown|text)
DELETE /api/debates/{id}         Delete debate
GET    /health                   Health check (already exists)
```

```
WS     /api/ws/{debate_id}       WebSocket connection for real-time updates
```

---

## Key Files to Implement

### Priority 1: Foundation (with tests)
1. **backend/core/config.py** + **tests/test_config.py** - Load API keys from environment
2. **backend/core/exceptions.py** - Custom exceptions (DebateNotFound, DebateExecutionError, etc.)
3. **backend/models/llm.py** + **tests/test_models.py** - ModelConfig, ModelProvider enum
4. **backend/models/agent.py** + **tests/test_models.py** - AgentConfig with ModelConfig, AgentRole enum
5. **backend/models/message.py** + **tests/test_models.py** - Message, MessageHistory
6. **backend/models/debate.py** + **tests/test_models.py** - DebateConfig (validates 2+ agents), DebateState, DebateStatus enum
7. **backend/models/judge.py** + **tests/test_models.py** - JudgeResult, AgentScore
8. **backend/models/api.py** + **tests/test_models.py** - Request/response schemas, WebSocketMessage
9. **backend/storage/memory_store.py** + **tests/test_memory_store.py** - Thread-safe storage with asyncio locks

**Run tests:** `poetry run pytest tests/test_models.py tests/test_memory_store.py -v`

### Priority 2: LLM Integration (with tests)
10. **backend/services/llm/base.py** - BaseLLMClient abstract class
11. **backend/services/llm/anthropic_client.py** + **tests/test_llm_clients.py** - Anthropic implementation with retry
12. **backend/services/llm/openai_client.py** + **tests/test_llm_clients.py** - OpenAI implementation with retry
13. **backend/services/llm/factory.py** + **tests/test_llm_clients.py** - LLM client factory
14. **backend/services/prompt_builder.py** + **tests/test_prompt_builder.py** - Build prompts, format history

**Run tests:** `poetry run pytest tests/test_llm_clients.py tests/test_prompt_builder.py -v`

### Priority 3: Debate Logic (with tests)
15. **backend/services/agent_orchestrator.py** + **tests/test_agent_orchestrator.py** - execute_turn(), get_next_agent()
16. **backend/services/debate_manager.py** + **tests/test_debate_manager.py** - create_debate(), run_debate(), invoke_judge()

**Run tests:** `poetry run pytest tests/test_agent_orchestrator.py tests/test_debate_manager.py -v`

### Priority 4: API Layer (with tests)
17. **backend/routers/debates.py** + **tests/test_api.py** - All REST endpoints
18. **backend/routers/websocket.py** + **tests/test_api.py** - WebSocket connection management
19. **backend/main.py** - Mount routers, configure WebSocket, update CORS

**Run tests:** `poetry run pytest tests/test_api.py -v`

### Priority 5: Configuration
20. **backend/pyproject.toml** - Add LLM SDKs and test dependencies
21. **backend/.env.example** - API key templates for all providers
22. **backend/tests/conftest.py** - Pytest fixtures for mocking LLM clients

---

## Dependencies to Add

```toml
[tool.poetry.dependencies]
anthropic = "^0.18.0"         # Claude API SDK
openai = "^1.12.0"            # OpenAI API SDK
tenacity = "^8.2.0"           # Retry logic with exponential backoff
websockets = "^12.0"          # WebSocket support (if not included with FastAPI)
python-dotenv = "^1.0.0"      # Load .env files

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"             # Test framework
pytest-asyncio = "^0.21.0"    # Async test support
pytest-cov = "^4.1.0"         # Coverage reporting
pytest-mock = "^3.12.0"       # Mocking utilities
httpx = "^0.25.0"             # Test client for FastAPI
```

---

## Implementation Sequence

**CRITICAL: Test-Driven Development Approach**
- Write tests FIRST or immediately AFTER implementing each component
- Run tests after EVERY change: `poetry run pytest -v`
- Maintain >80% code coverage: `poetry run pytest --cov=. --cov-report=html`
- Never move to next phase without passing tests

### Phase 1: Core Models & Infrastructure (Day 1)
1. Update pyproject.toml with all dependencies, run `poetry install`
2. Create core/config.py with multi-provider API key loading
3. Create core/exceptions.py with custom exceptions
4. Create models/llm.py (ModelConfig, ModelProvider enum)
5. Create models/agent.py (AgentConfig with model_config field)
6. Create models/message.py (Message, MessageHistory)
7. Create models/debate.py (DebateConfig with 2+ agent validation, DebateState)
8. Create models/judge.py (JudgeResult, AgentScore)
9. Create models/api.py (Request/Response schemas)
10. Create storage/memory_store.py with thread-safe CRUD
11. **Write tests:** tests/test_models.py, tests/test_memory_store.py, tests/conftest.py
12. **Run tests:** `poetry run pytest tests/test_models.py tests/test_memory_store.py -v`
13. **Verify:** All model validations work, 2+ agents enforced, storage operations succeed

### Phase 2: LLM Integration (Day 2)
14. Create services/llm/base.py (BaseLLMClient abstract class)
15. Create services/llm/anthropic_client.py with retry logic
16. Create services/llm/openai_client.py with retry logic
17. Create services/llm/factory.py (LLM client factory)
18. Create services/prompt_builder.py (prompt templates, history formatting)
19. **Write tests:** tests/test_llm_clients.py (mock API calls), tests/test_prompt_builder.py
20. **Run tests:** `poetry run pytest tests/test_llm_clients.py tests/test_prompt_builder.py -v`
21. **Verify:** Factory creates correct clients, prompts format properly, history includes all agents

### Phase 3: Debate Orchestration (Day 3)
22. Create services/agent_orchestrator.py (execute_turn, get_next_agent, prepare_context)
23. **Write tests:** tests/test_agent_orchestrator.py (test turn execution, N-agent ordering)
24. **Run tests:** `poetry run pytest tests/test_agent_orchestrator.py -v`
25. **Verify:** Turns cycle correctly through N agents, history passes to all agents
26. Create services/debate_manager.py (create_debate, run_debate, invoke_judge, WebSocket broadcast)
27. **Write tests:** tests/test_debate_manager.py (test full debate lifecycle, judge invocation)
28. **Run tests:** `poetry run pytest tests/test_debate_manager.py -v`
29. **Verify:** Full debate completes, judge receives all messages, winner declared correctly
30. **Integration test:** Run 3-agent debate with mixed models (Claude + GPT)

### Phase 4: API Layer (Day 4)
31. Create routers/debates.py (POST create, GET list/details, POST start, GET export, DELETE)
32. Create routers/websocket.py (WebSocket connection, message broadcasting)
33. Update main.py (mount routers, CORS, WebSocket config)
34. **Write tests:** tests/test_api.py (test all endpoints, WebSocket events)
35. **Run tests:** `poetry run pytest tests/test_api.py -v`
36. **Verify:** All endpoints work, WebSocket broadcasts events, export formats valid
37. **Manual test:** Create 3-agent debate via API, connect WebSocket, start debate, export

### Phase 5: Export & Polish (Day 5)
38. Implement export endpoint with JSON/Markdown/Text formatters
39. Add comprehensive error handling across all modules
40. **Write tests:** Test edge cases (API failures, invalid inputs, N>10 agents)
41. **Run full test suite:** `poetry run pytest -v --cov=. --cov-report=html`
42. **Verify:** >80% coverage, all tests pass, error handling works
43. Test with real LLM APIs (not mocks): 2-agent debate, 3-agent debate, 5-agent debate
44. Update README with usage examples and API documentation

---

## Testing Strategy

### Manual Testing Flow
1. Set ANTHROPIC_API_KEY in .env
2. Run backend: `poetry run uvicorn main:app --reload`
3. Create debate via REST:
   ```bash
   curl -X POST http://localhost:8000/api/debates \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "AI will benefit humanity more than harm it",
       "num_rounds": 2,
       "agents": [
         {
           "agent_id": "optimist",
           "model_config": {
             "provider": "anthropic",
             "model_name": "claude-3-5-sonnet-20241022",
             "api_key_env_var": "ANTHROPIC_API_KEY"
           },
           "role": "debater",
           "name": "Tech Optimist",
           "stance": "Pro",
           "system_prompt": "You are an optimistic technologist who believes AI will solve major problems.",
           "temperature": 1.0,
           "max_tokens": 1024
         },
         {
           "agent_id": "skeptic",
           "model_config": {
             "provider": "openai",
             "model_name": "gpt-4o",
             "api_key_env_var": "OPENAI_API_KEY"
           },
           "role": "debater",
           "name": "AI Skeptic",
           "stance": "Con",
           "system_prompt": "You are a cautious critic who worries about AI risks and unintended consequences.",
           "temperature": 0.9,
           "max_tokens": 1024
         },
         {
           "agent_id": "neutral",
           "model_config": {
             "provider": "anthropic",
             "model_name": "claude-3-5-sonnet-20241022",
             "api_key_env_var": "ANTHROPIC_API_KEY"
           },
           "role": "debater",
           "name": "Pragmatist",
           "stance": "Neutral",
           "system_prompt": "You weigh both benefits and risks, seeking balanced perspectives.",
           "temperature": 1.0,
           "max_tokens": 1024
         }
       ],
       "judge_config": {
         "agent_id": "judge",
         "model_config": {
           "provider": "anthropic",
           "model_name": "claude-3-5-sonnet-20241022",
           "api_key_env_var": "ANTHROPIC_API_KEY"
         },
         "role": "judge",
         "name": "Impartial Judge",
         "system_prompt": "You are a fair debate judge evaluating arguments objectively.",
         "temperature": 0.7,
         "max_tokens": 2048
       }
     }'
   ```
4. Connect WebSocket: `wscat -c ws://localhost:8000/api/ws/{debate_id}`
5. Start debate: `curl -X POST http://localhost:8000/api/debates/{id}/start`
6. Watch real-time updates in WebSocket
7. Export transcript: `curl http://localhost:8000/api/debates/{id}/export?format=markdown`

### Validation Checks
- ✅ **N-participant support:** Test with 2, 3, 4, 5 agents successfully
- ✅ **Multi-model support:** Test mixing Claude + OpenAI agents in same debate
- ✅ Agents receive full debate history in correct format
- ✅ Turns cycle through all N agents in specified order
- ✅ Judge receives complete transcript with all N agents' messages
- ✅ Scores are 0-10 floats with reasoning for each agent
- ✅ Winner has highest score
- ✅ WebSocket events fire in correct sequence
- ✅ Export formats are valid and complete
- ✅ Error handling works (API failures, invalid debate IDs, missing API keys)
- ✅ **Unit tests pass:** All modules have >80% coverage
- ✅ **Integration tests pass:** Full debate lifecycle works end-to-end

---

## Configuration & Setup

### Environment Variables
Create `.env` file (never commit):
```
# LLM Provider API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...

# Optional: Add more providers as needed
# GOOGLE_API_KEY=...
# COHERE_API_KEY=...
```

**Note:** Only set API keys for providers you plan to use. The system will fail gracefully if an agent's provider key is missing.

### Running the Backend
```bash
# Install dependencies
cd backend
poetry install

# Run tests
poetry run pytest -v

# Run tests with coverage
poetry run pytest --cov=. --cov-report=html
# View coverage: open htmlcov/index.html

# Run development server
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Check health
curl http://localhost:8000/health
```

---

## Future Enhancements (Out of Scope)

- Database persistence (PostgreSQL with SQLAlchemy)
- Streaming responses from Claude API (token-by-token updates)
- Frontend UI (React + TypeScript)
- Multiple debate formats (Oxford, Lincoln-Douglas)
- Pause/resume debates mid-execution
- User authentication and authorization
- Multiple judges with voting
- Agent personality presets library
- Advanced export formats (PDF with styling)

---

## Risk Mitigation

**Risk:** Claude API rate limiting on large debates
**Mitigation:** Add sleep(1) between turns, implement request queue for production

**Risk:** Long debate execution times
**Mitigation:** Async execution prevents blocking, WebSocket shows progress, set max timeout

**Risk:** API errors mid-debate
**Mitigation:** Comprehensive error handling, preserve completed messages, clear error reporting

**Risk:** In-memory state loss on restart
**Mitigation:** Document limitation, export important debates, plan DB migration path

**Risk:** WebSocket connection drops
**Mitigation:** Debate continues backend-side, client can reconnect and GET latest state via REST
