# ABOUTME: Tests for AI content generators.
# ABOUTME: Verifies prompt construction and response parsing.

import pytest

from plex_wrapped.ai.generators import (
    AuraGenerator,
    HotTakesGenerator,
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    SuggestionsGenerator,
    SuperlativesGenerator,
    ThemeGenerator,
)
from plex_wrapped.ai.provider import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing prompt construction."""

    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.last_prompt: str | None = None

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        self.last_prompt = prompt
        return self.response


class TestNarrativeGenerator:
    def test_generates_narrative_from_stats(self) -> None:
        """Narrative generator creates story from user stats."""
        provider = MockProvider('{"narrative": "Your 2024 was wild..."}')
        generator = NarrativeGenerator(provider)

        stats = {
            "total_minutes": 42000,
            "top_artist": "Radiohead",
            "top_genre": "Alternative",
        }
        result = generator.generate(stats)

        assert provider.last_prompt is not None
        assert "42000" in provider.last_prompt
        assert "Radiohead" in provider.last_prompt

    def test_prompt_includes_instruction_for_humor(self) -> None:
        """Prompt asks for playful, humorous tone."""
        provider = MockProvider('{"narrative": "test"}')
        generator = NarrativeGenerator(provider)

        generator.generate({"total_minutes": 100})

        assert "playful" in provider.last_prompt.lower() or "humor" in provider.last_prompt.lower()


class TestPersonalityGenerator:
    def test_generates_personality_type(self) -> None:
        """Personality generator creates type with tagline."""
        response = '''{
            "type": "The Chaos Agent",
            "tagline": "Your playlists have trust issues",
            "description": "You listen to everything...",
            "spirit_animal": "A caffeinated raccoon"
        }'''
        provider = MockProvider(response)
        generator = PersonalityGenerator(provider)

        result = generator.generate({"genres": ["rock", "pop", "jazz"]})

        assert provider.last_prompt is not None


class TestRoastGenerator:
    def test_generates_roasts_from_stats(self) -> None:
        """Roast generator creates playful callouts."""
        response = '{"roasts": ["Your 2am listening habits are concerning"]}'
        provider = MockProvider(response)
        generator = RoastGenerator(provider)

        result = generator.generate({
            "late_night_plays": 200,
            "most_repeated_track": "same song",
        })

        assert provider.last_prompt is not None


class TestSuperlativesGenerator:
    def test_generates_superlatives_from_stats(self) -> None:
        """Superlatives generator creates awards from stats."""
        response = '''{
            "superlatives": [
                {"award": "Most Dedicated Fan", "reason": "Played the same song 200 times"}
            ]
        }'''
        provider = MockProvider(response)
        generator = SuperlativesGenerator(provider)

        result = generator.generate({"top_track_plays": 200})

        assert provider.last_prompt is not None
        assert "superlatives" in provider.last_prompt.lower() or "award" in provider.last_prompt.lower()


class TestHotTakesGenerator:
    def test_generates_hot_takes_from_stats(self) -> None:
        """HotTakes generator creates spicy opinions."""
        response = '{"hot_takes": ["You say you like indie, but your top 10 is basically the radio"]}'
        provider = MockProvider(response)
        generator = HotTakesGenerator(provider)

        result = generator.generate({"top_artists": ["Pop Artist 1", "Pop Artist 2"]})

        assert provider.last_prompt is not None
        assert "hot take" in provider.last_prompt.lower()


class TestThemeGenerator:
    def test_generates_theme_with_palette_and_slides(self) -> None:
        """Theme generator creates colors and per-slide visualizations."""
        response = '''{
            "palette": {
                "primary": "#6366F1",
                "secondary": "#8B5CF6",
                "accent": "#EC4899",
                "background": "#0F172A",
                "text": "#FFFFFF"
            },
            "slides": {
                "intro": {"visualization": "aurora", "mood": "dramatic", "intensity": 0.8}
            }
        }'''
        provider = MockProvider(response)
        generator = ThemeGenerator(provider)

        result = generator.generate({"top_genres": ["rock", "electronic"]})

        assert provider.last_prompt is not None
        assert "palette" in provider.last_prompt.lower()
        assert "visualization" in provider.last_prompt.lower()
        assert result["palette"]["primary"] == "#6366F1"
        assert "intro" in result["slides"]
