# LLM Provider Unification: LiteLLM Integration

## Overview
Integrate LiteLLM to unify LLM provider integration, making it easy to add new providers (especially Ollama for local models) without writing provider-specific client code.

**Timeline:** 2-3 days
**Current Branch:** `feat/litellm-integration` (to be created)

---

## Phase 1: Add LiteLLM Dependency & Create Unified Client ✅

### ✅ 1.1 Add LiteLLM to dependencies
- [x] Add `litellm = "^1.56.0"` to `backend/pyproject.toml`
- [x] Run `cd backend && poetry add litellm`
- [x] Verify installation: `poetry show litellm`
- **Note:** Upgraded OpenAI to 2.x (required by LiteLLM), installed LiteLLM 1.81.13

### ✅ 1.2 Create LiteLLMClient
- [x] Create `backend/services/llm/litellm_client.py`
- [x] Implement `LiteLLMClient` class inheriting from `BaseLLMClient`
- [x] Add `__init__` with `model_name`, `api_key`, `api_base` parameters
- [x] Implement `send_message()` using `litellm.acompletion()`
- [x] Implement `get_provider_name()` to extract provider from model string
- [x] Add error handling with normalized error messages

---

## Phase 2: Update Configuration Models ✅

### ✅ 2.1 Update LLMConfig model
- [x] Open `backend/models/llm.py`
- [x] Change `provider` field from `ModelProvider` enum to `str`
- [x] Add `api_base: Optional[str] = None` field
- [x] Make `api_key_env_var` optional: `Optional[str] = None`
- [x] Add `litellm_model_name` property that returns `f"{provider}/{model_name}"`

### ✅ 2.2 Handle ModelProvider enum
- [x] **Option A:** Keep enum, add `OLLAMA = "ollama"` entry (backwards compatible)
- **Decision:** Implemented Option A for safer migration

---

## Phase 3: Simplify Factory ✅

### ✅ 3.1 Update factory.py
- [x] Open `backend/services/llm/factory.py`
- [x] Replace conditional logic with single LiteLLMClient instantiation
- [x] Make API key optional: use `get_api_key_optional()` if env var specified
- [x] Use `llm_config.litellm_model_name` for model parameter
- [x] Pass `api_base` to LiteLLMClient
- **Result:** Factory simplified from ~50 lines to ~25 lines, supports all providers

---

## Phase 4: Update Provider Catalog ✅

### ✅ 4.1 Add Ollama models
- [x] Open `backend/services/provider_catalog.py`
- [x] Add `ModelInfo` entries for:
  - `ollama/llama2` (Llama 2 7B)
  - `ollama/llama2:13b` (Llama 2 13B)
  - `ollama/mistral` (Mistral 7B)
- [x] Set `pricing_tier="free"` for all Ollama models
- [x] Set `recommended=False` (until validated)

---

## Phase 5: Update Tests ✅

### ✅ 5.1 Create new test file
- [x] Create `backend/tests/test_litellm_client.py`
- [x] Add test: `test_send_message_anthropic()` - mock `litellm.acompletion`
- [x] Add test: `test_send_message_openai()` - verify OpenAI format
- [x] Add test: `test_send_message_ollama()` - verify `api_base` passed correctly
- [x] Add test: `test_error_handling()` - verify exceptions normalized
- **Result:** Created comprehensive test suite with 16 tests covering all providers and error cases

### ✅ 5.2 Run test suite
- [x] Run: `poetry run pytest tests/test_litellm_client.py -v`
- [x] Run: `poetry run pytest tests/ -v` (verify all tests pass)
- [x] Fix any failing tests
- **Result:** All 166 tests passing (fixed export functions and updated factory tests)

---

## Phase 6: Documentation & Migration

### ☐ 6.1 Update README
- [ ] Add "Using Local Models (Ollama)" section to README
- [ ] Document Ollama setup: install, start server, pull models
- [ ] Add example `AgentConfig` with Ollama
- [ ] List supported local models

### ☐ 6.2 Update ARCHITECTURE.md
- [ ] Update LLM Integration section
- [ ] Document LiteLLM as unified gateway
- [ ] Explain provider format: `"provider/model_name"`
- [ ] Document how to add new providers (no code changes needed)

### ☐ 6.3 Optional: Feature flag for rollback
- [ ] Add `use_litellm: bool = True` to `backend/core/config.py`
- [ ] Update factory with conditional logic (LiteLLM vs legacy)
- [ ] Document rollback process

**Decision:** Implement feature flag for safer production rollout

---

## Phase 7: Cleanup (Optional, After Validation)

### ☐ 7.1 Remove old client files
- [ ] Delete `backend/services/llm/anthropic_client.py`
- [ ] Delete `backend/services/llm/openai_client.py`
- [ ] Update imports if needed

### ☐ 7.2 Remove old dependencies
- [ ] Run: `cd backend && poetry remove anthropic openai`
- [ ] Verify no other code depends on these SDKs

**Warning:** Only do this after 1-2 weeks of stable production usage

---

## Verification Checklist

### Unit Tests
- [ ] Run: `poetry run pytest tests/services/test_litellm_client.py -v`
- [ ] All tests pass

### Manual Testing: Cloud Providers
- [ ] Test Anthropic (Claude) - verify responses identical to before
- [ ] Test OpenAI (GPT-4o) - verify responses identical to before

### Manual Testing: Ollama (Local)
- [ ] Install Ollama: `brew install ollama` (macOS)
- [ ] Start Ollama: `ollama serve`
- [ ] Pull model: `ollama pull llama2`
- [ ] Test Ollama agent via API - verify response received

### Integration Testing
- [ ] Test mixed debate: Claude vs Ollama (cloud + local)
- [ ] Verify WebSocket messages received correctly
- [ ] Test frontend UI with Ollama agent

### Performance Monitoring
- [ ] Add latency logging to `litellm_client.py`
- [ ] Monitor: latency should be < 200ms overhead
- [ ] If > 200ms consistently, consider custom implementation

---

## Success Criteria

✅ All existing tests pass with LiteLLM
✅ Anthropic (Claude) agents work identically to before
✅ OpenAI (GPT) agents work identically to before
✅ Ollama agents successfully respond in debates
✅ Mixed provider debates (cloud + local) work
✅ WebSocket messages received correctly in frontend
✅ No regressions in debate functionality
✅ Documentation updated with Ollama setup instructions

---

## Rollback Plan

If issues arise:
1. **Immediate:** Set `use_litellm=false` in config (if feature flag implemented)
2. **Short-term:** Revert commits to restore old clients
3. **Long-term:** Consider custom abstraction if LiteLLM doesn't meet needs

---

## Critical Files

### To Modify
- `backend/pyproject.toml` - Add litellm dependency
- `backend/models/llm.py` - Update LLMConfig
- `backend/services/llm/factory.py` - Simplify factory
- `backend/services/provider_catalog.py` - Add Ollama models
- `README.md` or `backend/ARCHITECTURE.md` - Document Ollama

### To Create
- `backend/services/llm/litellm_client.py` - Unified client
- `backend/tests/services/test_litellm_client.py` - Tests

### To Keep (No Changes)
- `backend/services/llm/base.py` - Interface unchanged
- `backend/services/agent_orchestrator.py` - Uses factory
- `backend/services/debate_manager.py` - Uses factory
- `backend/routers/debates.py` - No API changes

---

## Notes

- Keep `BaseLLMClient` interface unchanged for flexibility
- Monitor latency in production - can switch to custom if needed
- LiteLLM docs: https://docs.litellm.ai/
- Consider keeping old clients behind feature flag for 1-2 weeks

---

## Future Enhancements (Post-Implementation)

Once LiteLLM is stable:
1. **Streaming support** - Use `litellm.acompletion(stream=True)`
2. **Cost tracking** - Use LiteLLM's built-in cost calculation
3. **Fallback providers** - Auto-fallback if primary fails
4. **More local models** - Add VLLM, LocalAI, LM Studio
