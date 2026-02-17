# TODO - Multi-Agent Debate System

## Remaining Issues from E2E Testing (2026-02-17)

_All issues have been resolved! See completed issues below._

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

### Issue #2: Round Display Off-by-One Error ✅
**Status**: Fixed in commit 4426a83
**Priority**: Medium
**Location**: `frontend/src/components/organisms/LiveDebate/index.tsx`

**Problem**:
- UI displayed incorrect round numbers (e.g., "Round 3 of 2" or "Round 4 of 3")
- Backend sends 1-indexed round numbers (1, 2, 3)
- Frontend incorrectly assumed 0-indexed and added +1

**Solution**:
- Removed the `+ 1` adjustment in LiveDebate component (line 64)
- Updated comment to reflect that backend sends 1-indexed round numbers
- Verified backend uses `range(1, num_rounds + 1)` in debate_manager.py

### Issue #3: Missing WebSocket Event Handlers ✅
**Status**: Fixed in commit 4426a83
**Priority**: Low
**Location**: `frontend/src/hooks/useDebateWebSocket.ts`

**Problem**:
Frontend didn't handle these WebSocket message types, logging "Unknown message type":
- `turn_complete`
- `round_complete`
- `judging_started`

**Solution**:
- Added handler for `TURN_COMPLETE` event - logs turn completion (informational)
- Added handler for `ROUND_COMPLETE` event - logs round completion (informational)
- Added handler for `JUDGING_STARTED` event - logs judging start (can be extended for UI feedback)
- Imported missing event type definitions from types/websocket
- All handlers properly typed and verified with TypeScript compilation

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
