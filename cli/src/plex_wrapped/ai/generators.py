# ABOUTME: AI content generators for Plex Wrapped.
# ABOUTME: Creates narratives, personalities, roasts, and other insights from user stats.

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from plex_wrapped.ai.provider import LLMProvider


class BaseGenerator(ABC):
    """Base class for all AI content generators."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @abstractmethod
    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate content from user stats."""
        pass

    def _parse_json(self, response: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """Parse JSON response from LLM with defensive error handling.

        Handles common LLM JSON issues:
        - Markdown code blocks
        - Unescaped newlines in strings
        - Truncated responses

        Args:
            response: Raw LLM response string
            default: Default value to return on parse failure

        Returns:
            Parsed JSON dict or default value
        """
        if default is None:
            default = {}

        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        # Try direct parse first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to fix common issues

        # Fix unescaped newlines inside string values
        # This regex finds string values and escapes literal newlines
        def escape_newlines_in_strings(text: str) -> str:
            result = []
            in_string = False
            escape_next = False
            for char in text:
                if escape_next:
                    result.append(char)
                    escape_next = False
                elif char == '\\':
                    result.append(char)
                    escape_next = True
                elif char == '"':
                    result.append(char)
                    in_string = not in_string
                elif char == '\n' and in_string:
                    result.append('\\n')
                elif char == '\r' and in_string:
                    result.append('\\r')
                else:
                    result.append(char)
            return ''.join(result)

        try:
            fixed = escape_newlines_in_strings(response)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Try to find and extract JSON object from response
        match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Return default if all else fails
        return default


class NarrativeGenerator(BaseGenerator):
    """Generates a narrative story of the user's year in music."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate narrative from user stats."""
        prompt = f"""You are writing a Last.fm Wrapped narrative for a user's 2024 listening year.

User Stats:
{json.dumps(stats, indent=2)}

Create a playful, humorous narrative that tells the story of their year through music.
Make it personal, fun, and slightly irreverent - like Spotify Wrapped but with more personality.

Return ONLY valid JSON in this format:
{{
    "narrative": "Your 2024 musical journey..."
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {"narrative": "Your musical journey was too epic to put into words."})


class PersonalityGenerator(BaseGenerator):
    """Generates a music personality type based on listening habits."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate personality type from user stats."""
        prompt = f"""You are creating a music personality type for a Last.fm user based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create a funny, creative personality type that captures their listening patterns. Think Myers-Briggs meets music taste.

Return ONLY valid JSON in this format:
{{
    "type": "The Chaos Agent",
    "tagline": "Your playlists have trust issues",
    "description": "You listen to everything...",
    "spirit_animal": "A caffeinated raccoon"
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "type": "The Mystery Listener",
            "tagline": "Your taste defies classification",
            "description": "We couldn't quite figure you out, but that's probably a compliment.",
            "spirit_animal": "A sphinx"
        })


class RoastGenerator(BaseGenerator):
    """Generates playful roasts based on listening habits."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate roasts from user stats."""
        prompt = f"""You are creating playful roasts for a Last.fm user based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create 3-5 funny, light-hearted roasts about their music taste or listening patterns.
Keep it fun and not mean-spirited - like friendly banter.

Return ONLY valid JSON in this format:
{{
    "roasts": [
        "Your 2am listening habits are concerning",
        "Another roast here..."
    ]
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "roasts": ["Your music taste is so unique, we couldn't even roast it properly."]
        })


class AuraGenerator(BaseGenerator):
    """Generates a music aura color and description."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate aura from user stats."""
        prompt = f"""You are creating a "music aura" for a Last.fm user based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create a creative aura color and vibe that represents their musical energy. Think astrology but for music taste.

Return ONLY valid JSON in this format:
{{
    "color": "Midnight Purple",
    "hex": "#9B59B6",
    "vibe": "Mysterious and moody",
    "description": "Your aura radiates..."
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "color": "Cosmic Purple",
            "hex": "#9B59B6",
            "vibe": "Enigmatic and eclectic",
            "description": "Your musical energy transcends simple description."
        })


class SuperlativesGenerator(BaseGenerator):
    """Generates fun superlatives and awards."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate superlatives from user stats."""
        prompt = f"""You are creating music superlatives/awards for a Last.fm user based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create 3-5 funny, creative awards like "Most Likely To..." or "Best..." based on their listening patterns.

Return ONLY valid JSON in this format:
{{
    "superlatives": [
        {{
            "award": "Most Dedicated Fan",
            "reason": "Played the same song 200 times"
        }}
    ]
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "superlatives": [
                {"award": "Most Dedicated Listener", "reason": "You showed up for your music"}
            ]
        })


class HotTakesGenerator(BaseGenerator):
    """Generates spicy hot takes about the user's music taste."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate hot takes from user stats."""
        prompt = f"""You are creating "hot takes" about a Last.fm user's music taste based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create 3-5 bold, funny opinions or observations about their music taste.
Make them slightly controversial but playful.

Return ONLY valid JSON in this format:
{{
    "hot_takes": [
        "You say you like indie, but your top 10 is basically the radio",
        "Another hot take..."
    ]
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "hot_takes": ["Your music taste is impeccable and we have no notes."]
        })


class SuggestionsGenerator(BaseGenerator):
    """Generates personalized music suggestions and predictions."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate suggestions from user stats."""
        prompt = f"""You are creating personalized music suggestions for a Last.fm user based on their 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Create 3-5 recommendations or predictions about what they should listen to next, or what their 2025 might look like.
Make them fun and personalized.

Return ONLY valid JSON in this format:
{{
    "suggestions": [
        "Based on your late-night listening, try: Artist Name",
        "Another suggestion..."
    ]
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(response, {
            "suggestions": ["Keep doing what you're doing - your taste is already excellent."]
        })


class ThemeGenerator(BaseGenerator):
    """Generates visual theme with color palette and per-slide visualizations."""

    AVAILABLE_VISUALIZATIONS = [
        {"id": "gradient_blob", "name": "Gradient Blob", "bestFor": ["warm", "introspective", "calm"]},
        {"id": "particles", "name": "Particles", "bestFor": ["celebratory", "reflective", "dreamy"]},
        {"id": "aurora", "name": "Aurora", "bestFor": ["dramatic", "mystical", "epic"]},
    ]

    SLIDES = [
        "intro", "totalTime", "topArtist", "topTracks", "listeningClock",
        "quirkyStats", "personality", "aura", "roasts", "narrative", "share"
    ]

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate theme from user stats."""
        viz_info = json.dumps(self.AVAILABLE_VISUALIZATIONS, indent=2)
        slides_list = json.dumps(self.SLIDES)

        prompt = f"""You are creating a visual theme for a Last.fm Wrapped experience based on the user's 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Available Visualizations:
{viz_info}

Slides to configure: {slides_list}

Based on the user's music taste and personality, create:
1. A color palette (5 colors) that reflects their musical vibe
2. A visualization type and mood for each slide

Moods can be: dramatic, mystical, warm, introspective, celebratory, reflective, energetic, playful, chaotic, analytical, triumphant

Return ONLY valid JSON in this format:
{{
    "palette": {{
        "primary": "#hexcolor",
        "secondary": "#hexcolor",
        "accent": "#hexcolor",
        "background": "#hexcolor",
        "text": "#ffffff"
    }},
    "slides": {{
        "intro": {{"visualization": "aurora", "mood": "dramatic", "intensity": 0.8}},
        "totalTime": {{"visualization": "particles", "mood": "celebratory", "intensity": 0.6}},
        "topArtist": {{"visualization": "gradient_blob", "mood": "warm", "intensity": 0.7}},
        "topTracks": {{"visualization": "particles", "mood": "energetic", "intensity": 0.5}},
        "listeningClock": {{"visualization": "aurora", "mood": "analytical", "intensity": 0.4}},
        "quirkyStats": {{"visualization": "particles", "mood": "playful", "intensity": 0.6}},
        "personality": {{"visualization": "gradient_blob", "mood": "introspective", "intensity": 0.7}},
        "aura": {{"visualization": "aurora", "mood": "mystical", "intensity": 0.9}},
        "roasts": {{"visualization": "particles", "mood": "chaotic", "intensity": 0.8}},
        "narrative": {{"visualization": "gradient_blob", "mood": "reflective", "intensity": 0.3}},
        "share": {{"visualization": "aurora", "mood": "triumphant", "intensity": 0.7}}
    }}
}}
"""

        response = self.provider.generate(prompt)
        default_theme = {
            "palette": {
                "primary": "#6366F1",
                "secondary": "#8B5CF6",
                "accent": "#EC4899",
                "background": "#0F172A",
                "text": "#FFFFFF"
            },
            "slides": {
                "intro": {"visualization": "aurora", "mood": "dramatic", "intensity": 0.8},
                "totalTime": {"visualization": "particles", "mood": "celebratory", "intensity": 0.6},
                "topArtist": {"visualization": "gradient_blob", "mood": "warm", "intensity": 0.7},
                "topTracks": {"visualization": "particles", "mood": "energetic", "intensity": 0.5},
                "listeningClock": {"visualization": "aurora", "mood": "analytical", "intensity": 0.4},
                "quirkyStats": {"visualization": "particles", "mood": "playful", "intensity": 0.6},
                "personality": {"visualization": "gradient_blob", "mood": "introspective", "intensity": 0.7},
                "aura": {"visualization": "aurora", "mood": "mystical", "intensity": 0.9},
                "roasts": {"visualization": "particles", "mood": "chaotic", "intensity": 0.8},
                "narrative": {"visualization": "gradient_blob", "mood": "reflective", "intensity": 0.3},
                "share": {"visualization": "aurora", "mood": "triumphant", "intensity": 0.7}
            }
        }
        return self._parse_json(response, default_theme)
