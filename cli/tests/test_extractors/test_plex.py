# ABOUTME: Tests for Plex data extraction.
# ABOUTME: Uses real Plex API calls (no mocking per project rules).

import pytest
from datetime import datetime
from pathlib import Path

from last_wrapped.extractors.plex import PlexExtractor, ListeningHistory, Track


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
