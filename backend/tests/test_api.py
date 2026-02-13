"""Tests for REST API endpoints and WebSocket functionality."""
import asyncio
import json
from typing import Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from models.agent import AgentConfig, AgentRole
from models.debate import DebateConfig, DebateStatus
from models.llm import LLMConfig, ModelProvider
from storage.memory_store import get_debate_store


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def clear_storage(event_loop):
    """Clear storage before and after each test."""
    store = get_debate_store()
    event_loop.run_until_complete(store.clear())
    yield
    event_loop.run_until_complete(store.clear())


@pytest.fixture
def sample_debate_config() -> DebateConfig:
    """Create a sample debate configuration."""
    return DebateConfig(
        topic="AI will benefit humanity more than harm it",
        num_rounds=2,
        agents=[
            AgentConfig(
                agent_id="optimist",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Tech Optimist",
                stance="Pro",
                system_prompt="You are an optimistic technologist.",
                temperature=1.0,
                max_tokens=1024,
            ),
            AgentConfig(
                agent_id="skeptic",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="AI Skeptic",
                stance="Con",
                system_prompt="You are a cautious critic.",
                temperature=0.9,
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
            name="Impartial Judge",
            stance="Neutral",
            system_prompt="You are a fair debate judge.",
            temperature=0.7,
            max_tokens=2048,
        ),
    )


class TestDebateEndpoints:
    """Test debate REST API endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_create_debate(self, client: TestClient, sample_debate_config: DebateConfig):
        """Test creating a new debate."""
        response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )

        assert response.status_code == 201
        data = response.json()
        assert "debate_id" in data
        assert data["status"] == DebateStatus.CREATED.value
        assert data["message"] == "Debate created successfully"

    def test_create_debate_invalid_config(self, client: TestClient):
        """Test creating debate with invalid configuration."""
        # Only one agent (should require minimum 2)
        invalid_config = {
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
                    "system_prompt": "Test prompt",
                    "temperature": 1.0,
                    "max_tokens": 1024,
                }
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
                "system_prompt": "Judge prompt",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        }

        response = client.post("/api/debates", json={"config": invalid_config})
        assert response.status_code == 422  # Validation error

    def test_list_debates_empty(self, client: TestClient):
        """Test listing debates when none exist."""
        response = client.get("/api/debates")
        assert response.status_code == 200
        data = response.json()
        assert data["debates"] == []
        assert data["total"] == 0

    def test_list_debates(self, client: TestClient, sample_debate_config: DebateConfig):
        """Test listing debates."""
        # Create two debates
        client.post("/api/debates", json={"config": sample_debate_config.model_dump()})
        client.post("/api/debates", json={"config": sample_debate_config.model_dump()})

        response = client.get("/api/debates")
        assert response.status_code == 200
        data = response.json()
        assert len(data["debates"]) == 2
        assert data["total"] == 2

    def test_get_debate(self, client: TestClient, sample_debate_config: DebateConfig):
        """Test getting a specific debate."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Get debate
        response = client.get(f"/api/debates/{debate_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["debate"]["debate_id"] == debate_id
        assert data["debate"]["status"] == DebateStatus.CREATED.value

    def test_get_debate_not_found(self, client: TestClient):
        """Test getting a non-existent debate."""
        response = client.get("/api/debates/nonexistent-id")
        assert response.status_code == 404

    def test_get_debate_status(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test getting debate status."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Get status
        response = client.get(f"/api/debates/{debate_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["debate_id"] == debate_id
        assert data["status"] == DebateStatus.CREATED.value
        assert data["current_round"] == 0
        assert data["current_turn"] == 0
        assert data["total_rounds"] == 2
        assert data["message_count"] == 0

    def test_start_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test starting a debate."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Start debate (will run in background)
        response = client.post(f"/api/debates/{debate_id}/start")
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert data["debate_id"] == debate_id
        assert "WebSocket" in data["message"]

    def test_start_debate_not_found(self, client: TestClient):
        """Test starting a non-existent debate."""
        response = client.post("/api/debates/nonexistent-id/start")
        assert response.status_code == 404

    def test_start_debate_already_in_progress(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test starting a debate that's already in progress."""
        # Create and start debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]
        client.post(f"/api/debates/{debate_id}/start")

        # Give it a moment to start
        import time
        time.sleep(0.1)

        # Try to start again
        response = client.post(f"/api/debates/{debate_id}/start")
        # Should be either 400 (already in progress) or 202 (if it finished quickly)
        assert response.status_code in [400, 202]

    def test_delete_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test deleting a debate."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Delete debate
        response = client.delete(f"/api/debates/{debate_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/debates/{debate_id}")
        assert get_response.status_code == 404

    def test_delete_debate_not_found(self, client: TestClient):
        """Test deleting a non-existent debate."""
        response = client.delete("/api/debates/nonexistent-id")
        assert response.status_code == 404

    def test_export_debate_json(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test exporting debate as JSON."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Export as JSON
        response = client.get(f"/api/debates/{debate_id}/export?format=json")
        assert response.status_code == 200
        data = response.json()
        assert "debate" in data
        assert data["debate"]["debate_id"] == debate_id

    def test_export_debate_markdown(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test exporting debate as Markdown."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Export as Markdown
        response = client.get(f"/api/debates/{debate_id}/export?format=markdown")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        content = response.text
        assert "# Debate:" in content
        assert sample_debate_config.topic in content

    def test_export_debate_text(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test exporting debate as plain text."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Export as text
        response = client.get(f"/api/debates/{debate_id}/export?format=text")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        content = response.text
        assert "DEBATE:" in content
        assert sample_debate_config.topic in content

    def test_export_debate_not_found(self, client: TestClient):
        """Test exporting a non-existent debate."""
        response = client.get("/api/debates/nonexistent-id/export?format=json")
        assert response.status_code == 404


class TestWebSocket:
    """Test WebSocket functionality."""

    def test_websocket_connection(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test WebSocket connection establishment."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Connect to WebSocket
        with client.websocket_connect(f"/api/ws/{debate_id}") as websocket:
            # Should receive connection established message
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert data["debate_id"] == debate_id
            assert "payload" in data
            assert data["payload"]["status"] == DebateStatus.CREATED.value

    def test_websocket_connection_debate_not_found(self, client: TestClient):
        """Test WebSocket connection with non-existent debate."""
        with pytest.raises(Exception):  # Should fail to connect
            with client.websocket_connect("/api/ws/nonexistent-id") as websocket:
                pass

    def test_websocket_ping_pong(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test WebSocket ping/pong for keep-alive."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Connect to WebSocket
        with client.websocket_connect(f"/api/ws/{debate_id}") as websocket:
            # Receive connection message
            websocket.receive_json()

            # Send ping
            websocket.send_json({"type": "ping"})

            # Should receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data

    def test_websocket_invalid_json(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test WebSocket handles invalid JSON gracefully."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Connect to WebSocket
        with client.websocket_connect(f"/api/ws/{debate_id}") as websocket:
            # Receive connection message
            websocket.receive_json()

            # Send invalid JSON
            websocket.send_text("not valid json {")

            # Send valid ping to ensure connection is still alive
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_multiple_connections(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test multiple WebSocket connections to the same debate."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Connect multiple WebSockets
        with client.websocket_connect(f"/api/ws/{debate_id}") as ws1:
            ws1.receive_json()  # Connection established

            with client.websocket_connect(f"/api/ws/{debate_id}") as ws2:
                ws2.receive_json()  # Connection established

                # Both should be connected
                # Send ping to first connection
                ws1.send_json({"type": "ping"})
                data1 = ws1.receive_json()
                assert data1["type"] == "pong"

                # Send ping to second connection
                ws2.send_json({"type": "ping"})
                data2 = ws2.receive_json()
                assert data2["type"] == "pong"

    def test_connection_manager_get_connection_count(self):
        """Test ConnectionManager.get_connection_count()."""
        from routers.websocket import ConnectionManager

        manager = ConnectionManager()

        # Test with non-existent debate
        count = manager.get_connection_count("nonexistent-debate")
        assert count == 0

    @patch("services.llm.factory.create_llm_client")
    def test_websocket_receives_debate_events(
        self,
        mock_create_client,
        client: TestClient,
        sample_debate_config: DebateConfig,
    ):
        """Test that WebSocket receives debate events."""
        # Mock LLM client
        mock_client = Mock()
        mock_client.send_message = AsyncMock(
            return_value="This is a test response from the agent."
        )
        mock_client.get_provider_name = Mock(return_value="mock_provider")
        mock_create_client.return_value = mock_client

        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Connect to WebSocket
        with client.websocket_connect(f"/api/ws/{debate_id}") as websocket:
            # Receive connection message
            websocket.receive_json()

            # Start debate
            client.post(f"/api/debates/{debate_id}/start")

            # Should receive debate_started event
            # Note: This is a basic test - in practice, events may be async
            # and might require more sophisticated testing with async websockets

            # Close connection
            websocket.close()

    def test_connection_manager_broadcast_to_disconnected(self):
        """Test broadcasting when a connection fails."""
        import asyncio
        from routers.websocket import ConnectionManager
        from unittest.mock import AsyncMock, MagicMock

        async def run_test():
            manager = ConnectionManager()

            # Create mock websockets
            good_ws = MagicMock()
            good_ws.accept = AsyncMock()
            good_ws.send_json = AsyncMock()

            bad_ws = MagicMock()
            bad_ws.accept = AsyncMock()
            bad_ws.send_json = AsyncMock(side_effect=Exception("Connection broken"))

            # Add connections
            debate_id = "test-debate"
            await manager.connect(debate_id, good_ws)
            await manager.connect(debate_id, bad_ws)

            # Broadcast message
            await manager.broadcast(debate_id, {"type": "test", "data": "message"})

            # Good connection should have received the message
            good_ws.send_json.assert_called_once()

            # Bad connection should have been attempted
            bad_ws.send_json.assert_called_once()

            # Bad connection should be removed
            count = manager.get_connection_count(debate_id)
            assert count == 1  # Only good connection remains

        asyncio.run(run_test())


class TestExportFormats:
    """Test export format generation."""

    def test_markdown_export_with_messages(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test markdown export includes all sections."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Export
        response = client.get(f"/api/debates/{debate_id}/export?format=markdown")
        content = response.text

        # Check for required sections
        assert "# Debate:" in content
        assert "## Participants" in content
        assert "Tech Optimist" in content
        assert "AI Skeptic" in content
        assert "## Debate Transcript" in content

    def test_text_export_with_messages(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test text export includes all sections."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Export
        response = client.get(f"/api/debates/{debate_id}/export?format=text")
        content = response.text

        # Check for required sections
        assert "DEBATE:" in content
        assert "PARTICIPANTS:" in content
        assert "Tech Optimist" in content
        assert "AI Skeptic" in content
        assert "DEBATE TRANSCRIPT:" in content

    def test_markdown_export_with_complete_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test markdown export with messages and judge results."""
        import asyncio
        from storage.memory_store import get_debate_store
        from models.message import Message
        from models.judge import JudgeResult, AgentScore
        from datetime import datetime, timezone

        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Add messages and judge result
        async def populate_debate():
            store = get_debate_store()
            debate = await store.get(debate_id)

            # Add messages
            debate.history = [
                Message(
                    agent_id="optimist",
                    agent_name="Tech Optimist",
                    stance="Pro",
                    content="AI will bring great benefits to humanity.",
                    round_number=1,
                    turn_number=0,
                    timestamp=datetime.now(timezone.utc),
                ),
                Message(
                    agent_id="skeptic",
                    agent_name="AI Skeptic",
                    stance="Con",
                    content="We must be cautious about AI risks.",
                    round_number=1,
                    turn_number=1,
                    timestamp=datetime.now(timezone.utc),
                ),
            ]

            # Add judge result
            debate.judge_result = JudgeResult(
                summary="Both sides presented compelling arguments.",
                agent_scores=[
                    AgentScore(
                        agent_id="optimist",
                        agent_name="Tech Optimist",
                        score=8.5,
                        reasoning="Strong logical arguments with good examples.",
                    ),
                    AgentScore(
                        agent_id="skeptic",
                        agent_name="AI Skeptic",
                        score=7.8,
                        reasoning="Valid concerns but less comprehensive.",
                    ),
                ],
                winner_id="optimist",
                winner_name="Tech Optimist",
                key_arguments=[
                    "AI can solve major problems",
                    "Risks must be carefully managed",
                ],
            )

            debate.status = DebateStatus.COMPLETED
            await store.update(debate)

        asyncio.run(populate_debate())

        # Export as markdown
        response = client.get(f"/api/debates/{debate_id}/export?format=markdown")
        content = response.text

        # Check for all sections
        assert "# Debate:" in content
        assert "## Participants" in content
        assert "## Debate Transcript" in content
        assert "### Round 1" in content
        assert "Tech Optimist (Pro):" in content
        assert "AI Skeptic (Con):" in content
        assert "AI will bring great benefits" in content
        assert "We must be cautious" in content
        assert "## Judge's Decision" in content
        assert "**Winner:** Tech Optimist" in content
        assert "### Summary" in content
        assert "Both sides presented compelling arguments" in content
        assert "### Scores" in content
        assert "8.5/10" in content
        assert "7.8/10" in content
        assert "### Key Arguments" in content
        assert "AI can solve major problems" in content

    def test_text_export_with_complete_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test text export with messages and judge results."""
        import asyncio
        from storage.memory_store import get_debate_store
        from models.message import Message
        from models.judge import JudgeResult, AgentScore
        from datetime import datetime, timezone

        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Add messages and judge result
        async def populate_debate():
            store = get_debate_store()
            debate = await store.get(debate_id)

            # Add messages
            debate.history = [
                Message(
                    agent_id="optimist",
                    agent_name="Tech Optimist",
                    stance="Pro",
                    content="AI will revolutionize healthcare.",
                    round_number=1,
                    turn_number=0,
                    timestamp=datetime.now(timezone.utc),
                ),
                Message(
                    agent_id="skeptic",
                    agent_name="AI Skeptic",
                    stance="Con",
                    content="AI poses existential risks.",
                    round_number=1,
                    turn_number=1,
                    timestamp=datetime.now(timezone.utc),
                ),
            ]

            # Add judge result
            debate.judge_result = JudgeResult(
                summary="A balanced debate on AI's impact.",
                agent_scores=[
                    AgentScore(
                        agent_id="optimist",
                        agent_name="Tech Optimist",
                        score=9.0,
                        reasoning="Excellent use of evidence.",
                    ),
                    AgentScore(
                        agent_id="skeptic",
                        agent_name="AI Skeptic",
                        score=8.0,
                        reasoning="Strong critical analysis.",
                    ),
                ],
                winner_id="optimist",
                winner_name="Tech Optimist",
                key_arguments=[
                    "Healthcare improvements",
                    "Risk management needed",
                ],
            )

            debate.status = DebateStatus.COMPLETED
            await store.update(debate)

        asyncio.run(populate_debate())

        # Export as text
        response = client.get(f"/api/debates/{debate_id}/export?format=text")
        content = response.text

        # Check for all sections
        assert "DEBATE:" in content
        assert "PARTICIPANTS:" in content
        assert "DEBATE TRANSCRIPT:" in content
        assert "ROUND 1" in content
        assert "Tech Optimist (Pro):" in content
        assert "AI Skeptic (Con):" in content
        assert "AI will revolutionize healthcare" in content
        assert "AI poses existential risks" in content
        assert "JUDGE'S DECISION:" in content
        assert "Winner: Tech Optimist" in content
        assert "Summary:" in content
        assert "A balanced debate on AI's impact" in content
        assert "Scores:" in content
        assert "9.0/10" in content
        assert "8.0/10" in content
        assert "Key Arguments:" in content
        assert "Healthcare improvements" in content


class TestErrorHandling:
    """Test error handling in API endpoints."""

    def test_invalid_debate_id_format(self, client: TestClient):
        """Test handling of malformed debate IDs."""
        # /api/debates/ actually maps to list endpoint (200)
        # Test with truly invalid path
        response = client.get("/api/debates/invalid@id#format")
        assert response.status_code == 404  # Not found

    def test_concurrent_debate_creation(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test creating multiple debates concurrently."""
        # Create multiple debates
        responses = []
        for _ in range(5):
            response = client.post(
                "/api/debates",
                json={"config": sample_debate_config.model_dump()},
            )
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

        # All should have unique IDs
        debate_ids = [r.json()["debate_id"] for r in responses]
        assert len(set(debate_ids)) == 5

    def test_delete_already_deleted_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test deleting a debate that was already deleted."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Delete once
        response1 = client.delete(f"/api/debates/{debate_id}")
        assert response1.status_code == 204

        # Delete again - should fail
        response2 = client.delete(f"/api/debates/{debate_id}")
        assert response2.status_code == 404

    @patch("storage.memory_store.MemoryDebateStore.create")
    def test_create_debate_storage_error(
        self, mock_create, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test handling of storage errors during debate creation."""
        from core.exceptions import StorageError

        # Mock storage error
        mock_create.side_effect = StorageError("Database connection failed")

        response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        assert response.status_code == 400
        assert "Database connection failed" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.create")
    def test_create_debate_generic_error(
        self, mock_create, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test handling of generic errors during debate creation."""
        # Mock generic error
        mock_create.side_effect = Exception("Unexpected error")

        response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        assert response.status_code == 500
        assert "Failed to create debate" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.list_all")
    def test_list_debates_error(self, mock_list_all, client: TestClient):
        """Test handling of errors when listing debates."""
        # Mock error
        mock_list_all.side_effect = Exception("Database error")

        response = client.get("/api/debates")
        assert response.status_code == 500
        assert "Failed to list debates" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.get")
    def test_get_debate_generic_error(self, mock_get, client: TestClient):
        """Test handling of generic errors when getting a debate."""
        # Mock error
        mock_get.side_effect = Exception("Database error")

        response = client.get("/api/debates/some-id")
        assert response.status_code == 500
        assert "Failed to retrieve debate" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.get")
    def test_get_status_not_found(self, mock_get, client: TestClient):
        """Test getting status of non-existent debate."""
        from core.exceptions import DebateNotFoundError

        mock_get.side_effect = DebateNotFoundError("Debate not found")

        response = client.get("/api/debates/nonexistent/status")
        assert response.status_code == 404

    @patch("storage.memory_store.MemoryDebateStore.get")
    def test_get_status_generic_error(self, mock_get, client: TestClient):
        """Test handling of generic errors when getting debate status."""
        # Mock error
        mock_get.side_effect = Exception("Database error")

        response = client.get("/api/debates/some-id/status")
        assert response.status_code == 500
        assert "Failed to retrieve debate status" in response.json()["detail"]

    def test_start_completed_debate(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test starting a debate that has already completed."""
        from storage.memory_store import get_debate_store
        from services.debate_manager import DebateManager
        import asyncio

        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Manually set status to COMPLETED
        async def mark_completed():
            store = get_debate_store()
            debate = await store.get(debate_id)
            debate.status = DebateStatus.COMPLETED
            await store.update(debate)

        asyncio.run(mark_completed())

        # Try to start
        response = client.post(f"/api/debates/{debate_id}/start")
        assert response.status_code == 400
        assert "already completed" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.get")
    def test_start_debate_generic_error(self, mock_get, client: TestClient):
        """Test handling of generic errors when starting a debate."""
        # Mock error
        mock_get.side_effect = Exception("Database error")

        response = client.post("/api/debates/some-id/start")
        assert response.status_code == 500
        assert "Failed to start debate" in response.json()["detail"]

    def test_export_unsupported_format(
        self, client: TestClient, sample_debate_config: DebateConfig
    ):
        """Test exporting with unsupported format."""
        # Create debate
        create_response = client.post(
            "/api/debates",
            json={"config": sample_debate_config.model_dump()},
        )
        debate_id = create_response.json()["debate_id"]

        # Try to export with invalid format (this will be validated by query param type)
        # Instead test with a format that passes validation but isn't handled
        # Actually, the Literal type will prevent this, so we test the error path differently
        response = client.get(f"/api/debates/{debate_id}/export?format=invalid")
        # FastAPI will return 422 for invalid Literal value
        assert response.status_code == 422

    @patch("storage.memory_store.MemoryDebateStore.get")
    def test_export_debate_generic_error(self, mock_get, client: TestClient):
        """Test handling of generic errors when exporting a debate."""
        # Mock error
        mock_get.side_effect = Exception("Database error")

        response = client.get("/api/debates/some-id/export?format=json")
        assert response.status_code == 500
        assert "Failed to export debate" in response.json()["detail"]

    @patch("storage.memory_store.MemoryDebateStore.delete")
    def test_delete_debate_generic_error(self, mock_delete, client: TestClient):
        """Test handling of generic errors when deleting a debate."""
        # Mock error
        mock_delete.side_effect = Exception("Database error")

        response = client.delete("/api/debates/some-id")
        assert response.status_code == 500
        assert "Failed to delete debate" in response.json()["detail"]
