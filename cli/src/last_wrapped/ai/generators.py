# ABOUTME: AI content generators for Last Wrapped.
# ABOUTME: Creates narratives, personalities, roasts, and other insights from user stats.

import json
from abc import ABC, abstractmethod
from typing import Any

from last_wrapped.ai.provider import LLMProvider


class BaseGenerator(ABC):
    """Base class for all AI content generators."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @abstractmethod
    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate content from user stats."""
        pass

    def _parse_json(self, response: str) -> dict[str, Any]:
        """Parse JSON response from LLM, handling markdown code blocks."""
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()
        return json.loads(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)


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

        response = self.provider.generate(prompt, max_tokens=1024)
        return self._parse_json(response)
