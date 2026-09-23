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
            "year": 2024,
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

        generator.generate({"year": 2024, "total_minutes": 100})

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

        result = generator.generate({"year": 2024, "genres": ["rock", "pop", "jazz"]})

        assert provider.last_prompt is not None


class TestRoastGenerator:
    def test_generates_roasts_from_stats(self) -> None:
        """Roast generator creates playful callouts."""
        response = '{"roasts": ["Your 2am listening habits are concerning"]}'
        provider = MockProvider(response)
        generator = RoastGenerator(provider)

        result = generator.generate({
            "year": 2024,
            "late_night_plays": 200,
            "most_repeated_track": "same song",
        })

        assert provider.last_prompt is not None


class TestSuperlativesGenerator:
    def test_falls_back_to_default_when_response_is_the_wrong_shape(self) -> None:
        """The model can return a single flat award/reason object instead of the wrapped
        list - valid JSON, wrong shape - and that must not pass through as-is."""
        provider = MockProvider('{"award": "Solo Award", "reason": "just one"}')
        generator = SuperlativesGenerator(provider)

        result = generator.generate({"year": 2025, "top_track_plays": 200})

        assert isinstance(result.get("superlatives"), list)
        assert len(result["superlatives"]) >= 1

    def test_generates_superlatives_from_stats(self) -> None:
        """Superlatives generator creates awards from stats."""
        response = '''{
            "superlatives": [
                {"award": "Most Dedicated Fan", "reason": "Played the same song 200 times"}
            ]
        }'''
        provider = MockProvider(response)
        generator = SuperlativesGenerator(provider)

        result = generator.generate({"year": 2024, "top_track_plays": 200})

        assert provider.last_prompt is not None
        assert "superlatives" in provider.last_prompt.lower() or "award" in provider.last_prompt.lower()


class TestHotTakesGenerator:
    def test_generates_hot_takes_from_stats(self) -> None:
        """HotTakes generator creates spicy opinions."""
        response = '{"hot_takes": ["You say you like indie, but your top 10 is basically the radio"]}'
        provider = MockProvider(response)
        generator = HotTakesGenerator(provider)

        result = generator.generate({"year": 2024, "top_artists": ["Pop Artist 1", "Pop Artist 2"]})

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

        result = generator.generate({"year": 2024, "top_genres": ["rock", "electronic"]})

        assert provider.last_prompt is not None
        assert "palette" in provider.last_prompt.lower()
        assert "visualization" in provider.last_prompt.lower()
        assert result["palette"]["primary"] == "#6366F1"
        assert "intro" in result["slides"]

    def test_falls_back_to_default_when_response_is_the_wrong_shape(self) -> None:
        """The model can return a flattened palette (no "palette"/"slides" wrapper at all) -
        valid JSON, wrong shape - and that must not pass through as-is."""
        provider = MockProvider('{"primary": "#B784A7", "secondary": "#8E6C7D", "accent": "#000"}')
        generator = ThemeGenerator(provider)

        result = generator.generate({"year": 2025, "top_genres": ["rock"]})

        assert isinstance(result.get("palette"), dict)
        assert "primary" in result["palette"]
        assert isinstance(result.get("slides"), dict)
        assert "intro" in result["slides"]


ALL_GENERATORS = [
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    AuraGenerator,
    SuperlativesGenerator,
    HotTakesGenerator,
    SuggestionsGenerator,
    ThemeGenerator,
]


def build_prompt(generator_class: type, year: int) -> str:
    """Run a generator against stats for the given year and return the prompt it built."""
    provider = MockProvider("{}")
    generator_class(provider).generate({"user": "tester", "year": year, "total": {"minutes": 100}})
    assert provider.last_prompt is not None
    return provider.last_prompt


class TestPromptsUseRealYearAndPlex:
    @pytest.mark.parametrize("generator_class", ALL_GENERATORS)
    @pytest.mark.parametrize("year", [2023, 2025])
    def test_prompt_states_the_year_from_stats(self, generator_class: type, year: int) -> None:
        """Opening instruction names the year being wrapped, not a fixed one."""
        instruction = build_prompt(generator_class, year).split("User Stats:")[0]

        assert str(year) in instruction

    @pytest.mark.parametrize("generator_class", ALL_GENERATORS)
    @pytest.mark.parametrize("year", [2022, 2025])
    def test_prompt_has_no_hardcoded_2024(self, generator_class: type, year: int) -> None:
        """A non-2024 year never produces a prompt that mentions 2024."""
        assert "2024" not in build_prompt(generator_class, year)

    @pytest.mark.parametrize("generator_class", ALL_GENERATORS)
    def test_prompt_never_mentions_lastfm(self, generator_class: type) -> None:
        """Prompts describe a Plex user, never Last.fm."""
        prompt = build_prompt(generator_class, 2025)

        assert "last.fm" not in prompt.lower()
        assert "Plex" in prompt

    def test_narrative_example_uses_the_stats_year(self) -> None:
        """The narrative example JSON opens with the real year."""
        assert "Your 2023 musical journey was" in build_prompt(NarrativeGenerator, 2023)

    def test_suggestions_look_ahead_to_the_following_year(self) -> None:
        """Suggestions predict the year after the wrapped year."""
        assert "what their 2026 might look like" in build_prompt(SuggestionsGenerator, 2025)

    def test_theme_prompt_names_the_user(self) -> None:
        """Theme prompt is personalised with the username from stats."""
        assert "tester" in build_prompt(ThemeGenerator, 2025).split("User Stats:")[0]

    @pytest.mark.parametrize("generator_class", ALL_GENERATORS)
    def test_missing_year_fails_clearly(self, generator_class: type) -> None:
        """Stats without a year raise instead of silently defaulting."""
        provider = MockProvider("{}")

        with pytest.raises(ValueError, match="year"):
            generator_class(provider).generate({"user": "tester"})

        assert provider.last_prompt is None


class TestParseJsonTrailingCommas:
    """LLMs sometimes emit a trailing comma, which is invalid JSON."""

    def parse(self, text: str, default: dict | None = None) -> dict:
        return NarrativeGenerator(MockProvider())._parse_json(text, default)

    def test_trailing_comma_in_object(self) -> None:
        assert self.parse('{"color": "Blue", "hex": "#0000FF",\n}') == {"color": "Blue", "hex": "#0000FF"}

    def test_trailing_comma_in_list(self) -> None:
        assert self.parse('{"roasts": ["one", "two",]}') == {"roasts": ["one", "two"]}

    def test_trailing_commas_in_nested_structures(self) -> None:
        text = '{"superlatives": [{"award": "A", "reason": "r",},],}'
        assert self.parse(text) == {"superlatives": [{"award": "A", "reason": "r"}]}

    def test_comma_inside_a_string_is_left_alone(self) -> None:
        """Only structural trailing commas are removed, never text inside strings."""
        assert self.parse('{"note": "ends like this,}",}') == {"note": "ends like this,}"}

    def test_trailing_comma_inside_a_markdown_block(self) -> None:
        assert self.parse('```json\n{"a": 1,}\n```') == {"a": 1}

    def test_trailing_comma_together_with_a_raw_newline_in_a_string(self) -> None:
        assert self.parse('{"text": "line one\nline two",}') == {"text": "line one\nline two"}

    def test_valid_json_is_unchanged(self) -> None:
        assert self.parse('{"a": [1, 2], "b": {"c": "d"}}') == {"a": [1, 2], "b": {"c": "d"}}

    def test_unparseable_text_still_returns_the_default(self) -> None:
        assert self.parse("not json at all", {"fallback": True}) == {"fallback": True}


class RecordingProvider(LLMProvider):
    """Records the prompts a generator sends to generate() and to generate_creative_pick()
    separately, and lets a test control what each one returns."""

    def __init__(self, response: str = "{}", pick: str = "a specific structural conceit") -> None:
        self.response = response
        self.pick = pick
        self.last_prompt: str | None = None
        self.pick_prompts: list[str] = []

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        self.last_prompt = prompt
        return self.response

    def generate_creative_pick(self, prompt: str) -> str:
        self.pick_prompts.append(prompt)
        return self.pick


NEVER_IN_PICK_PROMPT = ("music", "listening", "wrapped", "song", "playlist", "taste")


class TestNarrativeCreativePick:
    def test_asks_for_a_structural_conceit(self) -> None:
        """The picker prompt asks for a device, not for content about the user."""
        provider = RecordingProvider()
        NarrativeGenerator(provider).generate({"year": 2025, "total_minutes": 100})

        assert len(provider.pick_prompts) == 1
        assert "conceit" in provider.pick_prompts[0] or "device" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        """Naming the domain is what caused every pick to collapse onto a recap trope."""
        provider = RecordingProvider()
        NarrativeGenerator(provider).generate({"year": 2025, "total_minutes": 100})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt_as_a_directive(self) -> None:
        provider = RecordingProvider(pick="told entirely through voicemail transcripts")
        NarrativeGenerator(provider).generate({"year": 2025, "total_minutes": 100})

        assert "told entirely through voicemail transcripts" in provider.last_prompt
        assert "without deviation" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        """A provider with nothing to add (e.g. NoOpProvider) must not get an empty directive."""
        provider = RecordingProvider(pick="")
        NarrativeGenerator(provider).generate({"year": 2025, "total_minutes": 100})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            NarrativeGenerator(provider).generate({"total_minutes": 100})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestRoastCreativePick:
    def test_asks_for_a_critique_persona(self) -> None:
        provider = RecordingProvider()
        RoastGenerator(provider).generate({"year": 2025, "late_night_plays": 5})

        assert len(provider.pick_prompts) == 1
        assert "persona" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        RoastGenerator(provider).generate({"year": 2025, "late_night_plays": 5})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="a disgruntled maritime archaeologist")
        RoastGenerator(provider).generate({"year": 2025, "late_night_plays": 5})

        assert "a disgruntled maritime archaeologist" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        RoastGenerator(provider).generate({"year": 2025, "late_night_plays": 5})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            RoastGenerator(provider).generate({"late_night_plays": 5})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestPersonalityCreativePick:
    def test_asks_for_a_classification_framework(self) -> None:
        provider = RecordingProvider()
        PersonalityGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert len(provider.pick_prompts) == 1
        assert "classification" in provider.pick_prompts[0] or "framework" in provider.pick_prompts[0] or "metaphor" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        PersonalityGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="a species of deep-sea fungus")
        PersonalityGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert "a species of deep-sea fungus" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        PersonalityGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            PersonalityGenerator(provider).generate({"genres": ["rock"]})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestAuraCreativePick:
    def test_asks_for_a_colour_and_mood(self) -> None:
        provider = RecordingProvider()
        AuraGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert len(provider.pick_prompts) == 1
        assert "colour" in provider.pick_prompts[0] or "color" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        AuraGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="Burnt Sienna, wistful")
        AuraGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert "Burnt Sienna, wistful" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        AuraGenerator(provider).generate({"year": 2025, "genres": ["rock"]})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            AuraGenerator(provider).generate({"genres": ["rock"]})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestSuperlativesCreativePick:
    def test_asks_for_an_award_ceremony_format(self) -> None:
        provider = RecordingProvider()
        SuperlativesGenerator(provider).generate({"year": 2025, "top_track_plays": 200})

        assert len(provider.pick_prompts) == 1
        assert "award" in provider.pick_prompts[0] or "ceremony" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        SuperlativesGenerator(provider).generate({"year": 2025, "top_track_plays": 200})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="a county fair ribbon ceremony")
        SuperlativesGenerator(provider).generate({"year": 2025, "top_track_plays": 200})

        assert "a county fair ribbon ceremony" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        SuperlativesGenerator(provider).generate({"year": 2025, "top_track_plays": 200})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            SuperlativesGenerator(provider).generate({"top_track_plays": 200})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestHotTakesCreativePick:
    def test_asks_for_a_rhetorical_stance(self) -> None:
        provider = RecordingProvider()
        HotTakesGenerator(provider).generate({"year": 2025, "top_artists": ["A"]})

        assert len(provider.pick_prompts) == 1
        assert "stance" in provider.pick_prompts[0] or "angle" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        HotTakesGenerator(provider).generate({"year": 2025, "top_artists": ["A"]})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="a conspiracy theorist connecting unrelated dots")
        HotTakesGenerator(provider).generate({"year": 2025, "top_artists": ["A"]})

        assert "a conspiracy theorist connecting unrelated dots" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        HotTakesGenerator(provider).generate({"year": 2025, "top_artists": ["A"]})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            HotTakesGenerator(provider).generate({"top_artists": ["A"]})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestSuggestionsCreativePick:
    def test_asks_for_a_recommendation_format(self) -> None:
        provider = RecordingProvider()
        SuggestionsGenerator(provider).generate({"year": 2025})

        assert len(provider.pick_prompts) == 1
        assert "recommendation" in provider.pick_prompts[0] or "format" in provider.pick_prompts[0]

    def test_pick_prompt_is_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        SuggestionsGenerator(provider).generate({"year": 2025})

        pick_prompt = provider.pick_prompts[0].lower()
        for banned in NEVER_IN_PICK_PROMPT:
            assert banned not in pick_prompt

    def test_splices_the_pick_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="a fortune cookie slip")
        SuggestionsGenerator(provider).generate({"year": 2025})

        assert "a fortune cookie slip" in provider.last_prompt

    def test_skips_the_directive_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        SuggestionsGenerator(provider).generate({"year": 2025})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            SuggestionsGenerator(provider).generate({})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None


class TestThemeCreativePick:
    def test_asks_for_a_colour_and_mood_and_a_visual_direction(self) -> None:
        """Theme makes two picks: a palette colour/mood, and an overall visual direction
        that should inform every slide's visualization/mood choice."""
        provider = RecordingProvider()
        ThemeGenerator(provider).generate({"year": 2025, "top_genres": ["rock"]})

        assert len(provider.pick_prompts) == 2

    def test_pick_prompts_are_not_scoped_to_music_or_the_wrapped_domain(self) -> None:
        provider = RecordingProvider()
        ThemeGenerator(provider).generate({"year": 2025, "top_genres": ["rock"]})

        for pick_prompt in provider.pick_prompts:
            lowered = pick_prompt.lower()
            for banned in NEVER_IN_PICK_PROMPT:
                assert banned not in lowered

    def test_splices_both_picks_into_the_main_prompt(self) -> None:
        provider = RecordingProvider(pick="Electric Cerulean, unhinged")
        ThemeGenerator(provider).generate({"year": 2025, "top_genres": ["rock"]})

        assert "Electric Cerulean, unhinged" in provider.last_prompt
        assert provider.last_prompt.count("without deviation") == 2

    def test_skips_directives_when_the_provider_has_no_pick(self) -> None:
        provider = RecordingProvider(pick="")
        ThemeGenerator(provider).generate({"year": 2025, "top_genres": ["rock"]})

        assert "without deviation" not in provider.last_prompt

    def test_missing_year_raises_before_any_pick_call(self) -> None:
        provider = RecordingProvider()

        with pytest.raises(ValueError, match="year"):
            ThemeGenerator(provider).generate({"top_genres": ["rock"]})

        assert provider.pick_prompts == []
        assert provider.last_prompt is None

