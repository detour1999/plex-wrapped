# ABOUTME: Tests for time pattern analysis.
# ABOUTME: Verifies hour/day/month breakdowns and quirky stat detection.

import pytest
from datetime import datetime

from last_wrapped.extractors.plex import Track, ListeningHistory
from last_wrapped.processors.time_analysis import TimeAnalysisProcessor


def make_track_at(hour: int, day_of_week: int = 0, month: int = 1) -> Track:
    """Create a track played at specific time."""
    # day_of_week: 0=Monday, 6=Sunday
    # Find a date in 2024 that matches the day_of_week
    base_date = datetime(2024, month, 1)
    days_ahead = day_of_week - base_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    target_date = base_date.replace(day=base_date.day + days_ahead)

    return Track(
        title=f"Song at {hour}",
        artist="Artist",
        album="Album",
        duration_ms=180000,
        played_at=target_date.replace(hour=hour),
        user="testuser",
    )


class TestTimeAnalysisProcessor:
    def test_plays_by_hour(self) -> None:
        """Counts plays per hour of day."""
        tracks = [
            make_track_at(hour=2),
            make_track_at(hour=2),
            make_track_at(hour=14),
        ]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = TimeAnalysisProcessor(history)
        by_hour = processor.plays_by_hour()

        assert len(by_hour) == 24
        assert by_hour[2] == 2
        assert by_hour[14] == 1
        assert by_hour[0] == 0

    def test_plays_by_day_of_week(self) -> None:
        """Counts plays per day of week."""
        tracks = [
            make_track_at(hour=12, day_of_week=0),  # Monday
            make_track_at(hour=12, day_of_week=0),  # Monday
            make_track_at(hour=12, day_of_week=4),  # Friday
        ]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = TimeAnalysisProcessor(history)
        by_day = processor.plays_by_day_of_week()

        assert len(by_day) == 7
        assert by_day[0] == 2  # Monday
        assert by_day[4] == 1  # Friday

    def test_peak_listening_hour(self) -> None:
        """Finds the hour with most plays."""
        tracks = [make_track_at(hour=22) for _ in range(10)]
        tracks += [make_track_at(hour=14) for _ in range(5)]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = TimeAnalysisProcessor(history)
        peak = processor.peak_listening_hour()

        assert peak == 22

    def test_late_night_anthem(self) -> None:
        """Finds most played track between midnight and 4am."""
        tracks = [
            Track(
                title="Night Song",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=datetime(2024, 1, i + 1, 2, 0),
                user="test",
            )
            for i in range(5)
        ]
        tracks += [
            Track(
                title="Day Song",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=datetime(2024, 1, 1, 14, 0),
                user="test",
            )
        ]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        processor = TimeAnalysisProcessor(history)
        anthem = processor.late_night_anthem()

        assert anthem is not None
        assert anthem["track"] == "Night Song"
        assert anthem["plays_after_midnight"] == 5
