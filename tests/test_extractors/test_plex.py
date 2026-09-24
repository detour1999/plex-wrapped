# ABOUTME: Tests for Plex data extraction.
# ABOUTME: Uses real Plex API calls (no mocking per project rules).

import pytest
from datetime import datetime

from plex_wrapped.extractors.plex import PlexExtractor, ListeningHistory, Track


class TestPlexExtractor:
    """Tests for PlexExtractor - requires real Plex server for integration tests."""

    def test_extractor_initialization(self) -> None:
        """Extractor initializes with URL and token."""
        extractor = PlexExtractor(
            url="https://plex.example.com",
            token="test-token",
        )
        assert extractor.url == "https://plex.example.com"
        assert extractor.token == "test-token"

    def test_track_model(self) -> None:
        """Track model holds listening data."""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_ms=180000,
            played_at=datetime(2024, 6, 15, 14, 30),
            user="testuser",
        )
        assert track.title == "Test Song"
        assert track.duration_minutes == 3.0

    def test_listening_history_model(self) -> None:
        """ListeningHistory aggregates tracks per user."""
        history = ListeningHistory(
            user="testuser",
            year=2024,
            tracks=[
                Track(
                    title="Song 1",
                    artist="Artist 1",
                    album="Album 1",
                    duration_ms=180000,
                    played_at=datetime(2024, 1, 1, 12, 0),
                    user="testuser",
                ),
                Track(
                    title="Song 2",
                    artist="Artist 2",
                    album="Album 2",
                    duration_ms=240000,
                    played_at=datetime(2024, 1, 2, 12, 0),
                    user="testuser",
                ),
            ],
        )
        assert history.total_tracks == 2
        assert history.total_minutes == 7.0


class TestNotConnectedGuards:
    """Every method that needs a server connection fails clearly if connect() was never
    called, before touching anything network-related - real, mock-free behavior."""

    def test_get_users_without_connecting(self) -> None:
        extractor = PlexExtractor(url="https://plex.example.com", token="test-token")

        with pytest.raises(RuntimeError, match="Not connected"):
            extractor.get_users()

    def test_extract_user_history_without_connecting(self) -> None:
        extractor = PlexExtractor(url="https://plex.example.com", token="test-token")

        with pytest.raises(RuntimeError, match="Not connected"):
            extractor.extract_user_history(username="someone", year=2024)

    def test_extract_all_users_without_connecting(self) -> None:
        extractor = PlexExtractor(url="https://plex.example.com", token="test-token")

        with pytest.raises(RuntimeError, match="Not connected"):
            extractor.extract_all_users(year=2024)

    def test_get_user_account_id_without_connecting(self) -> None:
        extractor = PlexExtractor(url="https://plex.example.com", token="test-token")

        with pytest.raises(RuntimeError, match="Not connected"):
            extractor._get_user_account_id("someone")
