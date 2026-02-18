"""In-memory storage for debates with thread-safe operations."""
import asyncio
from typing import Dict, List, Optional

from core.exceptions import DebateNotFoundError, StorageError
from models.debate import DebateState


class MemoryDebateStore:
    """Thread-safe in-memory storage for debates."""

    def __init__(self):
        """Initialize the memory store."""
        self._debates: Dict[str, DebateState] = {}
        self._lock = asyncio.Lock()

    async def create(self, debate: DebateState) -> DebateState:
        """
        Create a new debate in storage.

        Args:
            debate: Debate state to store

        Returns:
            Stored debate state

        Raises:
            StorageError: If debate with same ID already exists
        """
        async with self._lock:
            if debate.debate_id in self._debates:
                raise StorageError(f"Debate with ID {debate.debate_id} already exists")
            self._debates[debate.debate_id] = debate
            return debate

    async def get(self, debate_id: str) -> DebateState:
        """
        Get a debate by ID.

        Args:
            debate_id: ID of the debate to retrieve

        Returns:
            Debate state

        Raises:
            DebateNotFoundError: If debate does not exist
        """
        async with self._lock:
            if debate_id not in self._debates:
                raise DebateNotFoundError(f"Debate with ID {debate_id} not found")
            return self._debates[debate_id]

    async def update(self, debate: DebateState) -> DebateState:
        """
        Update an existing debate.

        Args:
            debate: Updated debate state

        Returns:
            Updated debate state

        Raises:
            DebateNotFoundError: If debate does not exist
        """
        async with self._lock:
            if debate.debate_id not in self._debates:
                raise DebateNotFoundError(
                    f"Debate with ID {debate.debate_id} not found"
                )
            self._debates[debate.debate_id] = debate
            return debate

    async def delete(self, debate_id: str) -> None:
        """
        Delete a debate.

        Args:
            debate_id: ID of the debate to delete

        Raises:
            DebateNotFoundError: If debate does not exist
        """
        async with self._lock:
            if debate_id not in self._debates:
                raise DebateNotFoundError(f"Debate with ID {debate_id} not found")
            del self._debates[debate_id]

    async def list_all(self) -> List[DebateState]:
        """
        List all debates.

        Returns:
            List of all debate states
        """
        async with self._lock:
            return list(self._debates.values())

    async def exists(self, debate_id: str) -> bool:
        """
        Check if a debate exists.

        Args:
            debate_id: ID of the debate to check

        Returns:
            True if debate exists, False otherwise
        """
        async with self._lock:
            return debate_id in self._debates

    async def clear(self) -> None:
        """Clear all debates from storage (useful for testing)."""
        async with self._lock:
            self._debates.clear()


# Global instance for use across the application
_debate_store: Optional[MemoryDebateStore] = None


def get_debate_store() -> MemoryDebateStore:
    """
    Get the global debate store instance.

    Returns:
        MemoryDebateStore instance
    """
    global _debate_store
    if _debate_store is None:
        _debate_store = MemoryDebateStore()
    return _debate_store
