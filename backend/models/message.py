"""Message models for debate communication."""
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a debate."""

    agent_id: str = Field(..., description="ID of the agent that sent this message")
    agent_name: str = Field(..., description="Display name of the agent")
    content: str = Field(..., description="Message content/response")
    round_number: int = Field(..., ge=1, description="Round number (1-indexed)")
    turn_number: int = Field(
        ..., ge=0, description="Turn number within the round (0-indexed)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the message was created",
    )
    stance: str = Field(..., description="Agent's stance in the debate")


class MessageHistory(BaseModel):
    """Collection of messages in a debate."""

    messages: List[Message] = Field(
        default_factory=list, description="List of messages"
    )

    def add_message(self, message: Message) -> None:
        """
        Add a message to the history.

        Args:
            message: Message to add
        """
        self.messages.append(message)

    def get_messages_for_round(self, round_number: int) -> List[Message]:
        """
        Get all messages for a specific round.

        Args:
            round_number: Round number to filter by

        Returns:
            List of messages in the specified round
        """
        return [msg for msg in self.messages if msg.round_number == round_number]

    def get_all_messages(self) -> List[Message]:
        """
        Get all messages in chronological order.

        Returns:
            List of all messages
        """
        return self.messages
