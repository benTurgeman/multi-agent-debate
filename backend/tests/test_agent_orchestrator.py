"""Tests for agent orchestrator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.agent import AgentConfig, AgentRole
from models.debate import DebateState, DebateConfig, DebateStatus
from models.llm import LLMConfig, ModelProvider
from models.message import Message
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
        AgentConfig(
            agent_id="agent_3",
            llm_config=sample_llm_config,
            role=AgentRole.DEBATER,
            name="Agent Three",
            stance="Neutral",
            system_prompt="You are agent three.",
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
def debate_state_2_agents(sample_agents, sample_judge_config):
    """Create a debate state with 2 agents."""
    config = DebateConfig(
        topic="Test topic",
        num_rounds=2,
        agents=sample_agents[:2],
        judge_config=sample_judge_config,
    )
    return DebateState(config=config)


@pytest.fixture
def debate_state_3_agents(sample_agents, sample_judge_config):
    """Create a debate state with 3 agents."""
    config = DebateConfig(
        topic="Test topic with 3 agents",
        num_rounds=2,
        agents=sample_agents,
        judge_config=sample_judge_config,
    )
    return DebateState(config=config)


@pytest.fixture
def orchestrator():
    """Create an agent orchestrator instance."""
    return AgentOrchestrator(max_turn_retries=3)


class TestGetNextAgent:
    """Tests for get_next_agent method."""

    def test_get_next_agent_first_turn(self, orchestrator, debate_state_2_agents):
        """Test getting the first agent."""
        debate_state_2_agents.current_turn = 0
        agent = orchestrator.get_next_agent(debate_state_2_agents)
        assert agent.agent_id == "agent_1"

    def test_get_next_agent_second_turn(self, orchestrator, debate_state_2_agents):
        """Test getting the second agent."""
        debate_state_2_agents.current_turn = 1
        agent = orchestrator.get_next_agent(debate_state_2_agents)
        assert agent.agent_id == "agent_2"

    def test_get_next_agent_cycles_correctly(self, orchestrator, debate_state_2_agents):
        """Test that agents cycle correctly."""
        # Turn 0: agent_1
        debate_state_2_agents.current_turn = 0
        assert orchestrator.get_next_agent(debate_state_2_agents).agent_id == "agent_1"

        # Turn 1: agent_2
        debate_state_2_agents.current_turn = 1
        assert orchestrator.get_next_agent(debate_state_2_agents).agent_id == "agent_2"

        # Turn 2: back to agent_1
        debate_state_2_agents.current_turn = 2
        assert orchestrator.get_next_agent(debate_state_2_agents).agent_id == "agent_1"

        # Turn 3: agent_2
        debate_state_2_agents.current_turn = 3
        assert orchestrator.get_next_agent(debate_state_2_agents).agent_id == "agent_2"

    def test_get_next_agent_3_agents(self, orchestrator, debate_state_3_agents):
        """Test cycling with 3 agents."""
        # Turn 0: agent_1
        debate_state_3_agents.current_turn = 0
        assert orchestrator.get_next_agent(debate_state_3_agents).agent_id == "agent_1"

        # Turn 1: agent_2
        debate_state_3_agents.current_turn = 1
        assert orchestrator.get_next_agent(debate_state_3_agents).agent_id == "agent_2"

        # Turn 2: agent_3
        debate_state_3_agents.current_turn = 2
        assert orchestrator.get_next_agent(debate_state_3_agents).agent_id == "agent_3"

        # Turn 3: back to agent_1
        debate_state_3_agents.current_turn = 3
        assert orchestrator.get_next_agent(debate_state_3_agents).agent_id == "agent_1"

    def test_get_next_agent_no_agents_validation(self, orchestrator, sample_judge_config):
        """Test that config validation prevents creating debate with no agents."""
        from pydantic import ValidationError

        # DebateConfig validation should prevent creating a debate with no agents
        with pytest.raises(ValidationError, match="at least 2 items"):
            config = DebateConfig(
                topic="Test",
                num_rounds=1,
                agents=[],
                judge_config=sample_judge_config,
            )


class TestExecuteTurn:
    """Tests for execute_turn method."""

    @pytest.mark.asyncio
    async def test_execute_turn_success(
        self, orchestrator, debate_state_2_agents, sample_agents
    ):
        """Test successful turn execution."""
        agent = sample_agents[0]
        debate_state_2_agents.current_round = 1
        debate_state_2_agents.current_turn = 0

        # Mock the LLM client
        mock_client = AsyncMock()
        mock_client.send_message.return_value = "This is my response."

        with patch(
            "services.agent_orchestrator.create_llm_client", return_value=mock_client
        ):
            message = await orchestrator.execute_turn(debate_state_2_agents, agent)

        assert isinstance(message, Message)
        assert message.agent_id == "agent_1"
        assert message.agent_name == "Agent One"
        assert message.content == "This is my response."
        assert message.round_number == 1
        assert message.turn_number == 0
        assert message.stance == "Pro"

        # Verify LLM client was called
        mock_client.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_turn_with_history(
        self, orchestrator, debate_state_2_agents, sample_agents
    ):
        """Test turn execution with existing history."""
        # Add a previous message to history
        previous_message = Message(
            agent_id="agent_1",
            agent_name="Agent One",
            content="Previous message",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        debate_state_2_agents.add_message(previous_message)
        debate_state_2_agents.current_round = 1
        debate_state_2_agents.current_turn = 1

        agent = sample_agents[1]

        mock_client = AsyncMock()
        mock_client.send_message.return_value = "Response to previous message."

        with patch(
            "services.agent_orchestrator.create_llm_client", return_value=mock_client
        ):
            message = await orchestrator.execute_turn(debate_state_2_agents, agent)

        assert message.agent_id == "agent_2"
        assert message.content == "Response to previous message."

        # Verify the history was passed to the LLM
        call_args = mock_client.send_message.call_args
        messages_arg = call_args.kwargs["messages"]
        assert len(messages_arg) == 1
        assert "Previous message" in messages_arg[0]["content"]

    @pytest.mark.asyncio
    async def test_execute_turn_retry_on_failure(
        self, orchestrator, debate_state_2_agents, sample_agents
    ):
        """Test that turn execution retries on failure."""
        agent = sample_agents[0]
        debate_state_2_agents.current_round = 1
        debate_state_2_agents.current_turn = 0

        mock_client = AsyncMock()
        # Fail twice, then succeed
        mock_client.send_message.side_effect = [
            Exception("API error 1"),
            Exception("API error 2"),
            "Success on third try",
        ]

        with patch(
            "services.agent_orchestrator.create_llm_client", return_value=mock_client
        ):
            message = await orchestrator.execute_turn(debate_state_2_agents, agent)

        assert message.content == "Success on third try"
        assert mock_client.send_message.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_turn_fails_after_max_retries(
        self, orchestrator, debate_state_2_agents, sample_agents
    ):
        """Test that turn execution fails after max retries."""
        agent = sample_agents[0]
        debate_state_2_agents.current_round = 1
        debate_state_2_agents.current_turn = 0

        mock_client = AsyncMock()
        # Always fail
        mock_client.send_message.side_effect = Exception("Persistent API error")

        with patch(
            "services.agent_orchestrator.create_llm_client", return_value=mock_client
        ):
            with pytest.raises(
                DebateExecutionError, match="Failed to execute turn.*after 3 attempts"
            ):
                await orchestrator.execute_turn(debate_state_2_agents, agent)

        # Should have tried 3 times (max_turn_retries)
        assert mock_client.send_message.call_count == 3


class TestGetTurnOrder:
    """Tests for get_turn_order method."""

    def test_get_turn_order_2_agents(self, orchestrator, debate_state_2_agents):
        """Test turn order with 2 agents."""
        turn_order = orchestrator.get_turn_order(debate_state_2_agents)
        assert turn_order == ["agent_1", "agent_2"]

    def test_get_turn_order_3_agents(self, orchestrator, debate_state_3_agents):
        """Test turn order with 3 agents."""
        turn_order = orchestrator.get_turn_order(debate_state_3_agents)
        assert turn_order == ["agent_1", "agent_2", "agent_3"]


class TestCalculateTotalTurns:
    """Tests for calculate_total_turns method."""

    def test_calculate_total_turns_2_agents_2_rounds(
        self, orchestrator, debate_state_2_agents
    ):
        """Test total turns calculation with 2 agents and 2 rounds."""
        total_turns = orchestrator.calculate_total_turns(debate_state_2_agents)
        assert total_turns == 4  # 2 rounds * 2 agents

    def test_calculate_total_turns_3_agents_2_rounds(
        self, orchestrator, debate_state_3_agents
    ):
        """Test total turns calculation with 3 agents and 2 rounds."""
        total_turns = orchestrator.calculate_total_turns(debate_state_3_agents)
        assert total_turns == 6  # 2 rounds * 3 agents

    def test_calculate_total_turns_3_agents_5_rounds(
        self, orchestrator, sample_agents, sample_judge_config
    ):
        """Test total turns calculation with 3 agents and 5 rounds."""
        config = DebateConfig(
            topic="Test",
            num_rounds=5,
            agents=sample_agents,
            judge_config=sample_judge_config,
        )
        debate_state = DebateState(config=config)

        total_turns = orchestrator.calculate_total_turns(debate_state)
        assert total_turns == 15  # 5 rounds * 3 agents
