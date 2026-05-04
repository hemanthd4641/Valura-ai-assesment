import os
from abc import ABC, abstractmethod
from openai import AsyncOpenAI

class BaseLLMClient(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict], response_format=None) -> str:
        """Complete the conversation."""
        pass

class OpenAIClient(BaseLLMClient):
    """Wraps OpenAI AsyncOpenAI."""
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("MODEL_DEV", "gpt-4o-mini")

    async def complete(self, messages: list[dict], response_format=None) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            kwargs["response_format"] = response_format
            
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

class AnthropicClient(BaseLLMClient):
    """Wraps Anthropic AsyncAnthropic."""
    async def complete(self, messages: list[dict], response_format=None) -> str:
        # Implementation for Anthropic if needed
        raise NotImplementedError("AnthropicClient not implemented yet")

class GroqClient(BaseLLMClient):
    """Wraps Groq client."""
    async def complete(self, messages: list[dict], response_format=None) -> str:
        # Implementation for Groq if needed
        raise NotImplementedError("GroqClient not implemented yet")

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
