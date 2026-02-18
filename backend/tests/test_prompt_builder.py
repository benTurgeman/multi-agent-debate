"""Tests for prompt building utilities."""
import pytest
from datetime import datetime, timezone

from models.agent import AgentConfig, AgentRole
from models.llm import LLMConfig, ModelProvider
from models.message import Message
from services.prompt_builder import (
    build_debater_prompt,
    build_judge_prompt,
    format_history_for_context,
    format_history_for_judge,
    create_user_message,
)


@pytest.fixture
def sample_llm_config():
    """Create a sample LLM config."""
    return LLMConfig(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet-20241022",
        api_key_env_var="ANTHROPIC_API_KEY",
    )


@pytest.fixture
def sample_agent(sample_llm_config):
    """Create a sample agent config."""
    return AgentConfig(
        agent_id="agent1",
        llm_config=sample_llm_config,
        role=AgentRole.DEBATER,
        name="Tech Optimist",
        stance="Pro",
        system_prompt="You are an optimistic technologist who believes AI will benefit humanity.",
        temperature=1.0,
        max_tokens=1024,
    )


@pytest.fixture
def sample_judge_config(sample_llm_config):
    """Create a sample judge config."""
    return AgentConfig(
        agent_id="judge",
        llm_config=sample_llm_config,
        role=AgentRole.JUDGE,
        name="Impartial Judge",
        stance="Neutral",
        system_prompt="You are a fair and impartial debate judge.",
        temperature=0.7,
        max_tokens=2048,
    )


@pytest.fixture
def sample_messages():
    """Create sample debate messages."""
    return [
        Message(
            agent_id="agent1",
            agent_name="Tech Optimist",
            content="AI will revolutionize healthcare and save millions of lives.",
            round_number=1,
            turn_number=0,
            stance="Pro",
            timestamp=datetime.now(timezone.utc),
        ),
        Message(
            agent_id="agent2",
            agent_name="AI Skeptic",
            content="AI poses significant risks including job displacement and privacy concerns.",
            round_number=1,
            turn_number=1,
            stance="Con",
            timestamp=datetime.now(timezone.utc),
        ),
    ]


class TestBuildDebaterPrompt:
    """Tests for debater prompt building."""

    def test_build_debater_prompt(self, sample_agent):
        """Test building a debater system prompt."""
        topic = "AI will benefit humanity more than harm it"
        current_round = 2
        total_rounds = 3

        prompt = build_debater_prompt(
            agent=sample_agent,
            topic=topic,
            current_round=current_round,
            total_rounds=total_rounds,
        )

        # Check that all components are present
        assert sample_agent.system_prompt in prompt
        assert topic in prompt
        assert sample_agent.stance in prompt
        assert f"{current_round} of {total_rounds}" in prompt
        assert "DEBATE CONTEXT:" in prompt
        assert "INSTRUCTIONS:" in prompt
        assert "200-400 words" in prompt

    def test_build_debater_prompt_structure(self, sample_agent):
        """Test that the prompt has proper structure."""
        prompt = build_debater_prompt(
            agent=sample_agent, topic="Test topic", current_round=1, total_rounds=3
        )

        # Should not have leading/trailing whitespace
        assert prompt == prompt.strip()
        # Should contain key sections
        assert "DEBATE CONTEXT:" in prompt
        assert "INSTRUCTIONS:" in prompt


class TestBuildJudgePrompt:
    """Tests for judge prompt building."""

    def test_build_judge_prompt(self, sample_judge_config, sample_llm_config):
        """Test building a judge system prompt."""
        topic = "AI will benefit humanity"
        agents = [
            AgentConfig(
                agent_id="agent1",
                llm_config=sample_llm_config,
                role=AgentRole.DEBATER,
                name="Optimist",
                stance="Pro",
                system_prompt="Test",
                temperature=1.0,
                max_tokens=1024,
            ),
            AgentConfig(
                agent_id="agent2",
                llm_config=sample_llm_config,
                role=AgentRole.DEBATER,
                name="Skeptic",
                stance="Con",
                system_prompt="Test",
                temperature=1.0,
                max_tokens=1024,
            ),
        ]

        prompt = build_judge_prompt(
            topic=topic, agents=agents, judge_config=sample_judge_config
        )

        # Check components
        assert sample_judge_config.system_prompt in prompt
        assert topic in prompt
        assert "Optimist (Pro)" in prompt
        assert "Skeptic (Con)" in prompt
        assert "DEBATE TOPIC:" in prompt
        assert "PARTICIPANTS:" in prompt
        assert "TASK:" in prompt
        assert "JSON format" in prompt
        assert "agent_scores" in prompt
        assert "winner_id" in prompt

    def test_build_judge_prompt_multiple_agents(
        self, sample_judge_config, sample_llm_config
    ):
        """Test judge prompt with multiple agents."""
        agents = [
            AgentConfig(
                agent_id=f"agent{i}",
                llm_config=sample_llm_config,
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance=f"Stance {i}",
                system_prompt="Test",
                temperature=1.0,
                max_tokens=1024,
            )
            for i in range(1, 4)
        ]

        prompt = build_judge_prompt(
            topic="Test topic", agents=agents, judge_config=sample_judge_config
        )

        # All agents should be listed
        for agent in agents:
            assert f"{agent.name} ({agent.stance})" in prompt


class TestFormatHistoryForContext:
    """Tests for formatting debate history for context."""

    def test_format_history_empty(self):
        """Test formatting with no history."""
        context = format_history_for_context(
            history=[], topic="Test topic", current_round=1, total_rounds=3
        )

        assert "Test topic" in context
        assert "ROUND: 1 of 3" in context
        assert "No previous messages" in context
        assert "opening statement" in context

    def test_format_history_with_messages(self, sample_messages):
        """Test formatting with message history."""
        context = format_history_for_context(
            history=sample_messages, topic="AI debate", current_round=2, total_rounds=3
        )

        assert "AI debate" in context
        assert "ROUND: 2 of 3" in context
        assert "Tech Optimist (Pro)" in context
        assert "AI Skeptic (Con)" in context
        assert "revolutionize healthcare" in context
        assert "job displacement" in context
        assert "YOUR TURN:" in context

    def test_format_history_message_order(self, sample_messages):
        """Test that messages are in correct order."""
        context = format_history_for_context(
            history=sample_messages, topic="Test", current_round=2, total_rounds=3
        )

        # First message should appear before second
        optimist_pos = context.find("Tech Optimist")
        skeptic_pos = context.find("AI Skeptic")
        assert optimist_pos < skeptic_pos

    def test_format_history_includes_round_and_turn(self, sample_messages):
        """Test that round and turn numbers are included."""
        context = format_history_for_context(
            history=sample_messages, topic="Test", current_round=2, total_rounds=3
        )

        assert "[Round 1, Turn 1]" in context
        assert "[Round 1, Turn 2]" in context


class TestFormatHistoryForJudge:
    """Tests for formatting history for judge evaluation."""

    def test_format_history_for_judge(self, sample_messages):
        """Test formatting complete history for judge."""
        topic = "AI debate topic"
        context = format_history_for_judge(history=sample_messages, topic=topic)

        assert topic in context
        assert "FULL TRANSCRIPT:" in context
        assert "Tech Optimist (Pro)" in context
        assert "AI Skeptic (Con)" in context
        assert "revolutionize healthcare" in context
        assert "job displacement" in context
        assert "Please evaluate" in context
        assert "JSON format" in context

    def test_format_history_for_judge_separator(self, sample_messages):
        """Test that messages are separated properly."""
        context = format_history_for_judge(history=sample_messages, topic="Test")

        # Should have separator between messages
        assert "---" in context

    def test_format_history_for_judge_empty(self):
        """Test formatting with empty history."""
        context = format_history_for_judge(history=[], topic="Test topic")

        assert "Test topic" in context
        assert "FULL TRANSCRIPT:" in context


class TestCreateUserMessage:
    """Tests for creating user messages."""

    def test_create_user_message(self):
        """Test creating a user message dict."""
        content = "This is a test message"
        message = create_user_message(content)

        assert message["role"] == "user"
        assert message["content"] == content
        assert len(message) == 2

    def test_create_user_message_empty(self):
        """Test creating an empty user message."""
        message = create_user_message("")

        assert message["role"] == "user"
        assert message["content"] == ""
