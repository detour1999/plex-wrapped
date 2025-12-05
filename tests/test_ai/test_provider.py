# ABOUTME: Tests for LLM provider abstraction.
# ABOUTME: Verifies provider selection and interface contract.

import pytest

from plex_wrapped.ai.provider import get_provider, LLMProvider, NoOpProvider
from plex_wrapped.config import LLMConfig


class TestProviderSelection:
    def test_none_provider_returns_noop(self) -> None:
        """Provider 'none' returns NoOpProvider."""
        config = LLMConfig(provider="none")
        provider = get_provider(config)
        assert isinstance(provider, NoOpProvider)

    def test_noop_provider_returns_empty_strings(self) -> None:
        """NoOpProvider returns empty/default content."""
        provider = NoOpProvider()
        result = provider.generate("test prompt")
        assert result == ""


class TestLLMProviderInterface:
    def test_provider_has_generate_method(self) -> None:
        """All providers must have generate method."""
        provider = NoOpProvider()
        assert hasattr(provider, "generate")
        assert callable(provider.generate)
