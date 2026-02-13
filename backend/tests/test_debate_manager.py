"""Tests for debate manager."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, call

from models.agent import AgentConfig, AgentRole
from models.debate import DebateState, DebateConfig, DebateStatus
from models.llm import LLMConfig, ModelProvider
from models.judge import JudgeResult, AgentScore
from models.message import Message
from services.debate_manager import (
    DebateManager,
    DebateEvent,
    DebateEventType,
)
from services.agent_orchestrator import AgentOrchestrator
from core.exceptions import DebateExecutionError


@pytest.fixture
def sample_llm_config():
    """Create a sample LLM configuration."""
    return LLMConfig(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet-20241022",
        api_key_env_var="ANTHROPIC_API_KEY",
    )


@pytest.fixture
def sample_agents(sample_llm_config):
    """Create sample agents for testing."""
    return [
        AgentConfig(
            agent_id="agent_1",
            llm_config=sample_llm_config,
            role=AgentRole.DEBATER,
            name="Agent One",
            stance="Pro",
            system_prompt="You are agent one.",
            temperature=1.0,
            max_tokens=1024,
        ),
        AgentConfig(
            agent_id="agent_2",
            llm_config=sample_llm_config,
            role=AgentRole.DEBATER,
            name="Agent Two",
            stance="Con",
            system_prompt="You are agent two.",
            temperature=1.0,
            max_tokens=1024,
        ),
    ]


@pytest.fixture
def sample_judge_config(sample_llm_config):
    """Create a sample judge configuration."""
    return AgentConfig(
        agent_id="judge",
        llm_config=sample_llm_config,
        role=AgentRole.JUDGE,
        name="Judge",
        stance="Impartial",
        system_prompt="You are an impartial judge.",
        temperature=0.7,
        max_tokens=2048,
    )


@pytest.fixture
def debate_config(sample_agents, sample_judge_config):
    """Create a debate configuration."""
    return DebateConfig(
        topic="AI is beneficial to humanity",
        num_rounds=2,
        agents=sample_agents,
        judge_config=sample_judge_config,
    )


@pytest.fixture
def debate_manager():
    """Create a debate manager instance."""
    # Use very short rate limit delay for testing
    return DebateManager(rate_limit_delay=0.01)


class TestCreateDebate:
    """Tests for create_debate method."""

    def test_create_debate(self, debate_manager, debate_config):
        """Test creating a debate."""
        debate_state = debate_manager.create_debate(debate_config)

        assert isinstance(debate_state, DebateState)
        assert debate_state.config == debate_config
        assert debate_state.status == DebateStatus.CREATED
        assert debate_state.current_round == 0
        assert debate_state.current_turn == 0
        assert len(debate_state.history) == 0
        assert debate_state.judge_result is None
        assert debate_state.debate_id is not None


class TestEventSystem:
    """Tests for event callback system."""

    def test_register_event_callback(self, debate_manager):
        """Test registering an event callback."""
        callback = MagicMock()
        debate_manager.register_event_callback(callback)

        assert callback in debate_manager._event_callbacks

    def test_emit_event_calls_callbacks(self, debate_manager):
        """Test that emitting an event calls all registered callbacks."""
        callback1 = MagicMock()
        callback2 = MagicMock()

        debate_manager.register_event_callback(callback1)
        debate_manager.register_event_callback(callback2)

        event = DebateEvent(
            event_type=DebateEventType.DEBATE_STARTED,
            debate_id="test_id",
            payload={"test": "data"},
        )

        debate_manager._emit_event(event)

        callback1.assert_called_once_with(event)
        callback2.assert_called_once_with(event)

    def test_emit_event_handles_callback_errors(self, debate_manager):
        """Test that callback errors don't crash event emission."""
        failing_callback = MagicMock(side_effect=Exception("Callback error"))
        working_callback = MagicMock()

        debate_manager.register_event_callback(failing_callback)
        debate_manager.register_event_callback(working_callback)

        event = DebateEvent(
            event_type=DebateEventType.DEBATE_STARTED,
            debate_id="test_id",
        )

        # Should not raise exception
        debate_manager._emit_event(event)

        # Working callback should still be called
        working_callback.assert_called_once()


class TestRunDebate:
    """Tests for run_debate method."""

    @pytest.mark.asyncio
    async def test_run_debate_success(self, debate_manager, debate_config):
        """Test successful debate execution."""
        debate_state = debate_manager.create_debate(debate_config)

        # Mock the orchestrator
        mock_orchestrator = AsyncMock(spec=AgentOrchestrator)
        mock_orchestrator.get_turn_order.return_value = ["agent_1", "agent_2"]

        # Mock execute_turn to return messages
        def create_mock_message(agent_id, round_num, turn_num):
            return Message(
                agent_id=agent_id,
                agent_name=f"Agent {agent_id}",
                content=f"Message from {agent_id}",
                round_number=round_num,
                turn_number=turn_num,
                stance="Pro" if agent_id == "agent_1" else "Con",
            )

        mock_orchestrator.execute_turn.side_effect = [
            # Round 1
            create_mock_message("agent_1", 1, 0),
            create_mock_message("agent_2", 1, 1),
            # Round 2
            create_mock_message("agent_1", 2, 0),
            create_mock_message("agent_2", 2, 1),
        ]

        debate_manager.orchestrator = mock_orchestrator

        # Mock judge response
        judge_result = JudgeResult(
            summary="Great debate",
            agent_scores=[
                AgentScore(
                    agent_id="agent_1",
                    agent_name="Agent One",
                    score=8.5,
                    reasoning="Strong arguments",
                ),
                AgentScore(
                    agent_id="agent_2",
                    agent_name="Agent Two",
                    score=7.5,
                    reasoning="Good points",
                ),
            ],
            winner_id="agent_1",
            winner_name="Agent One",
            key_arguments=["AI benefits", "Risk mitigation"],
        )

        with patch.object(
            debate_manager, "_invoke_judge", return_value=judge_result
        ) as mock_judge:
            result = await debate_manager.run_debate(debate_state)

        # Verify debate completed successfully
        assert result.status == DebateStatus.COMPLETED
        assert result.started_at is not None
        assert result.completed_at is not None
        assert len(result.history) == 4  # 2 rounds * 2 agents
        assert result.judge_result == judge_result

        # Verify orchestrator was called correctly
        assert mock_orchestrator.execute_turn.call_count == 4
        assert mock_orchestrator.get_turn_order.call_count == 2

        # Verify judge was called
        mock_judge.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_debate_emits_events(self, debate_manager, debate_config):
        """Test that debate execution emits correct events."""
        debate_state = debate_manager.create_debate(debate_config)

        # Track events
        events = []

        def event_callback(event: DebateEvent):
            events.append(event.event_type)

        debate_manager.register_event_callback(event_callback)

        # Mock orchestrator
        mock_orchestrator = AsyncMock(spec=AgentOrchestrator)
        mock_orchestrator.get_turn_order.return_value = ["agent_1", "agent_2"]
        mock_orchestrator.execute_turn.return_value = Message(
            agent_id="agent_1",
            agent_name="Agent One",
            content="Test message",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        debate_manager.orchestrator = mock_orchestrator

        # Mock judge
        judge_result = JudgeResult(
            summary="Test",
            agent_scores=[
                AgentScore(
                    agent_id="agent_1",
                    agent_name="Agent One",
                    score=8.0,
                    reasoning="Good",
                )
            ],
            winner_id="agent_1",
            winner_name="Agent One",
            key_arguments=[],
        )

        with patch.object(debate_manager, "_invoke_judge", return_value=judge_result):
            await debate_manager.run_debate(debate_state)

        # Verify event sequence
        # Note: We're mocking _invoke_judge, so judge events won't be emitted
        # They're tested separately in TestInvokeJudge
        assert DebateEventType.DEBATE_STARTED in events
        assert DebateEventType.ROUND_STARTED in events
        assert DebateEventType.AGENT_THINKING in events
        assert DebateEventType.MESSAGE_RECEIVED in events
        assert DebateEventType.TURN_COMPLETE in events
        assert DebateEventType.ROUND_COMPLETE in events
        assert DebateEventType.DEBATE_COMPLETE in events

    @pytest.mark.asyncio
    async def test_run_debate_failure_handling(self, debate_manager, debate_config):
        """Test that debate failures are handled correctly."""
        debate_state = debate_manager.create_debate(debate_config)

        # Track events
        events = []

        def event_callback(event: DebateEvent):
            events.append(event.event_type)

        debate_manager.register_event_callback(event_callback)

        # Mock orchestrator to fail
        mock_orchestrator = AsyncMock(spec=AgentOrchestrator)
        mock_orchestrator.get_turn_order.return_value = ["agent_1", "agent_2"]
        mock_orchestrator.execute_turn.side_effect = Exception("API failure")
        debate_manager.orchestrator = mock_orchestrator

        with pytest.raises(DebateExecutionError, match="Debate execution failed"):
            await debate_manager.run_debate(debate_state)

        # Verify debate marked as failed
        assert debate_state.status == DebateStatus.FAILED
        assert debate_state.error_message is not None
        assert "API failure" in debate_state.error_message

        # Verify error event was emitted
        assert DebateEventType.ERROR in events


class TestInvokeJudge:
    """Tests for _invoke_judge method."""

    @pytest.mark.asyncio
    async def test_invoke_judge_success(self, debate_manager, debate_config):
        """Test successful judge invocation."""
        debate_state = debate_manager.create_debate(debate_config)

        # Add some messages to history
        debate_state.add_message(
            Message(
                agent_id="agent_1",
                agent_name="Agent One",
                content="Pro argument",
                round_number=1,
                turn_number=0,
                stance="Pro",
            )
        )
        debate_state.add_message(
            Message(
                agent_id="agent_2",
                agent_name="Agent Two",
                content="Con argument",
                round_number=1,
                turn_number=1,
                stance="Con",
            )
        )

        # Mock LLM client for judge
        judge_response = {
            "summary": "Excellent debate with strong arguments on both sides",
            "agent_scores": [
                {
                    "agent_id": "agent_1",
                    "agent_name": "Agent One",
                    "score": 8.5,
                    "reasoning": "Strong logical arguments",
                },
                {
                    "agent_id": "agent_2",
                    "agent_name": "Agent Two",
                    "score": 7.5,
                    "reasoning": "Good counterpoints",
                },
            ],
            "winner_id": "agent_1",
            "winner_name": "Agent One",
            "key_arguments": ["AI benefits humanity", "Risk considerations"],
        }

        mock_client = AsyncMock()
        mock_client.send_message.return_value = json.dumps(judge_response)

        with patch(
            "services.debate_manager.create_llm_client", return_value=mock_client
        ):
            result = await debate_manager._invoke_judge(debate_state)

        assert isinstance(result, JudgeResult)
        assert result.summary == judge_response["summary"]
        assert len(result.agent_scores) == 2
        assert result.winner_id == "agent_1"
        assert result.winner_name == "Agent One"

    @pytest.mark.asyncio
    async def test_invoke_judge_with_markdown_code_fence(
        self, debate_manager, debate_config
    ):
        """Test judge response parsing with markdown code fence."""
        debate_state = debate_manager.create_debate(debate_config)

        judge_response = {
            "summary": "Test summary",
            "agent_scores": [
                {
                    "agent_id": "agent_1",
                    "agent_name": "Agent One",
                    "score": 8.0,
                    "reasoning": "Good",
                }
            ],
            "winner_id": "agent_1",
            "winner_name": "Agent One",
            "key_arguments": [],
        }

        # Wrap response in markdown code fence
        markdown_response = f"```json\n{json.dumps(judge_response)}\n```"

        mock_client = AsyncMock()
        mock_client.send_message.return_value = markdown_response

        with patch(
            "services.debate_manager.create_llm_client", return_value=mock_client
        ):
            result = await debate_manager._invoke_judge(debate_state)

        assert isinstance(result, JudgeResult)
        assert result.winner_id == "agent_1"

    @pytest.mark.asyncio
    async def test_invoke_judge_fallback_on_parse_error(
        self, debate_manager, debate_config
    ):
        """Test judge fallback when response cannot be parsed."""
        debate_state = debate_manager.create_debate(debate_config)

        # Invalid JSON response
        invalid_response = "This is not valid JSON at all"

        mock_client = AsyncMock()
        mock_client.send_message.return_value = invalid_response

        with patch(
            "services.debate_manager.create_llm_client", return_value=mock_client
        ):
            result = await debate_manager._invoke_judge(debate_state)

        # Should still return a valid JudgeResult with fallback values
        assert isinstance(result, JudgeResult)
        assert len(result.agent_scores) == len(debate_state.config.agents)
        assert all(score.score == 5.0 for score in result.agent_scores)
        assert "Unable to parse" in result.summary or "failed to parse" in result.summary.lower()


class TestExecuteRound:
    """Tests for _execute_round method."""

    @pytest.mark.asyncio
    async def test_execute_round(self, debate_manager, debate_config):
        """Test executing a single round."""
        debate_state = debate_manager.create_debate(debate_config)

        # Track events
        events = []

        def event_callback(event: DebateEvent):
            events.append((event.event_type, event.payload))

        debate_manager.register_event_callback(event_callback)

        # Mock orchestrator
        mock_orchestrator = AsyncMock(spec=AgentOrchestrator)
        mock_orchestrator.get_turn_order.return_value = ["agent_1", "agent_2"]

        mock_orchestrator.execute_turn.side_effect = [
            Message(
                agent_id="agent_1",
                agent_name="Agent One",
                content="Message 1",
                round_number=1,
                turn_number=0,
                stance="Pro",
            ),
            Message(
                agent_id="agent_2",
                agent_name="Agent Two",
                content="Message 2",
                round_number=1,
                turn_number=1,
                stance="Con",
            ),
        ]

        debate_manager.orchestrator = mock_orchestrator

        await debate_manager._execute_round(debate_state, 1)

        # Verify round state
        assert debate_state.current_round == 1
        assert len(debate_state.history) == 2

        # Verify events were emitted
        event_types = [e[0] for e in events]
        assert DebateEventType.ROUND_STARTED in event_types
        assert DebateEventType.AGENT_THINKING in event_types
        assert DebateEventType.MESSAGE_RECEIVED in event_types
        assert DebateEventType.TURN_COMPLETE in event_types
        assert DebateEventType.ROUND_COMPLETE in event_types

        # Verify round complete event has correct payload
        round_complete_event = next(
            e for e in events if e[0] == DebateEventType.ROUND_COMPLETE
        )
        assert round_complete_event[1]["round_number"] == 1


class TestParseJudgeResponse:
    """Tests for _parse_judge_response method."""

    def test_parse_valid_json(self, debate_manager, sample_agents):
        """Test parsing valid JSON response."""
        response = {
            "summary": "Great debate",
            "agent_scores": [
                {
                    "agent_id": "agent_1",
                    "agent_name": "Agent One",
                    "score": 9.0,
                    "reasoning": "Excellent",
                }
            ],
            "winner_id": "agent_1",
            "winner_name": "Agent One",
            "key_arguments": ["Key point 1"],
        }

        result = debate_manager._parse_judge_response(
            json.dumps(response), sample_agents
        )

        assert isinstance(result, JudgeResult)
        assert result.winner_id == "agent_1"

    def test_parse_json_with_code_fence(self, debate_manager, sample_agents):
        """Test parsing JSON wrapped in markdown code fence."""
        response = {
            "summary": "Test",
            "agent_scores": [
                {
                    "agent_id": "agent_1",
                    "agent_name": "Agent One",
                    "score": 8.0,
                    "reasoning": "Good",
                }
            ],
            "winner_id": "agent_1",
            "winner_name": "Agent One",
            "key_arguments": [],
        }

        wrapped = f"```json\n{json.dumps(response)}\n```"

        result = debate_manager._parse_judge_response(wrapped, sample_agents)

        assert isinstance(result, JudgeResult)
        assert result.winner_id == "agent_1"

    def test_parse_invalid_json_fallback(self, debate_manager, sample_agents):
        """Test fallback behavior for invalid JSON."""
        invalid_json = "This is not JSON"

        result = debate_manager._parse_judge_response(invalid_json, sample_agents)

        assert isinstance(result, JudgeResult)
        # Should create fallback scores for all agents
        assert len(result.agent_scores) == len(sample_agents)
        assert all(score.score == 5.0 for score in result.agent_scores)
