"""Edge case tests for the debate system."""
import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from core.exceptions import LLMClientError
from main import app
from models.agent import AgentConfig, AgentRole
from models.debate import DebateConfig, DebateStatus
from models.llm import LLMConfig, ModelProvider
from storage.memory_store import get_debate_store


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_storage(event_loop):
    """Clear storage before and after each test."""
    store = get_debate_store()
    event_loop.run_until_complete(store.clear())
    yield
    event_loop.run_until_complete(store.clear())


class TestLargeNumberOfAgents:
    """Test debates with many agents."""

    def test_debate_with_ten_agents(self, client: TestClient):
        """Test creating a debate with 10 agents."""
        agents = [
            AgentConfig(
                agent_id=f"agent_{i}",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance=f"Position {i}",
                system_prompt=f"You are agent {i}.",
                temperature=1.0,
                max_tokens=512,
            )
            for i in range(10)
        ]

        config = DebateConfig(
            topic="A debate with many participants",
            num_rounds=1,
            agents=agents,
            judge_config=AgentConfig(
                agent_id="judge",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.JUDGE,
                name="Judge",
                stance="Neutral",
                system_prompt="You are a judge.",
                temperature=0.7,
                max_tokens=2048,
            ),
        )

        response = client.post("/api/debates", json={"config": config.model_dump()})
        assert response.status_code == 201
        assert "debate_id" in response.json()

    def test_debate_with_fifteen_agents(self, client: TestClient):
        """Test creating a debate with 15 agents (stress test)."""
        agents = [
            AgentConfig(
                agent_id=f"agent_{i}",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name=f"Agent {i}",
                stance=f"Position {i}",
                system_prompt=f"You are agent {i}.",
                temperature=1.0,
                max_tokens=256,
            )
            for i in range(15)
        ]

        config = DebateConfig(
            topic="A debate with many participants",
            num_rounds=1,
            agents=agents,
            judge_config=AgentConfig(
                agent_id="judge",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.JUDGE,
                name="Judge",
                stance="Neutral",
                system_prompt="You are a judge.",
                temperature=0.7,
                max_tokens=2048,
            ),
        )

        response = client.post("/api/debates", json={"config": config.model_dump()})
        assert response.status_code == 201
        assert "debate_id" in response.json()


class TestInvalidInputs:
    """Test handling of invalid inputs."""

    def test_debate_with_negative_rounds(self, client: TestClient):
        """Test creating a debate with negative rounds."""
        config = {
            "topic": "Test topic",
            "num_rounds": -1,
            "agents": [
                {
                    "agent_id": "agent1",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 1",
                    "stance": "Pro",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
                {
                    "agent_id": "agent2",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 2",
                    "stance": "Con",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
            ],
            "judge_config": {
                "agent_id": "judge",
                "llm_config": {
                    "provider": "anthropic",
                    "model_name": "claude-3-5-sonnet-20241022",
                    "api_key_env_var": "ANTHROPIC_API_KEY",
                },
                "role": "judge",
                "name": "Judge",
                "stance": "Neutral",
                "system_prompt": "Judge",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": config})
        assert response.status_code == 422  # Validation error

    def test_debate_with_zero_rounds(self, client: TestClient):
        """Test creating a debate with zero rounds."""
        config = {
            "topic": "Test topic",
            "num_rounds": 0,
            "agents": [
                {
                    "agent_id": "agent1",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 1",
                    "stance": "Pro",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
                {
                    "agent_id": "agent2",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 2",
                    "stance": "Con",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
            ],
            "judge_config": {
                "agent_id": "judge",
                "llm_config": {
                    "provider": "anthropic",
                    "model_name": "claude-3-5-sonnet-20241022",
                    "api_key_env_var": "ANTHROPIC_API_KEY",
                },
                "role": "judge",
                "name": "Judge",
                "stance": "Neutral",
                "system_prompt": "Judge",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": config})
        assert response.status_code == 422  # Validation error

    def test_debate_with_invalid_temperature(self, client: TestClient):
        """Test creating a debate with temperature outside valid range."""
        config = {
            "topic": "Test topic",
            "num_rounds": 1,
            "agents": [
                {
                    "agent_id": "agent1",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 1",
                    "stance": "Pro",
                    "system_prompt": "Test",
                    "temperature": 3.0,  # Invalid: > 2.0
                    "max_tokens": 1024,
                },
                {
                    "agent_id": "agent2",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 2",
                    "stance": "Con",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
            ],
            "judge_config": {
                "agent_id": "judge",
                "llm_config": {
                    "provider": "anthropic",
                    "model_name": "claude-3-5-sonnet-20241022",
                    "api_key_env_var": "ANTHROPIC_API_KEY",
                },
                "role": "judge",
                "name": "Judge",
                "stance": "Neutral",
                "system_prompt": "Judge",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": config})
        assert response.status_code == 422  # Validation error

    def test_debate_with_duplicate_agent_ids(self, client: TestClient):
        """Test creating a debate with duplicate agent IDs."""
        config = {
            "topic": "Test topic",
            "num_rounds": 1,
            "agents": [
                {
                    "agent_id": "agent1",  # Duplicate
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 1",
                    "stance": "Pro",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
                {
                    "agent_id": "agent1",  # Duplicate
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 2",
                    "stance": "Con",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
            ],
            "judge_config": {
                "agent_id": "judge",
                "llm_config": {
                    "provider": "anthropic",
                    "model_name": "claude-3-5-sonnet-20241022",
                    "api_key_env_var": "ANTHROPIC_API_KEY",
                },
                "role": "judge",
                "name": "Judge",
                "stance": "Neutral",
                "system_prompt": "Judge",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": config})
        assert response.status_code == 422  # Validation error

    def test_debate_with_empty_topic(self, client: TestClient):
        """Test creating a debate with empty topic (allowed but not recommended)."""
        config = {
            "topic": "",  # Empty - allowed but edge case
            "num_rounds": 1,
            "agents": [
                {
                    "agent_id": "agent1",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 1",
                    "stance": "Pro",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
                {
                    "agent_id": "agent2",
                    "llm_config": {
                        "provider": "anthropic",
                        "model_name": "claude-3-5-sonnet-20241022",
                        "api_key_env_var": "ANTHROPIC_API_KEY",
                    },
                    "role": "debater",
                    "name": "Agent 2",
                    "stance": "Con",
                    "system_prompt": "Test",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                },
            ],
            "judge_config": {
                "agent_id": "judge",
                "llm_config": {
                    "provider": "anthropic",
                    "model_name": "claude-3-5-sonnet-20241022",
                    "api_key_env_var": "ANTHROPIC_API_KEY",
                },
                "role": "judge",
                "name": "Judge",
                "stance": "Neutral",
                "system_prompt": "Judge",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": config})
        # Empty topic is allowed (edge case)
        assert response.status_code == 201


class TestAPIFailures:
    """Test handling of API failures during debate execution."""

    @patch("services.llm.factory.create_llm_client")
    def test_debate_with_llm_api_failure(
        self, mock_create_client, client: TestClient
    ):
        """Test debate handling when LLM API fails."""
        # Mock LLM client that always fails
        mock_client = Mock()
        mock_client.send_message = AsyncMock(
            side_effect=LLMClientError("API connection failed")
        )
        mock_client.get_provider_name = Mock(return_value="mock_provider")
        mock_create_client.return_value = mock_client

        # Create debate config
        config = DebateConfig(
            topic="Test debate",
            num_rounds=1,
            agents=[
                AgentConfig(
                    agent_id="agent1",
                    llm_config=LLMConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-3-5-sonnet-20241022",
                        api_key_env_var="ANTHROPIC_API_KEY",
                    ),
                    role=AgentRole.DEBATER,
                    name="Agent 1",
                    stance="Pro",
                    system_prompt="Test",
                    temperature=1.0,
                    max_tokens=1024,
                ),
                AgentConfig(
                    agent_id="agent2",
                    llm_config=LLMConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-3-5-sonnet-20241022",
                        api_key_env_var="ANTHROPIC_API_KEY",
                    ),
                    role=AgentRole.DEBATER,
                    name="Agent 2",
                    stance="Con",
                    system_prompt="Test",
                    temperature=1.0,
                    max_tokens=1024,
                ),
            ],
            judge_config=AgentConfig(
                agent_id="judge",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.JUDGE,
                name="Judge",
                stance="Neutral",
                system_prompt="Judge",
                temperature=0.7,
                max_tokens=2048,
            ),
        )

        # Create debate
        response = client.post("/api/debates", json={"config": config.model_dump()})
        assert response.status_code == 201
        debate_id = response.json()["debate_id"]

        # Start debate (should fail but handle gracefully)
        response = client.post(f"/api/debates/{debate_id}/start")
        assert response.status_code == 202

        # Wait a bit for background task
        import time
        time.sleep(2)

        # Check debate status - should be FAILED
        async def check_status():
            store = get_debate_store()
            debate = await store.get(debate_id)
            return debate.status

        status = asyncio.run(check_status())
        assert status == DebateStatus.FAILED

    def test_retry_mechanism_unit(self):
        """Test that retry mechanism is configured correctly (unit test)."""
        from services.llm.anthropic_client import AnthropicClient
        from services.llm.openai_client import OpenAIClient
        import inspect

        # Check that retry decorators are applied
        # Anthropic client should have retry decorator
        assert hasattr(AnthropicClient.send_message, "__wrapped__")

        # OpenAI client should have retry decorator
        assert hasattr(OpenAIClient.send_message, "__wrapped__")


class TestConcurrentOperations:
    """Test concurrent operations on debates."""

    def test_concurrent_status_checks(self, client: TestClient):
        """Test multiple concurrent status checks on the same debate."""
        import concurrent.futures

        # Create debate
        config = DebateConfig(
            topic="Test concurrent access",
            num_rounds=1,
            agents=[
                AgentConfig(
                    agent_id="agent1",
                    llm_config=LLMConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-3-5-sonnet-20241022",
                        api_key_env_var="ANTHROPIC_API_KEY",
                    ),
                    role=AgentRole.DEBATER,
                    name="Agent 1",
                    stance="Pro",
                    system_prompt="Test",
                    temperature=1.0,
                    max_tokens=1024,
                ),
                AgentConfig(
                    agent_id="agent2",
                    llm_config=LLMConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-3-5-sonnet-20241022",
                        api_key_env_var="ANTHROPIC_API_KEY",
                    ),
                    role=AgentRole.DEBATER,
                    name="Agent 2",
                    stance="Con",
                    system_prompt="Test",
                    temperature=1.0,
                    max_tokens=1024,
                ),
            ],
            judge_config=AgentConfig(
                agent_id="judge",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.JUDGE,
                name="Judge",
                stance="Neutral",
                system_prompt="Judge",
                temperature=0.7,
                max_tokens=2048,
            ),
        )

        response = client.post("/api/debates", json={"config": config.model_dump()})
        debate_id = response.json()["debate_id"]

        # Make concurrent status requests
        def check_status():
            return client.get(f"/api/debates/{debate_id}/status")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_status) for _ in range(20)]
            results = [f.result() for f in futures]

        # All should succeed
        for result in results:
            assert result.status_code == 200
            assert result.json()["debate_id"] == debate_id
