# ABOUTME: Abstract LLM provider interface with concrete implementations.
# ABOUTME: Factory pattern for creating provider instances based on config.

from abc import ABC, abstractmethod

from last_wrapped.config import LLMConfig


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate content from a prompt.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            Generated text content.
        """
        pass


class NoOpProvider(LLMProvider):
    """Provider that returns empty strings for AI-free mode."""

    def generate(self, prompt: str) -> str:
        """Return empty string without calling any LLM.

        Args:
            prompt: The prompt (ignored).

        Returns:
            Empty string.
        """
        return ""


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key.
            model: Model ID to use.
        """
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate content using Anthropic API.

        Args:
            prompt: The prompt to send to Claude.

        Returns:
            Generated text content.
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's GPT API."""

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key.
            model: Model ID to use.
        """
        import openai

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate content using OpenAI API.

        Args:
            prompt: The prompt to send to GPT.

        Returns:
            Generated text content.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def get_provider(config: LLMConfig) -> LLMProvider:
    """Factory function to create LLM provider from config.

    Args:
        config: LLM configuration containing provider type and credentials.

    Returns:
        Appropriate LLMProvider instance.

    Raises:
        ValueError: If provider type is unsupported.
    """
    if config.provider == "none":
        return NoOpProvider()
    elif config.provider == "anthropic":
        if not config.api_key:
            raise ValueError("Anthropic API key required")
        return AnthropicProvider(api_key=config.api_key, model=config.model)
    elif config.provider == "openai":
        if not config.api_key:
            raise ValueError("OpenAI API key required")
        return OpenAIProvider(api_key=config.api_key, model=config.model)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
