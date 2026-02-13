"""Anthropic LLM client implementation."""
import logging
from typing import List, Dict

import anthropic
from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) LLM client with retry logic."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            model_name: Model name (e.g., 'claude-3-5-sonnet-20241022')
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized AnthropicClient with model: {model_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (
                anthropic.APIConnectionError,
                anthropic.RateLimitError,
                anthropic.InternalServerError,
            )
        ),
        reraise=True,
    )
    async def send_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Send a message to Claude and return the response.

        Args:
            system_prompt: System prompt defining agent behavior
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Temperature parameter (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Response text from Claude

        Raises:
            anthropic.APIError: If API call fails after retries
        """
        try:
            logger.debug(
                f"Sending message to Anthropic API - Model: {self.model_name}, "
                f"Temp: {temperature}, Max tokens: {max_tokens}"
            )

            response = await self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                text = response.content[0].text
                logger.debug(
                    f"Received response from Anthropic - "
                    f"Input tokens: {response.usage.input_tokens}, "
                    f"Output tokens: {response.usage.output_tokens}"
                )
                return text
            else:
                raise ValueError("Empty response from Anthropic API")

        except anthropic.APIConnectionError as e:
            logger.error(f"Connection error with Anthropic API: {e}")
            raise
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for Anthropic API: {e}")
            raise
        except anthropic.APIStatusError as e:
            logger.error(
                f"Anthropic API error - Status: {e.status_code}, Response: {e.response}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic client: {e}")
            raise

    def get_provider_name(self) -> str:
        """
        Return provider name.

        Returns:
            Provider name
        """
        return "anthropic"
