"""
Base agent class with shared LLM client functionality.
"""

import json
from openai import OpenAI, AsyncOpenAI

from src.config import settings


class BaseAgent:
    """
    Base class for AI agents.
    Provides shared OpenAI client and utility methods.
    Supports both sync and async operations.
    """

    def __init__(self):
        """Initialize the agent with OpenAI clients (sync and async)."""
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._async_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Send a chat completion request to OpenAI (sync).

        Args:
            system_prompt: The system message defining agent behavior
            user_prompt: The user message/query
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in the response

        Returns:
            The assistant's response text
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Send a chat completion request expecting JSON response (sync).

        Args:
            system_prompt: The system message defining agent behavior
            user_prompt: The user message/query
            temperature: Sampling temperature
            max_tokens: Maximum tokens in the response

        Returns:
            Parsed JSON response as a dictionary
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    async def _chat_json_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Send a chat completion request expecting JSON response (async).

        Args:
            system_prompt: The system message defining agent behavior
            user_prompt: The user message/query
            temperature: Sampling temperature
            max_tokens: Maximum tokens in the response

        Returns:
            Parsed JSON response as a dictionary
        """
        response = await self._async_client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

