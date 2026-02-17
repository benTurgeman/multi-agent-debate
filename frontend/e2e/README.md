# E2E Tests for Multi-Agent Debate System

Comprehensive end-to-end tests using Playwright to validate the complete debate flow.

## Prerequisites

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

### 2. Start Ollama Service

```bash
ollama serve
```

### 3. Pull Required Models

```bash
# Pull Mistral 7B (recommended for tests)
ollama pull mistral

# Optional: Pull other models
ollama pull llama3.2:3b
```

### 4. Verify Ollama is Running

```bash
curl http://localhost:11434/api/tags
```

## Running Tests

### Run All Tests

```bash
cd frontend
npm run test:e2e
```

### Run Tests with UI Mode (Recommended for Development)

```bash
npm run test:e2e:ui
```

This opens Playwright's interactive UI where you can:
- Watch tests run in real-time
- Debug failures
- See browser interactions
- Inspect element selectors

### Run Tests in Headed Mode (See Browser)

```bash
npm run test:e2e:headed
```

### Debug Specific Test

```bash
npm run test:e2e:debug
```

### Run Specific Test File

```bash
npx playwright test debate-flow.spec.ts
```

### Run Specific Test Case

```bash
npx playwright test -g "Complete debate flow"
```

## Test Structure

```
e2e/
├── README.md                 # This file
├── debate-flow.spec.ts       # Main E2E test suite
└── helpers/
    ├── ollama-checker.ts     # Ollama availability verification
    └── debate-helpers.ts     # Reusable test utilities
```

## Test Suites

### 1. Complete Debate Flow
Tests the full debate lifecycle:
- Configuration phase (topic, agents, judge, rounds)
- Debate execution (multiple rounds, agent responses)
- Completion phase (winner declaration, export functionality)

**Duration**: ~90-120 seconds

### 2. UI State Updates
Verifies that UI elements update correctly as debate progresses:
- Status transitions (Created → In Progress → Completed)
- Participant status updates
- Message count increments

**Duration**: ~60-90 seconds

### 3. Error Handling
Tests error scenarios:
- Invalid configuration (missing required fields)
- Disabled button states

**Duration**: ~5 seconds

### 4. Export Functionality
Validates debate export features:
- Export button appears after completion
- Export button is functional

**Duration**: ~60-90 seconds

## Configuration

Test configuration can be modified in `debate-flow.spec.ts`:

```typescript
const TEST_CONFIG = {
  topic: 'Should AI be regulated by governments?',
  rounds: 2,
  provider: 'Ollama',
  model: 'Mistral 7B',
  judgeModel: 'Mistral 7B (Ollama)',
  agent1Name: 'Pro Agent',
  agent1Stance: 'Pro',
  agent2Name: 'Con Agent',
  agent2Stance: 'Con',
  expectedRuntime: 90000,
};
```

## Troubleshooting

### Tests Timeout

If tests timeout, it's usually because:
1. **Ollama not running**: Start Ollama with `ollama serve`
2. **Model not available**: Pull model with `ollama pull mistral`
3. **Backend not running**: Tests auto-start backend, but ensure Poetry is installed
4. **Slow model responses**: Increase timeout in test or use faster model

### Selector Not Found

If selectors fail:
1. Run test with `--headed` to see browser
2. Use UI mode (`npm run test:e2e:ui`) to debug selectors
3. Check that frontend is built correctly
4. Verify element IDs haven't changed in UI

### WebSocket Connection Failed

If WebSocket fails:
1. Check backend is running on port 8000
2. Check frontend is running on port 5173
3. Verify CORS settings in `backend/main.py`
4. Check browser console for errors

### Judge Response Parsing Failure

If judge fails to provide verdict:
1. This is handled gracefully by the backend
2. Test should still pass as backend extracts partial results
3. Check console logs for details

## CI/CD Integration

To run tests in CI/CD:

1. **Install Ollama in CI**:
```yaml
- name: Install Ollama
  run: curl -fsSL https://ollama.ai/install.sh | sh

- name: Start Ollama
  run: ollama serve &

- name: Pull Models
  run: ollama pull mistral
```

2. **Run Tests**:
```yaml
- name: Run E2E Tests
  run: |
    cd frontend
    npm run test:e2e
```

## Debugging Tips

1. **Enable debug mode**: Set `DEBUG=true` to see console logs
2. **Take screenshots**: Screenshots are automatically saved on failure
3. **Record videos**: Videos are recorded for failed tests
4. **Inspect traces**: Use `npx playwright show-trace` to view traces
5. **Check console logs**: Test helper captures all console output

## Writing New Tests

When adding new tests:

1. Import helper utilities from `./helpers/`
2. Use `verifyTestPrerequisites()` in `beforeAll` to check Ollama
3. Follow existing test structure for consistency
4. Use meaningful test descriptions
5. Add console.log statements for progress tracking
6. Handle async operations properly
7. Use appropriate timeouts for LLM operations

Example:

```typescript
test('My new test', async ({ page }) => {
  // Capture console logs
  const logs = captureConsoleLogs(page);

  // Navigate
  await page.goto('/');

  // Perform actions
  // ...

  // Verify results
  await expect(/* ... */).toBeVisible();

  console.log('✓ Test completed');
});
```

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Ollama Documentation](https://ollama.ai/docs)
- [Project Architecture](../../backend/ARCHITECTURE.md)
- [Frontend README](../README.md)
