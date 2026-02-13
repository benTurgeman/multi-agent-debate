"""Integration tests for complete debate lifecycle."""
import pytest
from unittest.mock import AsyncMock, patch

from models.agent import AgentConfig, AgentRole
from models.debate import DebateConfig, DebateStatus
from models.llm import LLMConfig, ModelProvider
from services.debate_manager import DebateManager, DebateEventType


@pytest.fixture
def llm_configs():
    """Create LLM configurations for different providers."""
    return {
        "anthropic": LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        ),
        "openai": LLMConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            api_key_env_var="OPENAI_API_KEY",
        ),
    }


@pytest.fixture
def three_agent_mixed_debate_config(llm_configs):
    """Create a debate with 3 agents using mixed models (Claude + OpenAI)."""
    agents = [
        AgentConfig(
            agent_id="optimist",
            llm_config=llm_configs["anthropic"],
            role=AgentRole.DEBATER,
            name="Tech Optimist",
            stance="Pro",
            system_prompt="You are an optimistic technologist who believes AI will benefit humanity.",
            temperature=1.0,
            max_tokens=1024,
        ),
        AgentConfig(
            agent_id="skeptic",
            llm_config=llm_configs["openai"],
            role=AgentRole.DEBATER,
            name="AI Skeptic",
            stance="Con",
            system_prompt="You are a cautious critic worried about AI risks.",
            temperature=0.9,
            max_tokens=1024,
        ),
        AgentConfig(
            agent_id="pragmatist",
            llm_config=llm_configs["anthropic"],
            role=AgentRole.DEBATER,
            name="Pragmatist",
            stance="Neutral",
            system_prompt="You weigh both benefits and risks objectively.",
            temperature=1.0,
            max_tokens=1024,
        ),
    ]

    judge = AgentConfig(
        agent_id="judge",
        llm_config=llm_configs["anthropic"],
        role=AgentRole.JUDGE,
        name="Impartial Judge",
        stance="Impartial",
        system_prompt="You are a fair debate judge.",
        temperature=0.7,
        max_tokens=2048,
    )

    return DebateConfig(
        topic="AI will benefit humanity more than harm it",
        num_rounds=2,
        agents=agents,
        judge_config=judge,
    )


@pytest.mark.asyncio
async def test_complete_3_agent_mixed_model_debate(three_agent_mixed_debate_config):
    """
    Integration test: Run a complete 3-agent debate with mixed models.

    This test verifies:
    - 3 agents can debate successfully
    - Mixed Claude + OpenAI models work together
    - Turn order cycles correctly through all 3 agents
    - Judge receives all messages and declares winner
    - All events are emitted in correct order
    """
    manager = DebateManager(rate_limit_delay=0.01)
    debate_state = manager.create_debate(three_agent_mixed_debate_config)

    # Track all events
    events = []

    def event_callback(event):
        events.append((event.event_type, event.payload))

    manager.register_event_callback(event_callback)

    # Mock LLM clients for both Anthropic and OpenAI
    mock_anthropic = AsyncMock()
    mock_openai = AsyncMock()

    # Agent responses for 2 rounds, 3 agents each = 6 messages
    agent_responses = [
        # Round 1
        "AI has tremendous potential to solve global challenges like climate change and disease.",
        "But we must consider the risks of job displacement and autonomous weapons.",
        "Both perspectives have merit. We need balanced regulation.",
        # Round 2
        "The benefits far outweigh the risks if we implement proper safeguards.",
        "History shows technology often has unintended consequences we can't foresee.",
        "Pragmatic governance frameworks can maximize benefits while minimizing risks.",
    ]

    response_index = [0]  # Use list to allow modification in closure

    async def mock_anthropic_send(*args, **kwargs):
        result = agent_responses[response_index[0]]
        response_index[0] += 1
        return result

    async def mock_openai_send(*args, **kwargs):
        result = agent_responses[response_index[0]]
        response_index[0] += 1
        return result

    mock_anthropic.send_message = mock_anthropic_send
    mock_anthropic.get_provider_name.return_value = "anthropic"

    mock_openai.send_message = mock_openai_send
    mock_openai.get_provider_name.return_value = "openai"

    # Mock judge response
    judge_response = """{
        "summary": "An excellent debate with all three perspectives well-represented.",
        "agent_scores": [
            {
                "agent_id": "optimist",
                "agent_name": "Tech Optimist",
                "score": 8.5,
                "reasoning": "Strong, well-reasoned arguments about AI's potential benefits."
            },
            {
                "agent_id": "skeptic",
                "agent_name": "AI Skeptic",
                "score": 8.0,
                "reasoning": "Raised important concerns about risks and unintended consequences."
            },
            {
                "agent_id": "pragmatist",
                "agent_name": "Pragmatist",
                "score": 9.0,
                "reasoning": "Balanced perspective with practical solutions for governance."
            }
        ],
        "winner_id": "pragmatist",
        "winner_name": "Pragmatist",
        "key_arguments": [
            "AI has potential to solve global challenges",
            "Risks include job displacement and autonomous weapons",
            "Balanced regulation and governance frameworks needed"
        ]
    }"""

    async def mock_judge_send(*args, **kwargs):
        return judge_response

    mock_anthropic.send_message = AsyncMock(side_effect=[
        # Optimist (agent 1) responses
        agent_responses[0],  # Round 1
        agent_responses[3],  # Round 2
        # Pragmatist (agent 3) responses
        agent_responses[2],  # Round 1
        agent_responses[5],  # Round 2
        # Judge response
        judge_response,
    ])

    mock_openai.send_message = AsyncMock(side_effect=[
        # Skeptic (agent 2) responses
        agent_responses[1],  # Round 1
        agent_responses[4],  # Round 2
    ])

    # Patch the LLM factory to return our mocks
    def mock_create_llm_client(llm_config):
        if llm_config.provider == ModelProvider.ANTHROPIC:
            return mock_anthropic
        elif llm_config.provider == ModelProvider.OPENAI:
            return mock_openai

    with patch(
        "services.agent_orchestrator.create_llm_client",
        side_effect=mock_create_llm_client,
    ), patch(
        "services.debate_manager.create_llm_client",
        side_effect=mock_create_llm_client,
    ):
        # Run the complete debate
        result = await manager.run_debate(debate_state)

    # Verify debate completed successfully
    assert result.status == DebateStatus.COMPLETED
    assert result.started_at is not None
    assert result.completed_at is not None

    # Verify all messages were created (2 rounds * 3 agents = 6 messages)
    assert len(result.history) == 6

    # Verify turn order cycled correctly through all 3 agents
    # Round 1: optimist, skeptic, pragmatist
    # Round 2: optimist, skeptic, pragmatist
    assert result.history[0].agent_id == "optimist"
    assert result.history[0].round_number == 1
    assert result.history[0].turn_number == 0

    assert result.history[1].agent_id == "skeptic"
    assert result.history[1].round_number == 1
    assert result.history[1].turn_number == 1

    assert result.history[2].agent_id == "pragmatist"
    assert result.history[2].round_number == 1
    assert result.history[2].turn_number == 2

    assert result.history[3].agent_id == "optimist"
    assert result.history[3].round_number == 2
    assert result.history[3].turn_number == 0

    assert result.history[4].agent_id == "skeptic"
    assert result.history[4].round_number == 2
    assert result.history[4].turn_number == 1

    assert result.history[5].agent_id == "pragmatist"
    assert result.history[5].round_number == 2
    assert result.history[5].turn_number == 2

    # Verify judge result
    assert result.judge_result is not None
    assert result.judge_result.winner_id == "pragmatist"
    assert result.judge_result.winner_name == "Pragmatist"
    assert len(result.judge_result.agent_scores) == 3

    # Verify all 3 agents were scored
    agent_ids_scored = {score.agent_id for score in result.judge_result.agent_scores}
    assert agent_ids_scored == {"optimist", "skeptic", "pragmatist"}

    # Verify scores are in valid range
    for score in result.judge_result.agent_scores:
        assert 0.0 <= score.score <= 10.0

    # Verify winner has highest score
    winner_score = result.judge_result.get_score_for_agent("pragmatist")
    assert winner_score == 9.0
    assert winner_score >= result.judge_result.get_score_for_agent("optimist")
    assert winner_score >= result.judge_result.get_score_for_agent("skeptic")

    # Verify event sequence
    event_types = [e[0] for e in events]

    assert DebateEventType.DEBATE_STARTED in event_types
    assert event_types.count(DebateEventType.ROUND_STARTED) == 2
    assert event_types.count(DebateEventType.AGENT_THINKING) == 6  # 2 rounds * 3 agents
    assert event_types.count(DebateEventType.MESSAGE_RECEIVED) == 6
    assert event_types.count(DebateEventType.TURN_COMPLETE) == 6
    assert event_types.count(DebateEventType.ROUND_COMPLETE) == 2
    assert DebateEventType.JUDGING_STARTED in event_types
    assert DebateEventType.JUDGE_RESULT in event_types
    assert DebateEventType.DEBATE_COMPLETE in event_types

    # Verify both LLM providers were used
    assert mock_anthropic.send_message.call_count == 5  # 2x optimist + 2x pragmatist + 1x judge
    assert mock_openai.send_message.call_count == 2  # 2x skeptic

    print("\n✅ Integration test passed: 3-agent mixed-model debate completed successfully")
    print(f"   - Total messages: {len(result.history)}")
    print(f"   - Winner: {result.judge_result.winner_name}")
    print(f"   - Scores: {[f'{s.agent_name}: {s.score}' for s in result.judge_result.agent_scores]}")


@pytest.mark.asyncio
async def test_debate_with_turn_retry_success(three_agent_mixed_debate_config):
    """Test that debates can recover from temporary API failures."""
    manager = DebateManager(rate_limit_delay=0.01)
    debate_state = manager.create_debate(three_agent_mixed_debate_config)

    # Mock LLM to fail once then succeed
    mock_client = AsyncMock()
    mock_client.get_provider_name.return_value = "anthropic"

    # First call fails, second succeeds
    responses = [
        Exception("Temporary API error"),
        "This is a successful response after retry.",
    ]
    response_iter = iter(responses)

    async def mock_send(*args, **kwargs):
        resp = next(response_iter)
        if isinstance(resp, Exception):
            raise resp
        return resp

    # Setup mock to alternate between failure and success
    call_count = [0]

    async def mock_send_with_retry(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # First debater turn fails once then succeeds
            raise Exception("Temporary API error")
        return f"Response for call {call_count[0]}"

    mock_client.send_message = AsyncMock(side_effect=[
        Exception("Temporary API error"),  # First attempt fails
        "Success after retry",  # Retry succeeds
        "Second agent response",
        "Third agent response",
        "Fourth message",
        "Fifth message",
        "Sixth message",
        # Judge
        '{"summary": "Test", "agent_scores": [{"agent_id": "optimist", "agent_name": "Tech Optimist", "score": 8.0, "reasoning": "Good"}], "winner_id": "optimist", "winner_name": "Tech Optimist", "key_arguments": []}',
    ])

    with patch(
        "services.agent_orchestrator.create_llm_client", return_value=mock_client
    ), patch("services.debate_manager.create_llm_client", return_value=mock_client):
        result = await manager.run_debate(debate_state)

    # Debate should complete successfully despite the retry
    assert result.status == DebateStatus.COMPLETED
    assert len(result.history) == 6

    # First message should be the retry success
    assert result.history[0].content == "Success after retry"

    print("\n✅ Turn retry test passed: Debate recovered from temporary API failure")
