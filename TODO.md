# TODO - Multi-Agent Debate System

## Remaining Issues from E2E Testing (2026-02-17)

### Issue #2: Round Display Off-by-One Error
**Priority**: Medium
**Status**: Not Started
**Location**: Frontend - likely in debate state management or UI components

**Problem**:
- UI displays incorrect round numbers (e.g., "Round 3 of 2" or "Round 4 of 3")
- Backend logs show correct round numbers (1, 2, 3)
- Suggests frontend is adding 1 to the round number somewhere

**Evidence**:
- WebSocket logs show: "Round started: 1", "Round started: 2"
- UI shows: "Round 2 of 3", "Round 3 of 3", "Round 4 of 3"

**Investigation Steps**:
1. Check `src/hooks/useDebateWebSocket.ts` - how it processes `round_started` events
2. Check debate state reducer/context - how it stores current round
3. Check UI components that display round numbers
4. Look for any `currentRound + 1` or similar logic

**Files to Check**:
- `frontend/src/hooks/useDebateWebSocket.ts`
- `frontend/src/components/organisms/DebateView/` (or similar)
- Any state management files handling debate rounds

---

### Issue #3: Missing WebSocket Event Handlers
**Priority**: Low
**Status**: Not Started
**Location**: `frontend/src/hooks/useDebateWebSocket.ts`

**Problem**:
Frontend doesn't handle these WebSocket message types, logging "Unknown message type":
- `turn_complete`
- `round_complete`
- `judging_started`

**Impact**:
- Events are received but not processed
- No UI feedback for these transitions
- Users don't see visual indicators for turn/round completion or judging start

**Evidence**:
Console logs show:
```
[LOG] [useDebateWebSocket] Unknown message type: turn_complete
[LOG] [useDebateWebSocket] Unknown message type: round_complete
[LOG] [useDebateWebSocket] Unknown message type: judging_started
```

**Implementation Plan**:
1. Add handlers in `useDebateWebSocket.ts` for these event types
2. Update debate state to reflect these transitions
3. Add UI feedback (optional):
   - Show "Turn completed" indicator
   - Show "Round completed" summary
   - Show "Judge is evaluating..." during judging

**Files to Modify**:
- `frontend/src/hooks/useDebateWebSocket.ts`
- Possibly UI components if visual feedback is desired

---

## Completed Issues ✅

### Issue #1: CORS Configuration ✅
**Status**: Fixed in commit b802e93
- Added port 5174 to allowed origins in `backend/main.py`

### Issue #4: Judge Response Parsing Failure ✅ (CRITICAL)
**Status**: Fixed in commit b802e93
- Added ValidationError handling for incomplete judge JSON responses
- Intelligently extracts partial data and fills missing fields
- Determines winner from highest score if winner_id not provided

### Issue #5: Judge Model Selection UX Bug ✅
**Status**: Fixed in commit b802e93
- Fixed string splitting for model IDs containing colons (e.g., `ollama:mistral:7b`)
- Changed from `.split(':')` to `.indexOf()` and `.substring()` approach

---

## E2E Test Plan

### Test Scope
Create a comprehensive Playwright-based e2e test that validates the complete debate flow using only local Ollama models.

### Test Configuration
- **Models**: Ollama Mistral 7B for all participants and judge
- **Rounds**: 2 (for faster execution)
- **Topic**: "Should AI be regulated by governments?" (or parameterizable)
- **Agents**: 2 agents (Pro and Con stances)
- **Runtime**: ~30-60 seconds expected

### Test Structure

```javascript
// e2e/debate-flow.spec.js

describe('Multi-Agent Debate - Full Flow', () => {

  beforeAll(async () => {
    // Verify Ollama is running and models are available
    // Check mistral:7b is pulled
  });

  test('Complete debate flow with Ollama models', async () => {
    // 1. Configuration Phase
    //    - Fill debate topic
    //    - Add Pro agent (Ollama Mistral)
    //    - Add Con agent (Ollama Mistral)
    //    - Set rounds to 2
    //    - Select judge model (Ollama Mistral)
    //    - Verify "Create Debate" button is enabled

    // 2. Debate Execution Phase
    //    - Click "Create Debate"
    //    - Verify WebSocket connection established
    //    - Verify "debate_started" event received
    //    - Verify round 1 starts
    //    - Wait for first agent message
    //    - Wait for second agent message
    //    - Verify round 2 starts
    //    - Wait for round 2 messages
    //    - Verify "judging_started" event

    // 3. Completion Phase
    //    - Wait for "judge_result" event
    //    - Wait for "debate_complete" event
    //    - Verify status shows "Debate Complete"
    //    - Verify winner is declared
    //    - Verify all agents show "Completed" status
    //    - Verify "Export Results" button appears
  });

  test('WebSocket events are received in correct order', async () => {
    // Track all WebSocket events and verify sequence:
    // 1. connection_established
    // 2. debate_started
    // 3. round_started (round 1)
    // 4. agent_thinking (agent 1)
    // 5. message_received (agent 1)
    // 6. turn_complete
    // 7. agent_thinking (agent 2)
    // 8. message_received (agent 2)
    // 9. turn_complete
    // 10. round_complete
    // 11. round_started (round 2)
    // ... repeat for round 2
    // N. judging_started
    // N+1. judge_result
    // N+2. debate_complete
  });

  test('UI state updates correctly during debate', async () => {
    // Verify UI elements update as debate progresses:
    // - Participant status (Waiting, Thinking, Active, Completed)
    // - Message count increments
    // - Round indicator updates (after Issue #2 is fixed)
    // - Debate status (In Progress -> Debate Complete)
  });

  test('Error handling - Ollama not running', async () => {
    // Stop Ollama service temporarily
    // Attempt to create debate
    // Verify appropriate error message shown
    // Verify debate doesn't crash
  });

  test('Error handling - Invalid model selected', async () => {
    // Select a model that doesn't exist
    // Attempt to create debate
    // Verify error handling
  });
});
```

### Test Implementation Steps

1. **Setup**:
   - Install Playwright: `npm install -D @playwright/test`
   - Create `e2e/` directory
   - Configure Playwright for local testing
   - Add npm scripts for running tests

2. **Prerequisites**:
   - Document that Ollama must be running
   - Document that `mistral:7b` model must be pulled
   - Add health check script to verify Ollama availability

3. **Test Utilities**:
   - Create helper to wait for WebSocket events
   - Create helper to verify debate state transitions
   - Create helper to capture and verify console logs

4. **CI/CD Integration** (Future):
   - Add GitHub Actions workflow
   - Install Ollama in CI
   - Pull required models
   - Run e2e tests

### Expected Test Outcomes

After fixes are applied:
- ✅ All tests pass
- ✅ Round numbers display correctly
- ✅ All WebSocket events are handled
- ✅ Debate completes successfully with winner declared
- ✅ No console errors or warnings
- ✅ UI state reflects backend state accurately

### Files to Create

- `e2e/debate-flow.spec.js` - Main e2e test
- `e2e/helpers/debate-helpers.js` - Reusable test utilities
- `e2e/helpers/ollama-checker.js` - Ollama availability checker
- `playwright.config.js` - Playwright configuration
- `.github/workflows/e2e-tests.yml` - CI workflow (optional)

---

## Future Enhancements

### UI Improvements
- Show visual indicator when turn completes
- Show round summary when round completes
- Add loading spinner during judging phase
- Display judge scores and reasoning in UI

### Testing Improvements
- Add unit tests for judge response parsing
- Add integration tests for WebSocket events
- Add visual regression tests for UI components

### Performance Optimizations
- Implement debate history pagination for long debates
- Add message streaming for real-time typing effect
- Optimize WebSocket message frequency

### Feature Additions
- Export debate transcript to PDF
- Share debate results via URL
- Save debate configurations as templates
- Support for more than 2 agents
- Support for multi-turn rounds (agents respond multiple times per round)

---

## Notes

- All Ollama testing performed with `mistral:7b` and `llama3.2:3b` models
- Backend auto-reloads with `--reload` flag for development
- Frontend uses Vite HMR for instant updates
- CORS configured for ports 5173, 5174, and 3000
- WebSocket heartbeat pings occur every ~10 seconds
