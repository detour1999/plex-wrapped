# ABOUTME: Tests for stats processing (top tracks, artists, albums).
# ABOUTME: Verifies correct aggregation and ranking of listening data.

import pytest
from datetime import datetime

from plex_wrapped.extractors.plex import Track, ListeningHistory
from plex_wrapped.processors.stats import StatsProcessor, TopItem


def make_track(title: str, artist: str, album: str, plays: int = 1) -> list[Track]:
    """Helper to create multiple track plays."""
    return [
        Track(
            title=title,
            artist=artist,
            album=album,
            duration_ms=180000,
            played_at=datetime(2024, 1, 1 + (i // 24), i % 24, 0),
            user="testuser",
        )
        for i in range(plays)
    ]


class TestStatsProcessor:
    def test_top_artists(self) -> None:
        """Calculates top artists by play count."""
        tracks = (
            make_track("Song A", "Artist 1", "Album 1", plays=10)
            + make_track("Song B", "Artist 2", "Album 2", plays=5)
            + make_track("Song C", "Artist 1", "Album 3", plays=3)
        )
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = StatsProcessor(history)
        top_artists = processor.top_artists(limit=2)

        assert len(top_artists) == 2
        assert top_artists[0].name == "Artist 1"
        assert top_artists[0].plays == 13
        assert top_artists[1].name == "Artist 2"
        assert top_artists[1].plays == 5

    def test_top_tracks(self) -> None:
        """Calculates top tracks by play count."""
        tracks = (
            make_track("Song A", "Artist 1", "Album 1", plays=10)
            + make_track("Song B", "Artist 2", "Album 2", plays=15)
        )
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = StatsProcessor(history)
        top_tracks = processor.top_tracks(limit=2)

        assert top_tracks[0].name == "Song B"
        assert top_tracks[0].plays == 15
        assert top_tracks[0].artist == "Artist 2"

    def test_top_albums(self) -> None:
        """Calculates top albums by play count."""
        tracks = (
            make_track("Song A", "Artist 1", "Album X", plays=5)
            + make_track("Song B", "Artist 1", "Album X", plays=5)
            + make_track("Song C", "Artist 2", "Album Y", plays=3)
        )
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = StatsProcessor(history)
        top_albums = processor.top_albums(limit=2)

        assert top_albums[0].name == "Album X"
        assert top_albums[0].plays == 10
        assert top_albums[0].artist == "Artist 1"

    def test_total_stats(self) -> None:
        """Calculates total listening stats."""
        tracks = make_track("Song A", "Artist 1", "Album 1", plays=100)
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = StatsProcessor(history)
        stats = processor.total_stats()

        assert stats["total_tracks"] == 100
        assert stats["total_minutes"] == 300.0  # 100 * 3 minutes
        assert stats["unique_artists"] == 1
        assert stats["unique_albums"] == 1
        assert stats["unique_tracks"] == 1
