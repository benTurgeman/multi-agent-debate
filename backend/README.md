# Debate Backend

Multi-agent AI debate system backend built with FastAPI.

## Features

- 🤖 **Multi-Agent Debates**: Support for 2+ agents with different perspectives
- 🔄 **Multiple LLM Providers**: Mix Claude and OpenAI models in the same debate
- 🎯 **Turn-Based Discussion**: Sequential rounds with full conversation history
- ⚖️ **AI Judge**: Automated evaluation with 0-10 scoring and winner selection
- 🔁 **Automatic Retries**: Resilient to temporary API failures (up to 3 retries per turn)
- ⏱️ **Rate Limiting**: Built-in delays to prevent API throttling
- 📡 **Event System**: Real-time updates via callback system
- 💾 **In-Memory Storage**: Fast, thread-safe debate state management

## Setup

```bash
cd backend
poetry install
```

## Environment Variables

Create a `.env` file in the backend directory with your API keys:

```bash
# Required API keys (add only the ones you plan to use)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
```

## Run

```bash
poetry run uvicorn main:app --reload
```

## Test

Run all tests:
```bash
poetry run pytest -v
```

Run with coverage:
```bash
poetry run pytest --cov=. --cov-report=html
# Open coverage report: open htmlcov/index.html
```

Run specific test files:
```bash
poetry run pytest tests/test_llm_clients.py -v
poetry run pytest tests/test_prompt_builder.py -v
poetry run pytest tests/test_edge_cases.py -v
```

**Test Coverage:** 97% overall (150 tests)
- ✅ Models and validation
- ✅ LLM client integration (Anthropic + OpenAI)
- ✅ Debate orchestration
- ✅ Event system
- ✅ Error handling and retries
- ✅ API endpoints and WebSocket
- ✅ Edge cases (10+ agents, invalid inputs, API failures)

## Usage

### Running a Debate

```python
from services.debate_manager import DebateManager
from models.debate import DebateConfig
from models.agent import AgentConfig, AgentRole
from models.llm import LLMConfig, ModelProvider

# Create agent configurations
agents = [
    AgentConfig(
        agent_id="optimist",
        llm_config=LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY"
        ),
        role=AgentRole.DEBATER,
        name="Tech Optimist",
        stance="Pro",
        system_prompt="You believe AI will benefit humanity.",
        temperature=1.0,
        max_tokens=1024
    ),
    AgentConfig(
        agent_id="skeptic",
        llm_config=LLMConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            api_key_env_var="OPENAI_API_KEY"
        ),
        role=AgentRole.DEBATER,
        name="AI Skeptic",
        stance="Con",
        system_prompt="You are cautious about AI risks.",
        temperature=0.9,
        max_tokens=1024
    )
]

# Create judge configuration
judge = AgentConfig(
    agent_id="judge",
    llm_config=LLMConfig(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet-20241022",
        api_key_env_var="ANTHROPIC_API_KEY"
    ),
    role=AgentRole.JUDGE,
    name="Judge",
    stance="Impartial",
    system_prompt="You are a fair debate judge.",
    temperature=0.7,
    max_tokens=2048
)

# Create debate configuration
config = DebateConfig(
    topic="AI will benefit humanity more than harm it",
    num_rounds=2,
    agents=agents,
    judge_config=judge
)

# Run debate
manager = DebateManager()
debate_state = manager.create_debate(config)

# Optional: Register event callback for real-time updates
def on_event(event):
    print(f"Event: {event.event_type}")
    if hasattr(event.payload, 'get'):
        print(f"Payload: {event.payload}")

manager.register_event_callback(on_event)

# Execute the debate
result = await manager.run_debate(debate_state)

# Access results
print(f"Status: {result.status}")
print(f"Winner: {result.judge_result.winner_name}")
print(f"Score: {result.judge_result.get_score_for_agent(result.judge_result.winner_id)}")

# Access all messages
for msg in result.history:
    print(f"[Round {msg.round_number}] {msg.agent_name}: {msg.content[:100]}...")
```

### Event System

The debate manager emits events during execution:

```python
from services.debate_manager import DebateEventType

def handle_events(event):
    if event.event_type == DebateEventType.MESSAGE_RECEIVED:
        message = event.payload['message']
        print(f"Agent {message['agent_name']} responded")

    elif event.event_type == DebateEventType.JUDGE_RESULT:
        result = event.payload['judge_result']
        print(f"Winner: {result['winner_name']}")

    elif event.event_type == DebateEventType.ERROR:
        print(f"Error: {event.payload['error_message']}")

manager.register_event_callback(handle_events)
```

**Available Events:**
- `DEBATE_STARTED` - Debate execution begins
- `ROUND_STARTED` - New round begins
- `AGENT_THINKING` - Agent is preparing response
- `MESSAGE_RECEIVED` - Agent response received
- `TURN_COMPLETE` - Turn finished
- `ROUND_COMPLETE` - Round finished
- `JUDGING_STARTED` - Judge evaluation begins
- `JUDGE_RESULT` - Judge verdict received
- `DEBATE_COMPLETE` - Debate finished
- `ERROR` - Error occurred

## Architecture

For system architecture and design details, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

## Advanced Usage

### Direct LLM Client Access

Use LLM clients independently from debates:

```python
from models.llm import LLMConfig, ModelProvider
from services.llm import create_llm_client

# Configure and create client
config = LLMConfig(
    provider=ModelProvider.ANTHROPIC,
    model_name="claude-3-5-sonnet-20241022",
    api_key_env_var="ANTHROPIC_API_KEY"
)
client = create_llm_client(config)

# Send message
response = await client.send_message(
    system_prompt="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=1.0,
    max_tokens=1024
)
```

**Supported Providers:** Anthropic (Claude models), OpenAI (GPT-4 models)

### Custom Prompt Building

Build prompts programmatically:

```python
from services.prompt_builder import build_debater_prompt, format_history_for_context

# Build system prompt for debater
system_prompt = build_debater_prompt(
    agent=agent_config,
    topic="AI will benefit humanity",
    current_round=2,
    total_rounds=5
)

# Format debate history for context
context = format_history_for_context(
    history=messages,
    topic="AI will benefit humanity",
    current_round=2,
    total_rounds=5
)
```

## Testing

The project uses pytest with async support and comprehensive test coverage:

```bash
# Run all tests
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=. --cov-report=html

# Run specific test file
poetry run pytest tests/test_debate_manager.py -v
```

## Manual Testing with Real LLM APIs

Test with actual LLM providers using the manual test scripts:

```bash
# 2-agent debate (Claude only)
python manual_tests/test_2_agent_debate.py

# 3-agent debate (Claude + GPT-4 - requires both API keys)
python manual_tests/test_3_agent_debate.py

# 5-agent debate (complex multi-perspective debate)
python manual_tests/test_5_agent_debate.py
```

See `manual_tests/README.md` for detailed information about each test, expected behavior, and troubleshooting.

**Note:** These tests make real API calls and consume credits. Ensure API keys are set in `.env` before running.

---

## Documentation

For more information, see:
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete REST and WebSocket API reference
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design decisions
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and debugging guide
- **[manual_tests/README.md](./manual_tests/README.md)** - Manual testing guide with real LLMs

### Quick API Example

Create and run a debate via REST API:

```bash
# 1. Create a debate
curl -X POST http://localhost:8000/api/debates \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "config": {
    "topic": "Climate change is the biggest challenge of our time",
    "num_rounds": 2,
    "agents": [
      {
        "agent_id": "scientist",
        "llm_config": {
          "provider": "anthropic",
          "model_name": "claude-3-5-sonnet-20241022",
          "api_key_env_var": "ANTHROPIC_API_KEY"
        },
        "role": "debater",
        "name": "Climate Scientist",
        "stance": "Pro",
        "system_prompt": "You are a climate scientist presenting evidence about climate change.",
        "temperature": 1.0,
        "max_tokens": 1024
      },
      {
        "agent_id": "economist",
        "llm_config": {
          "provider": "anthropic",
          "model_name": "claude-3-5-sonnet-20241022",
          "api_key_env_var": "ANTHROPIC_API_KEY"
        },
        "role": "debater",
        "name": "Economist",
        "stance": "Con",
        "system_prompt": "You argue that economic challenges are more pressing than climate.",
        "temperature": 1.0,
        "max_tokens": 1024
      }
    ],
    "judge_config": {
      "agent_id": "judge",
      "llm_config": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "api_key_env_var": "ANTHROPIC_API_KEY"
      },
      "role": "judge",
      "name": "Judge",
      "stance": "Neutral",
      "system_prompt": "You are an impartial judge evaluating debate arguments.",
      "temperature": 0.7,
      "max_tokens": 2048
    }
  }
}
EOF

# Response:
# {
#   "debate_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "created",
#   "message": "Debate created successfully"
# }

# 2. Connect to WebSocket for real-time updates
# (In another terminal)
wscat -c ws://localhost:8000/api/ws/550e8400-e29b-41d4-a716-446655440000

# 3. Start the debate
curl -X POST http://localhost:8000/api/debates/550e8400-e29b-41d4-a716-446655440000/start

# 4. Watch real-time updates in WebSocket connection
# Events will stream as the debate progresses

# 5. Export the transcript
curl http://localhost:8000/api/debates/550e8400-e29b-41d4-a716-446655440000/export?format=markdown > debate.md
```

---

## Test Coverage Summary

**Total:** 150 tests, 97% coverage

| Module | Coverage |
|--------|----------|
| models/ | 97% |
| services/ | 95% |
| routers/debates.py | 97% |
| routers/websocket.py | 91% |
| storage/ | 100% |

**Test Categories:**
- Unit tests: Models, LLM clients, prompt builder, storage
- Integration tests: Full debate lifecycle, agent orchestration
- API tests: REST endpoints, WebSocket events
- Edge case tests: 10+ agents, invalid inputs, API failures, concurrent access
