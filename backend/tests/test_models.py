"""Tests for all Pydantic models."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from models.agent import AgentConfig, AgentRole
from models.debate import DebateConfig, DebateState, DebateStatus
from models.judge import AgentScore, JudgeResult
from models.llm import LLMConfig, ModelProvider
from models.message import Message, MessageHistory


class TestLLMConfig:
    """Test LLMConfig model."""

    def test_valid_anthropic_config(self):
        """Test creating a valid Anthropic model config."""
        config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )
        assert config.provider == ModelProvider.ANTHROPIC
        assert config.model_name == "claude-3-5-sonnet-20241022"
        assert config.api_key_env_var == "ANTHROPIC_API_KEY"

    def test_valid_openai_config(self):
        """Test creating a valid OpenAI model config."""
        config = LLMConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            api_key_env_var="OPENAI_API_KEY",
        )
        assert config.provider == ModelProvider.OPENAI
        assert config.model_name == "gpt-4o"

    def test_missing_required_fields(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            LLMConfig(provider=ModelProvider.ANTHROPIC)


class TestAgentConfig:
    """Test AgentConfig model."""

    def test_valid_debater_config(self):
        """Test creating a valid debater agent config."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )
        agent = AgentConfig(
            agent_id="agent1",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Tech Optimist",
            stance="Pro",
            system_prompt="You are an optimistic technologist.",
            temperature=1.0,
            max_tokens=1024,
        )
        assert agent.agent_id == "agent1"
        assert agent.role == AgentRole.DEBATER
        assert agent.temperature == 1.0

    def test_default_values(self):
        """Test that default values are applied correctly."""
        llm_config = LLMConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            api_key_env_var="OPENAI_API_KEY",
        )
        agent = AgentConfig(
            agent_id="agent2",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="You are a fair judge.",
        )
        assert agent.temperature == 1.0
        assert agent.max_tokens == 1024

    def test_temperature_validation(self):
        """Test temperature bounds validation."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        # Valid temperature
        agent = AgentConfig(
            agent_id="agent3",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Test",
            stance="Pro",
            system_prompt="Test",
            temperature=0.5,
        )
        assert agent.temperature == 0.5

        # Invalid temperature (too high)
        with pytest.raises(ValidationError):
            AgentConfig(
                agent_id="agent4",
                llm_config=llm_config,
                role=AgentRole.DEBATER,
                name="Test",
                stance="Pro",
                system_prompt="Test",
                temperature=2.5,
            )


class TestMessage:
    """Test Message model."""

    def test_create_message(self):
        """Test creating a message."""
        msg = Message(
            agent_id="agent1",
            agent_name="Tech Optimist",
            content="AI will benefit humanity.",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        assert msg.agent_id == "agent1"
        assert msg.content == "AI will benefit humanity."
        assert isinstance(msg.timestamp, datetime)

    def test_message_validation(self):
        """Test message field validation."""
        # Invalid round number (must be >= 1)
        with pytest.raises(ValidationError):
            Message(
                agent_id="agent1",
                agent_name="Test",
                content="Test",
                round_number=0,
                turn_number=0,
                stance="Pro",
            )


class TestMessageHistory:
    """Test MessageHistory model."""

    def test_add_message(self):
        """Test adding messages to history."""
        history = MessageHistory()
        msg1 = Message(
            agent_id="agent1",
            agent_name="Agent 1",
            content="Message 1",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        msg2 = Message(
            agent_id="agent2",
            agent_name="Agent 2",
            content="Message 2",
            round_number=1,
            turn_number=1,
            stance="Con",
        )

        history.add_message(msg1)
        history.add_message(msg2)

        assert len(history.messages) == 2
        assert history.messages[0].agent_id == "agent1"

    def test_get_messages_for_round(self):
        """Test filtering messages by round."""
        history = MessageHistory()
        msg1 = Message(
            agent_id="agent1",
            agent_name="Agent 1",
            content="Round 1",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        msg2 = Message(
            agent_id="agent2",
            agent_name="Agent 2",
            content="Round 2",
            round_number=2,
            turn_number=0,
            stance="Con",
        )

        history.add_message(msg1)
        history.add_message(msg2)

        round1_msgs = history.get_messages_for_round(1)
        assert len(round1_msgs) == 1
        assert round1_msgs[0].content == "Round 1"


class TestJudgeModels:
    """Test Judge and scoring models."""

    def test_agent_score(self):
        """Test creating an agent score."""
        score = AgentScore(
            agent_id="agent1",
            agent_name="Tech Optimist",
            score=8.5,
            reasoning="Strong arguments and evidence.",
        )
        assert score.score == 8.5
        assert score.agent_id == "agent1"

    def test_score_validation(self):
        """Test score bounds validation."""
        # Valid score
        score = AgentScore(
            agent_id="agent1", agent_name="Test", score=10.0, reasoning="Perfect"
        )
        assert score.score == 10.0

        # Invalid score (too high)
        with pytest.raises(ValidationError):
            AgentScore(
                agent_id="agent1", agent_name="Test", score=11.0, reasoning="Test"
            )

        # Invalid score (negative)
        with pytest.raises(ValidationError):
            AgentScore(
                agent_id="agent1", agent_name="Test", score=-1.0, reasoning="Test"
            )

    def test_judge_result(self):
        """Test creating a judge result."""
        scores = [
            AgentScore(
                agent_id="agent1",
                agent_name="Optimist",
                score=8.5,
                reasoning="Strong",
            ),
            AgentScore(
                agent_id="agent2", agent_name="Skeptic", score=7.0, reasoning="Good"
            ),
        ]
        result = JudgeResult(
            summary="Close debate",
            agent_scores=scores,
            winner_id="agent1",
            winner_name="Optimist",
            key_arguments=["AI benefits", "Risk concerns"],
        )
        assert result.winner_id == "agent1"
        assert len(result.agent_scores) == 2

    def test_get_score_for_agent(self):
        """Test getting score for specific agent."""
        scores = [
            AgentScore(
                agent_id="agent1", agent_name="A", score=8.5, reasoning="Good"
            ),
            AgentScore(
                agent_id="agent2", agent_name="B", score=7.0, reasoning="OK"
            ),
        ]
        result = JudgeResult(
            summary="Test",
            agent_scores=scores,
            winner_id="agent1",
            winner_name="A",
        )

        assert result.get_score_for_agent("agent1") == 8.5
        assert result.get_score_for_agent("agent2") == 7.0
        assert result.get_score_for_agent("nonexistent") == 0.0


class TestDebateConfig:
    """Test DebateConfig model."""

    def test_valid_config_two_agents(self):
        """Test creating a valid debate config with 2 agents."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agent1 = AgentConfig(
            agent_id="agent1",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 1",
            stance="Pro",
            system_prompt="Test",
        )
        agent2 = AgentConfig(
            agent_id="agent2",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 2",
            stance="Con",
            system_prompt="Test",
        )
        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        config = DebateConfig(
            topic="AI benefits humanity",
            num_rounds=3,
            agents=[agent1, agent2],
            judge_config=judge,
        )

        assert config.topic == "AI benefits humanity"
        assert config.num_rounds == 3
        assert len(config.agents) == 2

    def test_valid_config_three_agents(self):
        """Test creating a valid debate config with 3 agents."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agents = [
            AgentConfig(
                agent_id=f"agent{i}",
                llm_config=llm_config,
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance="Pro" if i % 2 == 0 else "Con",
                system_prompt="Test",
            )
            for i in range(1, 4)
        ]

        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        config = DebateConfig(
            topic="Test topic", num_rounds=2, agents=agents, judge_config=judge
        )

        assert len(config.agents) == 3

    def test_minimum_agents_validation(self):
        """Test that at least 2 agents are required."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agent1 = AgentConfig(
            agent_id="agent1",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 1",
            stance="Pro",
            system_prompt="Test",
        )
        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        # Only 1 agent - should fail
        with pytest.raises(ValidationError) as exc_info:
            DebateConfig(
                topic="Test", num_rounds=2, agents=[agent1], judge_config=judge
            )
        # Check that validation error is about agents list length
        assert "agents" in str(exc_info.value).lower()
        assert "at least 2" in str(exc_info.value).lower() or "too_short" in str(exc_info.value)

    def test_unique_agent_ids_validation(self):
        """Test that agent IDs must be unique."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        # Both agents have same ID
        agent1 = AgentConfig(
            agent_id="same_id",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 1",
            stance="Pro",
            system_prompt="Test",
        )
        agent2 = AgentConfig(
            agent_id="same_id",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 2",
            stance="Con",
            system_prompt="Test",
        )
        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        with pytest.raises(ValidationError) as exc_info:
            DebateConfig(
                topic="Test",
                num_rounds=2,
                agents=[agent1, agent2],
                judge_config=judge,
            )
        assert "must be unique" in str(exc_info.value)


class TestDebateState:
    """Test DebateState model."""

    def test_create_debate_state(self):
        """Test creating a debate state."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agents = [
            AgentConfig(
                agent_id=f"agent{i}",
                llm_config=llm_config,
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance="Pro" if i % 2 == 0 else "Con",
                system_prompt="Test",
            )
            for i in range(1, 3)
        ]

        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        config = DebateConfig(
            topic="Test topic", num_rounds=2, agents=agents, judge_config=judge
        )

        state = DebateState(config=config)

        assert state.status == DebateStatus.CREATED
        assert state.current_round == 0
        assert len(state.history) == 0
        assert state.debate_id is not None

    def test_add_message_to_state(self):
        """Test adding messages to debate state."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agents = [
            AgentConfig(
                agent_id=f"agent{i}",
                llm_config=llm_config,
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance="Pro" if i % 2 == 0 else "Con",
                system_prompt="Test",
            )
            for i in range(1, 3)
        ]

        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        config = DebateConfig(
            topic="Test", num_rounds=2, agents=agents, judge_config=judge
        )
        state = DebateState(config=config)

        msg = Message(
            agent_id="agent1",
            agent_name="Agent 1",
            content="Test message",
            round_number=1,
            turn_number=0,
            stance="Pro",
        )
        state.add_message(msg)

        assert len(state.history) == 1
        assert state.history[0].agent_id == "agent1"

    def test_get_agent_by_id(self):
        """Test retrieving agent by ID from state."""
        llm_config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        agent1 = AgentConfig(
            agent_id="agent1",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 1",
            stance="Pro",
            system_prompt="Test",
        )
        agent2 = AgentConfig(
            agent_id="agent2",
            llm_config=llm_config,
            role=AgentRole.DEBATER,
            name="Agent 2",
            stance="Con",
            system_prompt="Test",
        )
        judge = AgentConfig(
            agent_id="judge",
            llm_config=llm_config,
            role=AgentRole.JUDGE,
            name="Judge",
            stance="Neutral",
            system_prompt="Test",
        )

        config = DebateConfig(
            topic="Test", num_rounds=2, agents=[agent1, agent2], judge_config=judge
        )
        state = DebateState(config=config)

        found_agent = state.get_agent_by_id("agent1")
        assert found_agent is not None
        assert found_agent.name == "Agent 1"

        not_found = state.get_agent_by_id("nonexistent")
        assert not_found is None
