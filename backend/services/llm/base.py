"""Base LLM client interface."""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMClient(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def send_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Send a message to the LLM and return the response.

        Args:
            system_prompt: System prompt defining agent behavior
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Temperature parameter for response randomness (0.0-2.0)
            max_tokens: Maximum tokens in the response

        Returns:
            Response text from the LLM

        Raises:
            Exception: If API call fails after retries
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the provider name for logging and identification.

        Returns:
            Provider name (e.g., "anthropic", "openai")
        """
        pass
