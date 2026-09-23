# ABOUTME: Tests for shared utility functions.
# ABOUTME: Covers slugify's text-cleaning and length-limiting behavior.

from plex_wrapped.utils import slugify


class TestSlugify:
    def test_lowercases_and_hyphenates(self) -> None:
        assert slugify("The Beatles") == "the-beatles"

    def test_strips_special_characters(self) -> None:
        assert slugify("AC/DC - Highway to Hell!") == "acdc-highway-to-hell"

    def test_empty_string_returns_empty_string(self) -> None:
        assert slugify("") == ""

    def test_collapses_multiple_spaces_and_hyphens_into_one(self) -> None:
        assert slugify("Sigur  Rós -- () Valtari") == "sigur-rós-valtari"

    def test_strips_leading_and_trailing_hyphens(self) -> None:
        assert slugify("  -Also Sprach- ") == "also-sprach"

    def test_truncates_to_fifty_characters(self) -> None:
        long_name = "A" * 100
        result = slugify(long_name)
        assert len(result) == 50
        assert result == "a" * 50

    def test_keeps_unicode_letters(self) -> None:
        """Non-ASCII letters aren't special characters and survive the slug."""
        assert slugify("Björk") == "björk"
