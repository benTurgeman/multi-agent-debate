"""WebSocket endpoint for real-time debate updates."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from core.exceptions import DebateNotFoundError
from services.debate_manager import DebateEvent, DebateManager
from storage.memory_store import get_debate_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections for debates."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, debate_id: str, websocket: WebSocket) -> None:
        """
        Register a new WebSocket connection for a debate.

        Args:
            debate_id: Debate ID
            websocket: WebSocket connection
        """
        await websocket.accept()

        async with self._lock:
            if debate_id not in self.active_connections:
                self.active_connections[debate_id] = set()
            self.active_connections[debate_id].add(websocket)

        logger.info(
            f"WebSocket connected for debate {debate_id}. "
            f"Total connections: {len(self.active_connections[debate_id])}"
        )

    async def disconnect(self, debate_id: str, websocket: WebSocket) -> None:
        """
        Unregister a WebSocket connection.

        Args:
            debate_id: Debate ID
            websocket: WebSocket connection
        """
        async with self._lock:
            if debate_id in self.active_connections:
                self.active_connections[debate_id].discard(websocket)
                if not self.active_connections[debate_id]:
                    del self.active_connections[debate_id]

        logger.info(f"WebSocket disconnected for debate {debate_id}")

    async def broadcast(self, debate_id: str, message: dict) -> None:
        """
        Broadcast a message to all connected clients for a debate.

        Args:
            debate_id: Debate ID
            message: Message to broadcast
        """
        async with self._lock:
            if debate_id not in self.active_connections:
                return

            connections = list(self.active_connections[debate_id])

        # Send to all connections (outside lock to avoid blocking)
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(
                    f"Error sending message to WebSocket: {e}",
                    exc_info=True,
                )
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                if debate_id in self.active_connections:
                    for connection in disconnected:
                        self.active_connections[debate_id].discard(connection)
                    if not self.active_connections[debate_id]:
                        del self.active_connections[debate_id]

    def get_connection_count(self, debate_id: str) -> int:
        """
        Get number of active connections for a debate.

        Args:
            debate_id: Debate ID

        Returns:
            Number of active connections
        """
        if debate_id not in self.active_connections:
            return 0
        return len(self.active_connections[debate_id])


# Global connection manager
_connection_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def setup_websocket_broadcasting(debate_manager: DebateManager) -> None:
    """
    Set up WebSocket broadcasting for debate events.

    Args:
        debate_manager: Debate manager to attach event handler to
    """
    connection_manager = get_connection_manager()

    def handle_debate_event(event: DebateEvent) -> None:
        """
        Handle debate events and broadcast to WebSocket clients.

        Args:
            event: Debate event
        """
        # Convert payload to JSON-serializable format
        # This handles Pydantic models and datetime objects
        import json
        from pydantic import BaseModel

        def serialize_payload(obj):
            """Recursively serialize payload to JSON-compatible types."""
            if isinstance(obj, BaseModel):
                return obj.model_dump(mode='json')
            elif isinstance(obj, dict):
                return {k: serialize_payload(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_payload(item) for item in obj]
            else:
                return obj

        serialized_payload = serialize_payload(event.payload)

        # Create WebSocket message
        message = {
            "type": event.event_type.value,
            "debate_id": event.debate_id,
            "payload": serialized_payload,
            "timestamp": event.timestamp.isoformat(),
        }

        # Broadcast asynchronously
        # Note: We need to run this in the event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Use ensure_future to schedule the coroutine in the current loop
                asyncio.ensure_future(
                    connection_manager.broadcast(event.debate_id, message),
                    loop=loop
                )
            else:
                loop.run_until_complete(
                    connection_manager.broadcast(event.debate_id, message)
                )
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}", exc_info=True)

    # Register event callback
    debate_manager.register_event_callback(handle_debate_event)


@router.websocket("/api/ws/{debate_id}")
async def websocket_endpoint(websocket: WebSocket, debate_id: str):
    """
    WebSocket endpoint for real-time debate updates.

    Args:
        websocket: WebSocket connection
        debate_id: Debate ID to subscribe to

    Flow:
        1. Verify debate exists
        2. Accept WebSocket connection
        3. Send current debate state
        4. Listen for messages and send real-time updates
        5. Handle disconnection
    """
    connection_manager = get_connection_manager()

    try:
        # Verify debate exists
        store = get_debate_store()
        try:
            debate = await store.get(debate_id)
        except DebateNotFoundError:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Debate {debate_id} not found",
            )
            return

        # Accept connection
        await connection_manager.connect(debate_id, websocket)

        # Send initial state
        await websocket.send_json(
            {
                "type": "connection_established",
                "debate_id": debate_id,
                "payload": {
                    "status": debate.status.value,
                    "current_round": debate.current_round,
                    "current_turn": debate.current_turn,
                    "message_count": len(debate.history),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (for heartbeat/ping)
                data = await websocket.receive_text()

                # Handle ping/pong for keep-alive
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for debate {debate_id}")
                break
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from WebSocket client")
                continue
            except Exception as e:
                logger.error(
                    f"Error in WebSocket receive loop: {e}",
                    exc_info=True,
                )
                break

    except Exception as e:
        logger.error(
            f"Error in WebSocket endpoint for debate {debate_id}: {e}",
            exc_info=True,
        )

    finally:
        # Clean up connection
        await connection_manager.disconnect(debate_id, websocket)
