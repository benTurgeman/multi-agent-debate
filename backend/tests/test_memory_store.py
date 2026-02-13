"""Tests for memory storage."""
import pytest

from core.exceptions import DebateNotFoundError, StorageError
from models.agent import AgentConfig, AgentRole
from models.debate import DebateConfig, DebateState
from models.llm import LLMConfig, ModelProvider
from storage.memory_store import MemoryDebateStore, get_debate_store


@pytest.fixture
def store():
    """Create a fresh memory store for each test."""
    return MemoryDebateStore()


@pytest.fixture
def sample_debate_config():
    """Create a sample debate configuration."""
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

    return DebateConfig(
        topic="Test topic", num_rounds=2, agents=[agent1, agent2], judge_config=judge
    )


@pytest.fixture
def sample_debate_state(sample_debate_config):
    """Create a sample debate state."""
    return DebateState(config=sample_debate_config)


class TestMemoryDebateStore:
    """Test MemoryDebateStore class."""

    @pytest.mark.asyncio
    async def test_create_debate(self, store, sample_debate_state):
        """Test creating a debate in storage."""
        result = await store.create(sample_debate_state)

        assert result.debate_id == sample_debate_state.debate_id
        assert result.config.topic == "Test topic"

    @pytest.mark.asyncio
    async def test_create_duplicate_debate(self, store, sample_debate_state):
        """Test that creating a debate with duplicate ID raises error."""
        await store.create(sample_debate_state)

        # Try to create again with same ID
        with pytest.raises(StorageError) as exc_info:
            await store.create(sample_debate_state)
        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_debate(self, store, sample_debate_state):
        """Test retrieving a debate by ID."""
        await store.create(sample_debate_state)

        result = await store.get(sample_debate_state.debate_id)

        assert result.debate_id == sample_debate_state.debate_id
        assert result.config.topic == "Test topic"

    @pytest.mark.asyncio
    async def test_get_nonexistent_debate(self, store):
        """Test that getting a nonexistent debate raises error."""
        with pytest.raises(DebateNotFoundError) as exc_info:
            await store.get("nonexistent_id")
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_debate(self, store, sample_debate_state):
        """Test updating a debate."""
        # Create debate
        await store.create(sample_debate_state)

        # Modify and update
        sample_debate_state.current_round = 1
        result = await store.update(sample_debate_state)

        assert result.current_round == 1

        # Verify it was updated in storage
        retrieved = await store.get(sample_debate_state.debate_id)
        assert retrieved.current_round == 1

    @pytest.mark.asyncio
    async def test_update_nonexistent_debate(self, store, sample_debate_state):
        """Test that updating a nonexistent debate raises error."""
        with pytest.raises(DebateNotFoundError) as exc_info:
            await store.update(sample_debate_state)
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_debate(self, store, sample_debate_state):
        """Test deleting a debate."""
        # Create debate
        await store.create(sample_debate_state)

        # Delete it
        await store.delete(sample_debate_state.debate_id)

        # Verify it's gone
        with pytest.raises(DebateNotFoundError):
            await store.get(sample_debate_state.debate_id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_debate(self, store):
        """Test that deleting a nonexistent debate raises error."""
        with pytest.raises(DebateNotFoundError) as exc_info:
            await store.delete("nonexistent_id")
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_all_empty(self, store):
        """Test listing debates when store is empty."""
        result = await store.list_all()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_all_multiple_debates(self, store, sample_debate_config):
        """Test listing all debates."""
        # Create multiple debates
        debate1 = DebateState(config=sample_debate_config)
        debate2 = DebateState(config=sample_debate_config)

        await store.create(debate1)
        await store.create(debate2)

        result = await store.list_all()

        assert len(result) == 2
        debate_ids = {d.debate_id for d in result}
        assert debate1.debate_id in debate_ids
        assert debate2.debate_id in debate_ids

    @pytest.mark.asyncio
    async def test_exists(self, store, sample_debate_state):
        """Test checking if a debate exists."""
        # Should not exist initially
        assert not await store.exists(sample_debate_state.debate_id)

        # Create debate
        await store.create(sample_debate_state)

        # Should exist now
        assert await store.exists(sample_debate_state.debate_id)

        # Delete debate
        await store.delete(sample_debate_state.debate_id)

        # Should not exist anymore
        assert not await store.exists(sample_debate_state.debate_id)

    @pytest.mark.asyncio
    async def test_clear(self, store, sample_debate_config):
        """Test clearing all debates."""
        # Create multiple debates
        debate1 = DebateState(config=sample_debate_config)
        debate2 = DebateState(config=sample_debate_config)

        await store.create(debate1)
        await store.create(debate2)

        # Verify they exist
        assert len(await store.list_all()) == 2

        # Clear storage
        await store.clear()

        # Verify empty
        assert len(await store.list_all()) == 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, store, sample_debate_config):
        """Test thread-safety with concurrent operations."""
        import asyncio

        # Create multiple debates concurrently
        debates = [DebateState(config=sample_debate_config) for _ in range(5)]

        # Create all debates concurrently
        await asyncio.gather(*[store.create(d) for d in debates])

        # Verify all were created
        all_debates = await store.list_all()
        assert len(all_debates) == 5

        # Update all concurrently
        for debate in debates:
            debate.current_round = 1

        await asyncio.gather(*[store.update(d) for d in debates])

        # Verify all were updated
        all_debates = await store.list_all()
        assert all(d.current_round == 1 for d in all_debates)


def test_get_debate_store_singleton():
    """Test that get_debate_store returns the same instance."""
    store1 = get_debate_store()
    store2 = get_debate_store()
    assert store1 is store2
