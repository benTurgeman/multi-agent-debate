# Troubleshooting Guide

This guide helps diagnose and resolve common issues when working with the multi-agent debate system.

## Common Issues

### API Key Errors

**Symptoms:**
- `401 Unauthorized` or `403 Forbidden` errors
- Error message: "API key not set" or "Invalid API key"
- Debate fails to start or agents don't respond

**Common Causes:**
- Missing `.env` file in backend directory
- Incorrect API key format or value
- Expired or invalid API key
- Wrong environment variable name

**Solutions:**

1. **Verify `.env` file exists:**
   ```bash
   cd backend
   ls -la .env
   ```
   If missing, copy from example:
   ```bash
   cp .env.example .env
   ```

2. **Check variable names match exactly:**
   ```bash
   # Correct names:
   ANTHROPIC_API_KEY=sk-ant-api03-...
   OPENAI_API_KEY=sk-...
   ```

3. **Validate API key format:**
   - Anthropic keys start with `sk-ant-api03-`
   - OpenAI keys start with `sk-`
   - No quotes or extra spaces

4. **Test keys directly:**
   ```bash
   # Test Anthropic key
   python manual_tests/test_2_agent_debate.py

   # Test OpenAI key
   python manual_tests/test_3_agent_debate.py
   ```

5. **Check API key status:**
   - Visit provider console (console.anthropic.com or platform.openai.com)
   - Verify key is active and has usage quota

---

### Rate Limiting

**Symptoms:**
- `429 Too Many Requests` errors
- Error message: "Rate limit exceeded"
- Debate pauses or fails mid-execution

**Common Causes:**
- Provider-specific rate limits reached
- Too many concurrent requests
- Insufficient delay between API calls

**Provider Rate Limits:**
- **Anthropic:** ~50 requests/minute (varies by tier)
- **OpenAI:** Varies by tier (check platform.openai.com/settings)

**Solutions:**

1. **Wait and retry:**
   ```bash
   # Wait 60 seconds between test runs
   sleep 60 && python manual_tests/test_2_agent_debate.py
   ```

2. **Use different model tier:**
   - Switch to Claude Haiku for testing (lower cost, higher limits)
   - Use GPT-4o-mini instead of GPT-4o

   ```python
   # In debate config
   llm_config=LLMConfig(
       provider=ModelProvider.ANTHROPIC,
       model_name="claude-3-haiku-20240307",  # Haiku has higher limits
       api_key_env_var="ANTHROPIC_API_KEY"
   )
   ```

3. **Check usage dashboard:**
   - **Anthropic:** console.anthropic.com/settings/usage
   - **OpenAI:** platform.openai.com/usage

4. **Reduce concurrent debates:**
   - Run one debate at a time
   - Add delays between starting debates

5. **Built-in protection:**
   - System includes 1-second delay between agent turns
   - Automatic retry with exponential backoff (1s, 2s, 4s)

---

### WebSocket Connection Issues

**Symptoms:**
- Connection drops during debate
- No real-time updates received
- `WebSocket disconnected` errors
- Timeout errors on connection

**Common Causes:**
- Network timeout or instability
- Debate not in `RUNNING` state
- Invalid debate ID
- Frontend disconnected before debate started

**Solutions:**

1. **Verify debate status before connecting:**
   ```bash
   curl http://localhost:8000/api/debates/{debate_id}/status
   ```

   Expected response when ready:
   ```json
   {
     "debate_id": "...",
     "status": "running"
   }
   ```

2. **Check debate lifecycle:**
   - `PENDING` - Debate created but not started (WebSocket won't receive events)
   - `RUNNING` - Active debate (WebSocket receives events)
   - `JUDGING` - Judge evaluating (WebSocket receives judge events)
   - `COMPLETE` - Debate finished (no more events)

3. **Implement reconnection logic:**
   ```typescript
   // Frontend example
   const connectWithRetry = (debateId: string, maxRetries = 5) => {
     let retries = 0;
     const connect = () => {
       const ws = new WebSocket(`ws://localhost:8000/ws/${debateId}`);

       ws.onclose = () => {
         if (retries < maxRetries) {
           retries++;
           const delay = Math.min(1000 * Math.pow(2, retries), 30000);
           setTimeout(connect, delay);
         }
       };
     };
     connect();
   };
   ```

4. **Check WebSocket endpoint:**
   ```bash
   # Test WebSocket connection
   curl --include \
        --no-buffer \
        --header "Connection: Upgrade" \
        --header "Upgrade: websocket" \
        --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
        --header "Sec-WebSocket-Version: 13" \
        http://localhost:8000/ws/{debate_id}
   ```

5. **Network issues:**
   - Check firewall settings
   - Verify localhost/8000 is accessible
   - Try different port if 8000 is blocked

---

### LLM Response Errors

**Symptoms:**
- Empty or incomplete agent responses
- Malformed JSON in responses
- `500 Internal Server Error` during debate
- Agent turns fail repeatedly

**Common Causes:**
- Model context length exceeded
- Invalid or malformed prompt
- LLM API outage or degraded performance
- Model safety filters triggered

**Solutions:**

1. **Check model context limits:**
   - **Claude 3.5 Sonnet:** 200k tokens (~150k words)
   - **GPT-4o:** 128k tokens (~96k words)
   - **Claude Haiku:** 200k tokens

   Long debates (10+ rounds, 5+ agents) can exceed limits.

2. **Reduce debate complexity:**
   ```python
   # Limit rounds
   debate_config = DebateConfig(
       topic="...",
       agents=[...],
       num_rounds=2,  # Reduce from 5
   )
   ```

   ```python
   # Reduce agents
   agents = agents[:3]  # Use only first 3 agents
   ```

3. **Check provider status:**
   - **Anthropic:** status.anthropic.com
   - **OpenAI:** status.openai.com

   If degraded, wait or switch providers.

4. **Review prompt length:**
   ```python
   # Debug prompt size
   from services.prompt_builder import build_debater_prompt, format_history_for_context

   system_prompt = build_debater_prompt(agent, topic, round, total_rounds)
   context = format_history_for_context(history, topic, round, total_rounds)

   print(f"System prompt: {len(system_prompt)} chars")
   print(f"Context: {len(context)} chars")
   ```

5. **Check response validation:**
   - Ensure agent responses are plain text (no special formatting required)
   - Check logs for validation errors
   - Verify no empty responses

---

### Debate Fails to Start

**Symptoms:**
- `POST /api/debates/{id}/start` returns error
- Debate stays in `PENDING` state
- `400 Bad Request` or `404 Not Found` errors

**Common Causes:**
- Debate already started or completed
- Invalid debate ID
- Validation errors in debate config
- Missing required fields

**Solutions:**

1. **Check debate status:**
   ```bash
   curl http://localhost:8000/api/debates/{debate_id}
   ```

   If status is not `PENDING`, cannot start:
   ```json
   {
     "status": "running"  // Already started
   }
   ```

2. **Verify debate ID exists:**
   ```bash
   # List all debates
   curl http://localhost:8000/api/debates
   ```

3. **Check debate configuration:**
   - Minimum 2 agents required
   - All agents must have valid LLM configs
   - At least 1 round required
   - Topic must be non-empty

4. **Review validation errors:**
   ```json
   {
     "error": "Validation error",
     "detail": [
       {
         "loc": ["agents"],
         "msg": "ensure this value has at least 2 items",
         "type": "value_error"
       }
     ]
   }
   ```

---

### Database/Storage Errors

**Symptoms:**
- `500 Internal Server Error` on debate operations
- Debates not persisting
- Concurrent access errors

**Common Causes:**
- Memory store race conditions (rare)
- Invalid debate state
- Concurrent modifications

**Solutions:**

1. **Restart backend:**
   ```bash
   # Stop server (Ctrl+C)
   poetry run uvicorn main:app --reload
   ```

   Memory store resets on restart (in-memory storage).

2. **Check thread safety:**
   - System uses locks for concurrent access
   - Should handle multiple debates simultaneously
   - If issues persist, report as bug

3. **Verify debate state:**
   ```bash
   curl http://localhost:8000/api/debates/{debate_id}
   ```

   Ensure state is valid and consistent.

---

## Debugging Strategies

### Enable Debug Logging

Add to `main.py` or test scripts:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

This shows:
- API requests and responses
- LLM client interactions
- Debate state transitions
- Error stack traces

### Inspect Debate State

Get full debate details:

```bash
curl http://localhost:8000/api/debates/{debate_id} | jq
```

Check specific fields:
```bash
# Get status only
curl http://localhost:8000/api/debates/{debate_id}/status

# Count messages
curl http://localhost:8000/api/debates/{debate_id} | jq '.messages | length'

# Get last message
curl http://localhost:8000/api/debates/{debate_id} | jq '.messages[-1]'
```

### Test Individual Components

**Test LLM client directly:**
```python
from models.llm import LLMConfig, ModelProvider
from services.llm import create_llm_client

config = LLMConfig(
    provider=ModelProvider.ANTHROPIC,
    model_name="claude-3-5-sonnet-20241022",
    api_key_env_var="ANTHROPIC_API_KEY"
)

client = create_llm_client(config)
response = await client.send_message(
    system_prompt="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Say hello"}],
    temperature=1.0,
    max_tokens=100
)
print(response)
```

**Test prompt builder:**
```python
from services.prompt_builder import build_debater_prompt
from models.agent import AgentConfig, AgentRole

prompt = build_debater_prompt(
    agent=AgentConfig(...),
    topic="AI benefits humanity",
    current_round=1,
    total_rounds=3
)
print(prompt)
```

### Monitor API Usage

Check API usage to avoid unexpected bills:

- **Anthropic:** console.anthropic.com/settings/usage
- **OpenAI:** platform.openai.com/usage

Set budget alerts in provider console.

### Use Manual Test Scripts

Run controlled tests with known configurations:

```bash
# Simple 2-agent test
python manual_tests/test_2_agent_debate.py

# Mixed models (requires both API keys)
python manual_tests/test_3_agent_debate.py

# Complex 5-agent test
python manual_tests/test_5_agent_debate.py
```

See `manual_tests/README.md` for details.

---

## Error Codes Reference

### HTTP Status Codes

| Code | Meaning | Common Causes | Solution |
|------|---------|---------------|----------|
| 400 | Bad Request | Invalid debate config, missing fields, debate already started | Check request payload, verify debate state |
| 404 | Not Found | Debate ID doesn't exist | Verify debate ID, list all debates to confirm |
| 409 | Conflict | Debate already in progress or completed | Check debate status before starting |
| 422 | Validation Error | Invalid Pydantic model data, type mismatch | Review validation error details in response |
| 500 | Internal Server Error | LLM API failure, unexpected exception, rate limiting | Check logs, verify API keys, check provider status |

### Debate Status Values

| Status | Meaning | Next Actions |
|--------|---------|--------------|
| `PENDING` | Created, not started | Call `POST /api/debates/{id}/start` |
| `RUNNING` | Agents taking turns | Monitor via WebSocket or GET endpoint |
| `JUDGING` | Judge evaluating | Wait for completion |
| `COMPLETE` | Finished with results | View results, export transcript |
| `FAILED` | Error occurred | Check error details, review logs |

### WebSocket Event Types

| Event Type | When Sent | Contains |
|------------|-----------|----------|
| `DEBATE_STARTED` | Debate begins | Debate ID, config |
| `TURN_STARTED` | Agent starts turn | Agent ID, round, turn |
| `TURN_COMPLETED` | Agent finishes | Agent ID, message content |
| `DEBATE_JUDGING` | Judge evaluating | Judge config |
| `DEBATE_COMPLETE` | Debate finished | Final state, judge results |
| `ERROR` | Error occurs | Error message, details |

---

## Getting Help

If issues persist after trying these solutions:

1. **Check logs:** Enable debug logging and review output
2. **Verify configuration:** Ensure all settings match expected format
3. **Test components:** Isolate the failing component (LLM, debate, WebSocket)
4. **Review documentation:**
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [README.md](README.md) - Setup and usage
5. **Report bug:** Create issue with reproduction steps, logs, and configuration

---

**Last Updated:** 2024-02-13
