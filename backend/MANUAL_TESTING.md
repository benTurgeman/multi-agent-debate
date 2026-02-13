# Manual Testing Guide

This guide walks you through manually testing the Multi-Agent Debate Engine API.

## Quick Start with Test Scripts

For the easiest way to test with real LLM APIs, use the automated test scripts:

```bash
# 2-agent debate
python manual_tests/test_2_agent_debate.py

# 3-agent debate (mixed Claude + GPT-4)
python manual_tests/test_3_agent_debate.py

# 5-agent debate (complex scenario)
python manual_tests/test_5_agent_debate.py
```

See [manual_tests/README.md](./manual_tests/README.md) for detailed documentation.

**For manual curl + WebSocket testing, continue below:**

## Prerequisites

1. **Set up environment variables:**

Create a `.env` file in the `backend/` directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your API keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
```

2. **Install dependencies:**

```bash
poetry install
```

3. **Start the server:**

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at `http://localhost:8000`

---

## Testing Workflow

### 1. Health Check

Verify the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","service":"Multi-Agent Debate Engine"}
```

---

### 2. Create a Debate

Create a 2-agent debate:

```bash
curl -X POST http://localhost:8000/api/debates \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "topic": "AI will benefit humanity more than harm it",
      "num_rounds": 2,
      "agents": [
        {
          "agent_id": "optimist",
          "llm_config": {
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
          "llm_config": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key_env_var": "ANTHROPIC_API_KEY"
          },
          "role": "debater",
          "name": "AI Skeptic",
          "stance": "Con",
          "system_prompt": "You are a cautious critic who worries about AI risks and unintended consequences.",
          "temperature": 0.9,
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
        "name": "Impartial Judge",
        "stance": "Neutral",
        "system_prompt": "You are a fair debate judge evaluating arguments objectively.",
        "temperature": 0.7,
        "max_tokens": 2048
      }
    }
  }'
```

Save the `debate_id` from the response:
```json
{
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "created",
  "message": "Debate created successfully"
}
```

---

### 3. Create a 3-Agent Debate (Mixed Models)

Test with multiple agents and mixed LLM providers:

```bash
curl -X POST http://localhost:8000/api/debates \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "topic": "Remote work is better than office work",
      "num_rounds": 2,
      "agents": [
        {
          "agent_id": "remote_advocate",
          "llm_config": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key_env_var": "ANTHROPIC_API_KEY"
          },
          "role": "debater",
          "name": "Remote Work Advocate",
          "stance": "Pro",
          "system_prompt": "You strongly support remote work for flexibility and productivity.",
          "temperature": 1.0,
          "max_tokens": 800
        },
        {
          "agent_id": "office_advocate",
          "llm_config": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "api_key_env_var": "OPENAI_API_KEY"
          },
          "role": "debater",
          "name": "Office Work Advocate",
          "stance": "Con",
          "system_prompt": "You believe office work is essential for collaboration and culture.",
          "temperature": 0.9,
          "max_tokens": 800
        },
        {
          "agent_id": "pragmatist",
          "llm_config": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key_env_var": "ANTHROPIC_API_KEY"
          },
          "role": "debater",
          "name": "Pragmatist",
          "stance": "Neutral",
          "system_prompt": "You see benefits to both approaches and seek balanced solutions.",
          "temperature": 1.0,
          "max_tokens": 800
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
        "system_prompt": "You are a fair debate judge.",
        "temperature": 0.7,
        "max_tokens": 2048
      }
    }
  }'
```

---

### 4. List All Debates

```bash
curl http://localhost:8000/api/debates
```

This will show all created debates with their current status.

---

### 5. Get Debate Details

Replace `{DEBATE_ID}` with the actual ID:

```bash
curl http://localhost:8000/api/debates/{DEBATE_ID}
```

---

### 6. Get Debate Status

Check the current state without full details:

```bash
curl http://localhost:8000/api/debates/{DEBATE_ID}/status
```

---

### 7. Connect to WebSocket (Optional)

If you have `wscat` installed:

```bash
# Install wscat if needed
npm install -g wscat

# Connect to debate
wscat -c ws://localhost:8000/api/ws/{DEBATE_ID}
```

You'll see real-time updates as the debate progresses.

---

### 8. Start the Debate

**Important:** Start the debate AFTER connecting to WebSocket if you want to see real-time updates.

```bash
curl -X POST http://localhost:8000/api/debates/{DEBATE_ID}/start
```

The debate will run in the background. Watch the WebSocket for real-time updates, or poll the status endpoint.

Expected response:
```json
{
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "message": "Debate execution started. Connect to WebSocket for real-time updates."
}
```

---

### 9. Monitor Progress

**Option A: WebSocket** (real-time)
- If connected via `wscat`, you'll see events as they happen

**Option B: Polling** (REST)
```bash
# Poll status every few seconds
while true; do
  curl http://localhost:8000/api/debates/{DEBATE_ID}/status
  sleep 2
done
```

---

### 10. Export Debate Transcript

After the debate completes, export in various formats:

**JSON:**
```bash
curl http://localhost:8000/api/debates/{DEBATE_ID}/export?format=json
```

**Markdown:**
```bash
curl http://localhost:8000/api/debates/{DEBATE_ID}/export?format=markdown > debate.md
```

**Plain Text:**
```bash
curl http://localhost:8000/api/debates/{DEBATE_ID}/export?format=text > debate.txt
```

---

### 11. View Full Debate Results

Get complete debate including judge's decision:

```bash
curl http://localhost:8000/api/debates/{DEBATE_ID} | jq .
```

Look for:
- `judge_result.winner_name`: Who won
- `judge_result.agent_scores`: Scores for each participant
- `judge_result.summary`: Judge's overall analysis
- `history`: All messages from the debate

---

### 12. Delete a Debate

Clean up when done:

```bash
curl -X DELETE http://localhost:8000/api/debates/{DEBATE_ID}
```

---

## Testing Edge Cases

### Test Invalid Input

**Create debate with only 1 agent (should fail):**
```bash
curl -X POST http://localhost:8000/api/debates \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "topic": "Test",
      "num_rounds": 1,
      "agents": [
        {
          "agent_id": "agent1",
          "llm_config": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key_env_var": "ANTHROPIC_API_KEY"
          },
          "role": "debater",
          "name": "Agent 1",
          "stance": "Pro",
          "system_prompt": "Test",
          "temperature": 1.0,
          "max_tokens": 1024
        }
      ],
      "judge_config": {...}
    }
  }'
```

Expected: 422 Validation Error (minimum 2 agents required)

### Test Non-Existent Debate

```bash
curl http://localhost:8000/api/debates/nonexistent-id
```

Expected: 404 Not Found

### Test Starting Already Running Debate

```bash
# Start debate
curl -X POST http://localhost:8000/api/debates/{DEBATE_ID}/start

# Try to start again immediately
curl -X POST http://localhost:8000/api/debates/{DEBATE_ID}/start
```

Expected: 400 Bad Request (already in progress)

---

## Sample Output

### Successful Debate Completion

After a 2-agent, 2-round debate completes, the full response will include:

```json
{
  "debate": {
    "debate_id": "...",
    "status": "completed",
    "current_round": 2,
    "history": [
      {
        "agent_name": "Tech Optimist",
        "content": "AI represents humanity's best hope for solving climate change...",
        "round_number": 1,
        "turn_number": 0
      },
      {
        "agent_name": "AI Skeptic",
        "content": "While AI has potential, we must consider the risks...",
        "round_number": 1,
        "turn_number": 1
      },
      ...
    ],
    "judge_result": {
      "winner_name": "Tech Optimist",
      "summary": "The Pro side presented more compelling evidence...",
      "agent_scores": [
        {
          "agent_name": "Tech Optimist",
          "score": 8.5,
          "reasoning": "Strong logical arguments with concrete examples"
        },
        {
          "agent_name": "AI Skeptic",
          "score": 7.8,
          "reasoning": "Valid concerns but less supported by data"
        }
      ]
    }
  }
}
```

---

## Troubleshooting

### Server won't start
- Check Python version (requires 3.12+)
- Run `poetry install` to install dependencies
- Check for port conflicts on 8000

### API key errors
- Verify `.env` file exists in `backend/` directory
- Check API key names match exactly: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
- Ensure keys are valid and have sufficient credits

### Debate fails mid-execution
- Check server logs for detailed error messages
- Verify API rate limits haven't been exceeded
- Ensure all agents use valid model names

### WebSocket connection fails
- Ensure debate exists before connecting
- Check firewall settings
- Verify WebSocket client supports the protocol

---

## Performance Notes

**Typical Timing (2 agents, 2 rounds):**
- Debate creation: < 100ms
- Each agent turn: 2-5 seconds
- Judge evaluation: 3-7 seconds
- Total debate time: 20-40 seconds

**For 3+ agents:**
- Time increases linearly with number of agents
- Example: 3 agents, 3 rounds = ~60-90 seconds

**Rate limiting:**
- 1 second delay between turns
- Consider provider API limits when running multiple debates
