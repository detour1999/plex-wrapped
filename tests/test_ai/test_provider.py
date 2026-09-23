# ABOUTME: Tests for LLM provider abstraction.
# ABOUTME: Verifies provider selection and interface contract.

import os
from unittest.mock import MagicMock

import pytest
from anthropic.types import Message, TextBlock, ThinkingBlock, Usage

from plex_wrapped.ai.generators import AuraGenerator
from plex_wrapped.ai.provider import (
    AnthropicProvider,
    MAX_OUTPUT_TOKENS,
    _extract_text,
    get_provider,
    LLMProvider,
    NoOpProvider,
)
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


def text(value: str) -> TextBlock:
    return TextBlock(type="text", text=value)


def thinking(value: str) -> ThinkingBlock:
    return ThinkingBlock(type="thinking", thinking=value, signature="sig")


class TestExtractText:
    def test_returns_text_when_a_thinking_block_comes_first(self) -> None:
        """Current models can lead with a thinking block; the answer is the text block."""
        assert _extract_text([thinking("hmm"), text('{"ok": true}')]) == '{"ok": true}'

    def test_returns_text_when_there_is_no_thinking_block(self) -> None:
        assert _extract_text([text("hello")]) == "hello"

    def test_joins_multiple_text_blocks(self) -> None:
        assert _extract_text([text("one "), thinking("x"), text("two")]) == "one two"

    def test_raises_when_the_response_has_no_text(self) -> None:
        """A thinking-only response (e.g. cut off by max_tokens) is an error, not a crash on .text."""
        with pytest.raises(ValueError, match="no text"):
            _extract_text([thinking("still thinking")])


class TestAnthropicProviderDefaults:
    def test_default_model_is_current(self) -> None:
        assert AnthropicProvider(api_key="unused").model == "claude-sonnet-5"

    def test_output_budget_leaves_room_for_thinking(self) -> None:
        """Thinking tokens count toward max_tokens, so 1024 truncates generated JSON."""
        assert MAX_OUTPUT_TOKENS >= 16000


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="needs ANTHROPIC_API_KEY")
class TestAnthropicProviderLive:
    def test_real_generator_round_trips_through_the_default_model(self) -> None:
        """End to end: a real generator prompt through the real API returns parsed JSON."""
        provider = AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"])
        stats = {
            "user": "tester",
            "year": 2025,
            "total": {"total_minutes": 1200.0},
            "top_artists": [{"name": "Radiohead", "plays": 40}],
        }

        result = AuraGenerator(provider).generate(stats)

        assert result.get("hex", "").startswith("#")
        assert result.get("vibe")


def anthropic_message(content: list) -> Message:
    return Message(
        id="msg_1",
        type="message",
        role="assistant",
        model="m",
        content=content,
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


class TestGenerateCreativePickDefault:
    def test_falls_back_to_generate_when_not_overridden(self) -> None:
        """A provider that only implements generate() still answers a creative-pick request."""

        class MinimalProvider(LLMProvider):
            def generate(self, prompt: str, max_tokens: int = 1024) -> str:
                return f"echo: {prompt}"

        provider = MinimalProvider()

        assert provider.generate_creative_pick("invent something") == "echo: invent something"


class TestAnthropicProviderCreativePick:
    def test_uses_a_separate_cheap_model_at_high_temperature(self) -> None:
        """Real sampling entropy (a hot, cheap model) makes the pick, not the main model."""
        provider = AnthropicProvider(api_key="unused")
        provider.client = MagicMock()
        provider.client.messages.create.return_value = anthropic_message(
            [text("a lit match at midnight")]
        )

        result = provider.generate_creative_pick("invent a conceit")

        assert result == "a lit match at midnight"
        _, kwargs = provider.client.messages.create.call_args
        assert kwargs["model"] != provider.model
        assert kwargs["temperature"] == 1.0
        assert kwargs["max_tokens"] < 200

    def test_strips_surrounding_whitespace(self) -> None:
        provider = AnthropicProvider(api_key="unused")
        provider.client = MagicMock()
        provider.client.messages.create.return_value = anthropic_message(
            [text("  a pick with padding  \n")]
        )

        assert provider.generate_creative_pick("invent a conceit") == "a pick with padding"

    def test_skips_thinking_blocks_like_the_main_generate_call(self) -> None:
        provider = AnthropicProvider(api_key="unused")
        provider.client = MagicMock()
        provider.client.messages.create.return_value = anthropic_message(
            [thinking("mulling it over"), text("a decision")]
        )

        assert provider.generate_creative_pick("invent a conceit") == "a decision"
