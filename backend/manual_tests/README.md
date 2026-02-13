# Manual Testing Scripts for Real LLM APIs

These scripts test the debate system with actual LLM API calls. They require valid API keys and will consume API credits.

## Setup

1. **Set API Keys in `.env` file:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   OPENAI_API_KEY=sk-...  # Only needed for 3-agent test
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

## Test Scripts

### 1. Two-Agent Debate (`test_2_agent_debate.py`)

Tests a simple 2-agent debate using only Anthropic's Claude.

**Topic:** "Artificial Intelligence will benefit humanity more than harm it"

**Participants:**
- Tech Optimist (Pro) - Claude 3.5 Sonnet
- AI Skeptic (Con) - Claude 3.5 Sonnet

**Rounds:** 2

**Run:**
```bash
python manual_tests/test_2_agent_debate.py
```

**Expected Duration:** ~30-60 seconds
**API Calls:** ~5 (2 rounds × 2 agents + judge)

---

### 2. Three-Agent Debate (`test_3_agent_debate.py`)

Tests a 3-agent debate with **mixed models** (Claude + GPT-4).

**Topic:** "Should governments implement universal basic income?"

**Participants:**
- UBI Advocate (Pro) - Claude 3.5 Sonnet
- UBI Critic (Con) - **GPT-4o (OpenAI)**
- Pragmatist (Neutral) - Claude 3.5 Sonnet

**Rounds:** 2

**Run:**
```bash
python manual_tests/test_3_agent_debate.py
```

**Expected Duration:** ~45-90 seconds
**API Calls:** ~7 (2 rounds × 3 agents + judge)
**Requirements:** Both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`

---

### 3. Five-Agent Debate (`test_5_agent_debate.py`)

Tests a complex 5-agent debate with diverse perspectives.

**Topic:** "What is the most important challenge facing humanity in the next 50 years?"

**Participants:**
- Climate Scientist - Climate Change
- AI Researcher - AI Alignment
- Global Health Expert - Pandemic Preparedness
- Development Economist - Economic Inequality
- Political Scientist - Democratic Erosion

**Rounds:** 2

**Run:**
```bash
python manual_tests/test_5_agent_debate.py
```

**Expected Duration:** ~2-3 minutes
**API Calls:** ~11 (2 rounds × 5 agents + judge)
**Note:** This test requires more time and API credits due to 10 agent turns + judging.

---

## What to Verify

When running these tests, verify:

✅ **Debate Execution:**
- All rounds complete successfully
- Agents take turns in correct order
- Each agent sees full history of previous turns

✅ **Real-time Events:**
- Progress updates display correctly
- Messages appear in real-time
- Error handling works gracefully

✅ **Judge Evaluation:**
- Judge receives all messages
- Scores are 0-10 floats
- Winner is declared
- Reasoning is provided for each score

✅ **Mixed Model Support (3-agent test):**
- Claude and OpenAI models work together
- No errors switching between providers
- Responses are coherent and contextual

✅ **Error Handling:**
- Retries work on temporary API failures
- Clear error messages on permanent failures
- Graceful degradation

---

## Troubleshooting

**"API key not set" error:**
- Ensure `.env` file exists in `backend/` directory
- Check that API key variable names match exactly
- Verify API keys are valid

**Rate limiting errors:**
- Add delays between tests
- Check API tier limits (Anthropic/OpenAI)
- Wait a minute and retry

**Debate fails mid-execution:**
- Check API credit balance
- Review error messages in output
- Check `backend/logs/` for detailed logs

**Timeout errors:**
- Increase timeout in `core/config.py` if needed
- Check internet connection
- Verify API service status

---

## Cost Estimation

Approximate costs per test (as of 2025):

| Test | API Calls | Estimated Cost |
|------|-----------|----------------|
| 2-agent | ~5 | $0.01 - $0.05 |
| 3-agent | ~7 | $0.02 - $0.08 |
| 5-agent | ~11 | $0.05 - $0.15 |

*Costs vary based on response lengths and model pricing. These are rough estimates.*

---

## Next Steps

After successful manual testing:

1. ✅ Verify debate transcripts are coherent
2. ✅ Test export functionality:
   ```python
   # In script, after debate completes:
   from routers.debates import _export_markdown, _export_text
   markdown = _export_markdown(result)
   print(markdown)
   ```

3. ✅ Test WebSocket integration (separate frontend testing)

4. ✅ Performance testing with longer debates (5+ rounds)

5. ✅ Stress testing with more agents (8-10 agents)
