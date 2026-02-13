"""OpenAI LLM client implementation."""
import logging
from typing import List, Dict

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """OpenAI (GPT) LLM client with retry logic."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model_name: Model name (e.g., 'gpt-4o', 'gpt-4-turbo')
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized OpenAIClient with model: {model_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.InternalServerError,
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
        Send a message to OpenAI and return the response.

        Args:
            system_prompt: System prompt defining agent behavior
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Temperature parameter (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Response text from OpenAI

        Raises:
            openai.APIError: If API call fails after retries
        """
        try:
            logger.debug(
                f"Sending message to OpenAI API - Model: {self.model_name}, "
                f"Temp: {temperature}, Max tokens: {max_tokens}"
            )

            # OpenAI expects system prompt as part of messages array
            full_messages = [{"role": "system", "content": system_prompt}] + messages

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract text from response
            if response.choices and len(response.choices) > 0:
                text = response.choices[0].message.content
                logger.debug(
                    f"Received response from OpenAI - "
                    f"Prompt tokens: {response.usage.prompt_tokens}, "
                    f"Completion tokens: {response.usage.completion_tokens}"
                )
                return text or ""
            else:
                raise ValueError("Empty response from OpenAI API")

        except openai.APIConnectionError as e:
            logger.error(f"Connection error with OpenAI API: {e}")
            raise
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for OpenAI API: {e}")
            raise
        except openai.APIStatusError as e:
            logger.error(
                f"OpenAI API error - Status: {e.status_code}, Response: {e.response}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {e}")
            raise

    def get_provider_name(self) -> str:
        """
        Return provider name.

        Returns:
            Provider name
        """
        return "openai"
