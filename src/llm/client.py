import os
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict], response_format=None) -> str:
        """Complete the conversation and return the response as a string."""
        pass


class OpenAIClient(BaseLLMClient):
    """Wraps OpenAI AsyncOpenAI. Supports native JSON mode."""
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("MODEL_DEV", "gpt-4o-mini")

    async def complete(self, messages: list[dict], response_format=None) -> str:
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            # OpenAI supports response_format natively
            kwargs["response_format"] = response_format

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class AnthropicClient(BaseLLMClient):
    """
    Wraps Anthropic AsyncAnthropic.
    No native JSON mode — inject system prompt instead.
    """
    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("MODEL_DEV", "claude-3-5-haiku-20241022")

    async def complete(self, messages: list[dict], response_format=None) -> str:
        # Inject JSON-only instruction for Anthropic
        system_msg = "You are a helpful assistant. Respond only with valid JSON. No preamble, no markdown, no code blocks."
        
        # Anthropic separates system from messages
        system = next((m["content"] for m in messages if m["role"] == "system"), system_msg)
        if response_format and response_format.get("type") == "json_object":
            system = system + "\n\nIMPORTANT: Respond ONLY with a valid JSON object, no other text."
        
        anthropic_messages = [m for m in messages if m["role"] != "system"]
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=anthropic_messages,
        )
        return response.content[0].text


class GroqClient(BaseLLMClient):
    """
    Wraps Groq client.
    Supports JSON mode for some models (llama3 series).
    """
    def __init__(self):
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("MODEL_DEV", "llama-3.1-8b-instant")

    async def complete(self, messages: list[dict], response_format=None) -> str:
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            # Groq supports JSON mode for llama3 models
            kwargs["response_format"] = response_format

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


def get_llm_client() -> BaseLLMClient:
    provider = os.getenv("LLM_PROVIDER", "openai")
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    elif provider == "groq":
        return GroqClient()
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
