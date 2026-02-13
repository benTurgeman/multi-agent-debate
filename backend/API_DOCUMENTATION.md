# Multi-Agent Debate Engine - API Documentation

## Overview

The Multi-Agent Debate Engine provides a REST API for creating and managing AI-powered debates, plus a WebSocket interface for real-time updates.

**Base URL:** `http://localhost:8000`

---

## REST API Endpoints

### Health Check

**GET** `/health`

Check if the server is running.

**Response:**
```json
{
  "status": "ok",
  "service": "Multi-Agent Debate Engine"
}
```

---

### Create Debate

**POST** `/api/debates`

Create a new debate with specified configuration.

**Request Body:**
```json
{
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
        "system_prompt": "You are a cautious critic who worries about AI risks.",
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
}
```

**Response (201 Created):**
```json
{
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "created",
  "message": "Debate created successfully"
}
```

---

### List All Debates

**GET** `/api/debates`

Retrieve all debates.

**Response (200 OK):**
```json
{
  "debates": [
    {
      "debate_id": "550e8400-e29b-41d4-a716-446655440000",
      "config": { ... },
      "status": "completed",
      "current_round": 2,
      "current_turn": 1,
      "history": [ ... ],
      "judge_result": { ... },
      "created_at": "2026-02-13T10:00:00Z",
      "started_at": "2026-02-13T10:01:00Z",
      "completed_at": "2026-02-13T10:05:00Z"
    }
  ],
  "total": 1
}
```

---

### Get Debate

**GET** `/api/debates/{debate_id}`

Retrieve a specific debate by ID.

**Response (200 OK):**
```json
{
  "debate": {
    "debate_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": { ... },
    "status": "completed",
    "current_round": 2,
    "current_turn": 1,
    "history": [
      {
        "message_id": "msg-1",
        "agent_id": "optimist",
        "agent_name": "Tech Optimist",
        "agent_stance": "Pro",
        "round_number": 1,
        "turn_number": 0,
        "content": "AI has the potential to...",
        "timestamp": "2026-02-13T10:01:15Z"
      }
    ],
    "judge_result": {
      "summary": "Both participants presented strong arguments...",
      "agent_scores": [
        {
          "agent_id": "optimist",
          "agent_name": "Tech Optimist",
          "score": 8.5,
          "reasoning": "Strong logical arguments and evidence"
        }
      ],
      "winner_id": "optimist",
      "winner_name": "Tech Optimist",
      "key_arguments": ["AI medical breakthroughs", "Climate modeling"]
    }
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Debate with ID {debate_id} not found"
}
```

---

### Start Debate

**POST** `/api/debates/{debate_id}/start`

Start debate execution in the background. The debate will run asynchronously.

**Response (202 Accepted):**
```json
{
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "message": "Debate execution started. Connect to WebSocket for real-time updates."
}
```

**Error Responses:**

- **404 Not Found:** Debate doesn't exist
- **400 Bad Request:** Debate already in progress or completed

---

### Get Debate Status

**GET** `/api/debates/{debate_id}/status`

Get current status of a debate.

**Response (200 OK):**
```json
{
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "current_round": 1,
  "current_turn": 0,
  "total_rounds": 2,
  "message_count": 3
}
```

---

### Export Debate

**GET** `/api/debates/{debate_id}/export?format={format}`

Export debate transcript in various formats.

**Query Parameters:**
- `format`: `json` (default), `markdown`, or `text`

**Response (200 OK):**

**JSON format:**
```json
{
  "debate": { ... }
}
```

**Markdown format:**
```markdown
# Debate: AI will benefit humanity more than harm it

**Date:** 2026-02-13T10:00:00Z
**Rounds:** 2
**Status:** completed

## Participants

- **Tech Optimist** (Pro)
  - Model: anthropic/claude-3-5-sonnet-20241022
  - Role: debater

...
```

**Text format:**
```text
DEBATE: AI will benefit humanity more than harm it
================================================================================

Date: 2026-02-13T10:00:00Z
Rounds: 2
Status: completed

...
```

---

### Delete Debate

**DELETE** `/api/debates/{debate_id}`

Delete a debate.

**Response (204 No Content)**

**Error Response (404 Not Found):**
```json
{
  "error": "Debate with ID {debate_id} not found"
}
```

---

## WebSocket API

### Connect to Debate

**WS** `/api/ws/{debate_id}`

Establish WebSocket connection for real-time debate updates.

**Connection Established Message:**
```json
{
  "type": "connection_established",
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "payload": {
    "status": "created",
    "current_round": 0,
    "current_turn": 0,
    "message_count": 0
  },
  "timestamp": "2026-02-13T10:00:00Z"
}
```

### Event Types

The WebSocket will broadcast the following event types during debate execution:

#### 1. Debate Started
```json
{
  "type": "debate_started",
  "debate_id": "...",
  "payload": {
    "topic": "AI will benefit humanity more than harm it",
    "num_rounds": 2,
    "num_agents": 2
  },
  "timestamp": "2026-02-13T10:01:00Z"
}
```

#### 2. Round Started
```json
{
  "type": "round_started",
  "debate_id": "...",
  "payload": {
    "round_number": 1
  },
  "timestamp": "2026-02-13T10:01:05Z"
}
```

#### 3. Agent Thinking
```json
{
  "type": "agent_thinking",
  "debate_id": "...",
  "payload": {
    "agent_id": "optimist",
    "agent_name": "Tech Optimist",
    "round_number": 1,
    "turn_number": 0
  },
  "timestamp": "2026-02-13T10:01:10Z"
}
```

#### 4. Message Received
```json
{
  "type": "message_received",
  "debate_id": "...",
  "payload": {
    "message": {
      "message_id": "msg-1",
      "agent_id": "optimist",
      "agent_name": "Tech Optimist",
      "agent_stance": "Pro",
      "round_number": 1,
      "turn_number": 0,
      "content": "AI has the potential to revolutionize...",
      "timestamp": "2026-02-13T10:01:15Z"
    }
  },
  "timestamp": "2026-02-13T10:01:15Z"
}
```

#### 5. Turn Complete
```json
{
  "type": "turn_complete",
  "debate_id": "...",
  "payload": {
    "round_number": 1,
    "turn_number": 0,
    "agent_id": "optimist"
  },
  "timestamp": "2026-02-13T10:01:16Z"
}
```

#### 6. Round Complete
```json
{
  "type": "round_complete",
  "debate_id": "...",
  "payload": {
    "round_number": 1
  },
  "timestamp": "2026-02-13T10:02:30Z"
}
```

#### 7. Judging Started
```json
{
  "type": "judging_started",
  "debate_id": "...",
  "payload": {
    "total_messages": 4
  },
  "timestamp": "2026-02-13T10:03:00Z"
}
```

#### 8. Judge Result
```json
{
  "type": "judge_result",
  "debate_id": "...",
  "payload": {
    "judge_result": {
      "summary": "Both participants presented compelling arguments...",
      "agent_scores": [...],
      "winner_id": "optimist",
      "winner_name": "Tech Optimist",
      "key_arguments": [...]
    }
  },
  "timestamp": "2026-02-13T10:03:30Z"
}
```

#### 9. Debate Complete
```json
{
  "type": "debate_complete",
  "debate_id": "...",
  "payload": {
    "winner_id": "optimist",
    "winner_name": "Tech Optimist",
    "total_messages": 4
  },
  "timestamp": "2026-02-13T10:03:35Z"
}
```

#### 10. Error
```json
{
  "type": "error",
  "debate_id": "...",
  "payload": {
    "error_message": "Failed to invoke judge: API error",
    "error_type": "DebateExecutionError"
  },
  "timestamp": "2026-02-13T10:03:00Z"
}
```

### Client-to-Server Messages

#### Ping/Pong for Keep-Alive

Send:
```json
{
  "type": "ping"
}
```

Receive:
```json
{
  "type": "pong",
  "timestamp": "2026-02-13T10:00:00Z"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Request accepted for processing |
| 204 | No Content - Success with no response body |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

---

## Data Models

### Model Providers

- `anthropic` - Claude models (Anthropic API)
- `openai` - GPT models (OpenAI API)

### Agent Roles

- `debater` - Participant in the debate
- `judge` - Evaluates debate and declares winner

### Debate Status

- `created` - Debate created but not started
- `in_progress` - Debate is currently running
- `completed` - Debate finished successfully
- `failed` - Debate execution failed

---

## Error Handling

All errors return a consistent format:

```json
{
  "error": "Human-readable error message",
  "detail": "Additional error details (optional)"
}
```

Common error scenarios:
- Missing API keys: Ensure environment variables are set
- Invalid debate ID: Check the ID exists
- Debate already in progress: Cannot start the same debate twice
- Validation errors: Check request payload matches schema

---

## Rate Limiting

The system includes built-in rate limiting protection:
- 1 second delay between agent turns
- Exponential backoff retry (3 attempts) for LLM API errors
- Consider provider-specific rate limits (Anthropic: ~50 req/min, OpenAI: varies by tier)

---

## Examples

See the `Manual Testing` section in the main README for complete curl examples and testing workflows.
