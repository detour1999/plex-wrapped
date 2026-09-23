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

    @staticmethod
    def _wrapped_year(stats: dict[str, Any]) -> int:
        """Return the year being wrapped, failing clearly if stats lack it."""
        year = stats.get("year")
        if year is None:
            raise ValueError("stats must include the 'year' being wrapped")
        return year

    def _creative_pick(self, instruction: str) -> str:
        """Delegate one open-ended creative choice to the provider's highest-entropy path.

        Asking the main generation call to simulate a "random" choice does not produce
        one - it just returns whatever it considers most likely. generate_creative_pick
        can spend a separate, cheaper model at a high temperature instead, which gives
        real sampling variation. The instruction must not name this project's domain
        (music, listening, Wrapped): naming it collapses picks onto a handful of
        recap-shaped tropes regardless of what varies the request.

        Returns "" if the provider has nothing to add (e.g. a no-op provider), so
        callers can skip the directive rather than inject an empty one.
        """
        return self.provider.generate_creative_pick(instruction).strip()

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
                elif char == "\\":
                    result.append(char)
                    escape_next = True
                elif char == '"':
                    result.append(char)
                    in_string = not in_string
                elif char == "\n" and in_string:
                    result.append("\\n")
                elif char == "\r" and in_string:
                    result.append("\\r")
                else:
                    result.append(char)
            return "".join(result)

        # Drop trailing commas before a closing brace or bracket, leaving strings alone
        def remove_trailing_commas(text: str) -> str:
            result = []
            in_string = False
            escape_next = False
            for i, char in enumerate(text):
                if escape_next:
                    escape_next = False
                elif in_string and char == "\\":
                    escape_next = True
                elif char == '"':
                    in_string = not in_string
                elif char == "," and not in_string:
                    following = text[i + 1 :].lstrip()
                    if following[:1] in ("}", "]"):
                        continue
                result.append(char)
            return "".join(result)

        try:
            fixed = remove_trailing_commas(escape_newlines_in_strings(response))
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Try to find and extract JSON object from response
        match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
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
        year = self._wrapped_year(stats)

        conceit = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected structural conceit or narrative "
            "device for telling a story. Reply with ONLY the conceit, nothing else, no "
            "quotes, no explanation."
        )
        directive = (
            f"Use this specific creative direction for the story, without deviation or "
            f"explanation: {conceit}\n\n"
            if conceit
            else ""
        )

        prompt = f"""You are writing a Plex Wrapped narrative for a user's {year} listening year.

User Stats:
{json.dumps(stats, indent=2)}

Create a playful, humorous narrative that tells the story of their year through music.
Make it personal, fun, and slightly irreverent - like Spotify Wrapped but with more personality.

{directive}IMPORTANT: Return ONLY valid JSON. The narrative text should be plain text with NO markdown formatting (no # headers, no **, no lists).
Keep paragraphs separated with \\n\\n for readability.

Return in this exact format:
{{
    "narrative": "Your {year} musical journey was..."
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(
            response, {"narrative": "Your musical journey was too epic to put into words."}
        )


class PersonalityGenerator(BaseGenerator):
    """Generates a music personality type based on listening habits."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate personality type from user stats."""
        year = self._wrapped_year(stats)

        framework = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected classification system or metaphor "
            "for describing a type of person (e.g. drawn from nature, a craft, a profession, "
            "a game). Reply with ONLY the system or metaphor, nothing else, no quotes, no "
            "explanation."
        )
        directive = (
            f"Base the personality type on this specific classification system or metaphor, "
            f"without deviation or explanation: {framework}\n\n"
            if framework
            else ""
        )

        prompt = f"""You are creating a music personality type for a Plex user based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create a funny, creative personality type that captures their listening patterns. Think Myers-Briggs meets music taste.

Return ONLY valid JSON in this format:
{{
    "type": "The Chaos Agent",
    "tagline": "Your playlists have trust issues",
    "description": "You listen to everything...",
    "spirit_animal": "A caffeinated raccoon"
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(
            response,
            {
                "type": "The Mystery Listener",
                "tagline": "Your taste defies classification",
                "description": "We couldn't quite figure you out, but that's probably a compliment.",
                "spirit_animal": "A sphinx",
            },
        )


class RoastGenerator(BaseGenerator):
    """Generates playful roasts based on listening habits."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate roasts from user stats."""
        year = self._wrapped_year(stats)

        persona = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected critique persona. Reply with "
            "ONLY the persona, nothing else, no quotes, no explanation."
        )
        directive = (
            f"Write these roasts in this specific comic voice, without deviation or "
            f"explanation: {persona}\n\n"
            if persona
            else ""
        )

        prompt = f"""You are creating playful roasts for a Plex user based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create 3-5 funny, light-hearted roasts about their music taste or listening patterns.
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
        return self._parse_json(
            response,
            {"roasts": ["Your music taste is so unique, we couldn't even roast it properly."]},
        )


class AuraGenerator(BaseGenerator):
    """Generates a music aura color and description."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate aura from user stats."""
        year = self._wrapped_year(stats)

        colour_mood = self._creative_pick(
            "In 3-8 words, invent a specific, unexpected colour and a one-word mood for it "
            "(state it as: colour name, mood word). Reply with ONLY the colour and mood, "
            "nothing else, no quotes, no explanation."
        )
        directive = (
            f"Base the aura on this specific colour and mood, without deviation or "
            f"explanation: {colour_mood}\n\n"
            if colour_mood
            else ""
        )

        prompt = f"""You are creating a "music aura" for a Plex user based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create a creative aura color and vibe that represents their musical energy. Think astrology but for music taste.

Return ONLY valid JSON in this format:
{{
    "color": "Midnight Purple",
    "hex": "#9B59B6",
    "vibe": "Mysterious and moody",
    "description": "Your aura radiates..."
}}
"""

        response = self.provider.generate(prompt)
        return self._parse_json(
            response,
            {
                "color": "Cosmic Purple",
                "hex": "#9B59B6",
                "vibe": "Enigmatic and eclectic",
                "description": "Your musical energy transcends simple description.",
            },
        )


class SuperlativesGenerator(BaseGenerator):
    """Generates fun superlatives and awards."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate superlatives from user stats."""
        year = self._wrapped_year(stats)

        ceremony = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected format or ceremony for handing out "
            "playful awards. Reply with ONLY the format or ceremony, nothing else, no quotes, "
            "no explanation."
        )
        directive = (
            f"Give these awards the flavor of this specific format or ceremony, without "
            f"deviation or explanation: {ceremony}. Whatever the ceremony, you must still "
            f"produce 3-5 separate awards as separate items in the JSON array below - never "
            f"collapse them into one.\n\n"
            if ceremony
            else ""
        )

        prompt = f"""You are creating music superlatives/awards for a Plex user based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create 3-5 funny, creative awards like "Most Likely To..." or "Best..." based on their listening patterns.

Return ONLY valid JSON in this format - always a "superlatives" array of 3-5 items, even if
the ceremony above suggests a single winner:
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
        default = {
            "superlatives": [
                {"award": "Most Dedicated Listener", "reason": "You showed up for your music"}
            ]
        }
        parsed = self._parse_json(response, default)
        # The model occasionally returns a single flat {award, reason} object instead of
        # the wrapped list - valid JSON, wrong shape - which must not pass through as-is.
        if not isinstance(parsed.get("superlatives"), list) or not parsed["superlatives"]:
            return default
        return parsed


class HotTakesGenerator(BaseGenerator):
    """Generates spicy hot takes about the user's music taste."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate hot takes from user stats."""
        year = self._wrapped_year(stats)

        stance = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected rhetorical stance or angle for "
            "delivering a bold opinion. Reply with ONLY the stance or angle, nothing else, "
            "no quotes, no explanation."
        )
        directive = (
            f"Deliver these opinions from this specific stance or angle, without deviation "
            f"or explanation: {stance}\n\n"
            if stance
            else ""
        )

        prompt = f"""You are creating "hot takes" about a Plex user's music taste based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create 3-5 bold, funny opinions or observations about their music taste.
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
        return self._parse_json(
            response, {"hot_takes": ["Your music taste is impeccable and we have no notes."]}
        )


class SuggestionsGenerator(BaseGenerator):
    """Generates personalized music suggestions and predictions."""

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate suggestions from user stats."""
        year = self._wrapped_year(stats)

        fmt = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected format for giving someone a "
            "recommendation (e.g. drawn from a ritual, a document, a piece of advice). "
            "Reply with ONLY the format, nothing else, no quotes, no explanation."
        )
        directive = (
            f"Present these recommendations in this specific format, without deviation or "
            f"explanation: {fmt}\n\n"
            if fmt
            else ""
        )

        prompt = f"""You are creating personalized music suggestions for a Plex user based on their {year} listening habits.

User Stats:
{json.dumps(stats, indent=2)}

{directive}Create 3-5 recommendations or predictions about what they should listen to next, or what their {year + 1} might look like.
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
        return self._parse_json(
            response,
            {"suggestions": ["Keep doing what you're doing - your taste is already excellent."]},
        )


class ThemeGenerator(BaseGenerator):
    """Generates visual theme with color palette and per-slide visualizations."""

    AVAILABLE_VISUALIZATIONS = [
        {
            "id": "gradient_blob",
            "name": "Gradient Blob",
            "bestFor": ["warm", "introspective", "calm"],
        },
        {
            "id": "particles",
            "name": "Particles",
            "bestFor": ["celebratory", "reflective", "dreamy"],
        },
        {"id": "aurora", "name": "Aurora", "bestFor": ["dramatic", "mystical", "epic"]},
    ]

    SLIDES = [
        "intro",
        "totalTime",
        "topArtist",
        "topTracks",
        "listeningClock",
        "quirkyStats",
        "personality",
        "aura",
        "roasts",
        "narrative",
        "share",
    ]

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate theme from user stats."""
        year = self._wrapped_year(stats)
        viz_info = json.dumps(self.AVAILABLE_VISUALIZATIONS, indent=2)
        slides_list = json.dumps(self.SLIDES)
        username = stats.get("user", "the user")

        colour_mood = self._creative_pick(
            "In 3-8 words, invent a specific, unexpected colour and a one-word mood for it "
            "(state it as: colour name, mood word). Reply with ONLY the colour and mood, "
            "nothing else, no quotes, no explanation."
        )
        direction = self._creative_pick(
            "In 3-10 words, invent a specific, unexpected overall visual mood or aesthetic "
            "direction for a set of animated backgrounds. Reply with ONLY the direction, "
            "nothing else, no quotes, no explanation."
        )
        directives = ""
        if colour_mood:
            directives += (
                f"Base the palette on this specific colour and mood, without deviation or "
                f"explanation: {colour_mood}\n\n"
            )
        if direction:
            directives += (
                f"Let this overall visual direction inform your visualization and mood choice "
                f"for every slide, without deviation or explanation: {direction}\n\n"
            )

        prompt = f"""You are creating a visual theme for {username}'s Plex Wrapped experience for {year}.

User Stats:
{json.dumps(stats, indent=2)}

Available Visualizations:
{viz_info}

Slides to configure: {slides_list}

{directives}Based on the user's music taste and personality, create:
1. A color palette (5 colors) that reflects their musical vibe
2. A visualization type and mood for each slide

Moods can be: dramatic, mystical, warm, introspective, celebratory, reflective, energetic, playful, chaotic, analytical, triumphant

Return ONLY valid JSON in this shape. The values below are placeholders showing what type
each field holds, not suggested answers - choose a real visualization id, a real mood, and a
real intensity (0.0-1.0) for every slide yourself, informed by the visual direction above:
{{
    "palette": {{
        "primary": "#hexcolor",
        "secondary": "#hexcolor",
        "accent": "#hexcolor",
        "background": "#hexcolor",
        "text": "#ffffff"
    }},
    "slides": {{
        "intro": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "totalTime": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "topArtist": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "topTracks": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "listeningClock": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "quirkyStats": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "personality": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "aura": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "roasts": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "narrative": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}},
        "share": {{"visualization": "<your pick>", "mood": "<your pick>", "intensity": "<0.0-1.0>"}}
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
                "text": "#FFFFFF",
            },
            "slides": {
                "intro": {"visualization": "aurora", "mood": "dramatic", "intensity": 0.8},
                "totalTime": {
                    "visualization": "particles",
                    "mood": "celebratory",
                    "intensity": 0.6,
                },
                "topArtist": {"visualization": "gradient_blob", "mood": "warm", "intensity": 0.7},
                "topTracks": {"visualization": "particles", "mood": "energetic", "intensity": 0.5},
                "listeningClock": {
                    "visualization": "aurora",
                    "mood": "analytical",
                    "intensity": 0.4,
                },
                "quirkyStats": {"visualization": "particles", "mood": "playful", "intensity": 0.6},
                "personality": {
                    "visualization": "gradient_blob",
                    "mood": "introspective",
                    "intensity": 0.7,
                },
                "aura": {"visualization": "aurora", "mood": "mystical", "intensity": 0.9},
                "roasts": {"visualization": "particles", "mood": "chaotic", "intensity": 0.8},
                "narrative": {
                    "visualization": "gradient_blob",
                    "mood": "reflective",
                    "intensity": 0.3,
                },
                "share": {"visualization": "aurora", "mood": "triumphant", "intensity": 0.7},
            },
        }
        parsed = self._parse_json(response, default_theme)
        # The model occasionally flattens the palette straight to the top level, dropping
        # the "palette"/"slides" wrapper entirely - valid JSON, wrong shape - which must
        # not pass through as-is.
        if not isinstance(parsed.get("palette"), dict) or not isinstance(
            parsed.get("slides"), dict
        ):
            return default_theme
        return parsed
