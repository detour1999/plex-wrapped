# ABOUTME: Abstract LLM provider interface with concrete implementations.
# ABOUTME: Factory pattern for creating provider instances based on config.

from abc import ABC, abstractmethod

from plex_wrapped.config import LLMConfig

# Thinking tokens count toward max_tokens, so leave room for them plus the answer.
MAX_OUTPUT_TOKENS = 16000


def _extract_text(content: list) -> str:
    """Join the text blocks of an Anthropic response, skipping thinking blocks.

    Raises:
        ValueError: If the response contains no text block.
    """
    text = "".join(block.text for block in content if block.type == "text")
    if not text:
        raise ValueError("Anthropic response contained no text block")
    return text


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

    def generate_creative_pick(self, prompt: str) -> str:
        """Make one open-ended creative choice with real sampling entropy.

        A provider that can spend a separate, cheaper model at a high temperature on
        this should override it: asking the main model to simulate a "random" choice
        does not produce one, since it just returns its single most likely answer. The
        default falls back to generate(), which uses whatever this provider's normal
        call does.

        Args:
            prompt: An instruction asking for one short, concrete creative choice.

        Returns:
            The chosen text, or "" if the provider has nothing to add.
        """
        return self.generate(prompt)


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

    # A cheap, fast model spent at temperature 1.0 for generate_creative_pick's real
    # sampling entropy; the main model stays on whatever `model` the caller configured.
    CREATIVE_PICK_MODEL = "claude-haiku-4-5"

    def __init__(self, api_key: str, model: str = "claude-sonnet-5") -> None:
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
            max_tokens=MAX_OUTPUT_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_text(message.content)

    def generate_creative_pick(self, prompt: str) -> str:
        """Ask a cheap model at temperature 1.0 for one concrete creative choice.

        Args:
            prompt: An instruction asking for one short, concrete creative choice.

        Returns:
            The chosen text, stripped of surrounding whitespace.
        """
        message = self.client.messages.create(
            model=self.CREATIVE_PICK_MODEL,
            max_tokens=60,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_text(message.content).strip()


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
        if config.model:
            return AnthropicProvider(api_key=config.api_key, model=config.model)
        return AnthropicProvider(api_key=config.api_key)
    elif config.provider == "openai":
        if not config.api_key:
            raise ValueError("OpenAI API key required")
        if config.model:
            return OpenAIProvider(api_key=config.api_key, model=config.model)
        return OpenAIProvider(api_key=config.api_key)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
