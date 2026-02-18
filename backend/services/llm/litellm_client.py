"""LiteLLM unified client implementation."""
import logging
from typing import List, Dict, Optional

import litellm
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class LiteLLMClient(BaseLLMClient):
    """Unified LLM client using LiteLLM for all providers."""

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """
        Initialize LiteLLM client.

        Args:
            model_name: Model name in format "provider/model" (e.g., 'anthropic/claude-3-5-sonnet-20241022')
            api_key: API key for the provider (optional for local models like Ollama)
            api_base: Base URL for the API (optional, used for Ollama and other local models)
        """
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base

        # Extract provider name from model string (e.g., "anthropic/claude-3-5-sonnet" -> "anthropic")
        self.provider = model_name.split("/")[0] if "/" in model_name else "unknown"

        logger.info(
            f"Initialized LiteLLMClient - Model: {model_name}, "
            f"Provider: {self.provider}, API Base: {api_base or 'default'}"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (
                litellm.RateLimitError,
                litellm.ServiceUnavailableError,
                litellm.APIConnectionError,
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
        Send a message to the LLM and return the response.

        Args:
            system_prompt: System prompt defining agent behavior
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Temperature parameter (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Response text from the LLM

        Raises:
            litellm.APIError: If API call fails after retries
        """
        try:
            logger.debug(
                f"Sending message to LiteLLM - Model: {self.model_name}, "
                f"Provider: {self.provider}, Temp: {temperature}, Max tokens: {max_tokens}"
            )

            # Prepare messages with system prompt
            full_messages = [{"role": "system", "content": system_prompt}] + messages

            # Prepare kwargs for litellm.acompletion
            completion_kwargs = {
                "model": self.model_name,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # Add optional parameters
            if self.api_key:
                completion_kwargs["api_key"] = self.api_key
            if self.api_base:
                completion_kwargs["api_base"] = self.api_base

            # Call LiteLLM
            response = await litellm.acompletion(**completion_kwargs)

            # Extract text from response
            if response.choices and len(response.choices) > 0:
                text = response.choices[0].message.content

                # Log usage if available
                if hasattr(response, "usage") and response.usage:
                    logger.debug(
                        f"Received response from {self.provider} - "
                        f"Prompt tokens: {response.usage.prompt_tokens}, "
                        f"Completion tokens: {response.usage.completion_tokens}, "
                        f"Total tokens: {response.usage.total_tokens}"
                    )
                else:
                    logger.debug(f"Received response from {self.provider}")

                return text
            else:
                raise ValueError(f"Empty response from {self.provider} via LiteLLM")

        except litellm.AuthenticationError as e:
            logger.error(f"Authentication error with {self.provider}: {e}")
            raise Exception(f"Authentication failed for {self.provider}: {str(e)}")
        except litellm.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for {self.provider}: {e}")
            raise
        except litellm.ContextWindowExceededError as e:
            logger.error(f"Context window exceeded for {self.provider}: {e}")
            raise Exception(f"Message too long for {self.provider}: {str(e)}")
        except litellm.BadRequestError as e:
            logger.error(f"Bad request to {self.provider}: {e}")
            raise Exception(f"Invalid request to {self.provider}: {str(e)}")
        except litellm.ServiceUnavailableError as e:
            logger.error(f"Service unavailable for {self.provider}: {e}")
            raise
        except litellm.APIConnectionError as e:
            logger.error(f"Connection error with {self.provider}: {e}")
            raise
        except litellm.APIError as e:
            logger.error(f"API error from {self.provider}: {e}")
            raise Exception(f"API error from {self.provider}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in LiteLLM client ({self.provider}): {e}")
            raise

    def get_provider_name(self) -> str:
        """
        Return the provider name for logging and identification.

        Returns:
            Provider name (e.g., "anthropic", "openai", "ollama")
        """
        return self.provider
