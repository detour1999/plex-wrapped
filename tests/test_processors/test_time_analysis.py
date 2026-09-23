# ABOUTME: Tests for time pattern analysis.
# ABOUTME: Verifies hour/day/month breakdowns and quirky stat detection.

from datetime import datetime

from plex_wrapped.extractors.plex import Track, ListeningHistory
from plex_wrapped.processors.time_analysis import TimeAnalysisProcessor


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

    def test_plays_by_month(self) -> None:
        tracks = [make_track_at(hour=12, month=3) for _ in range(2)]
        tracks += [make_track_at(hour=12, month=7)]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        by_month = TimeAnalysisProcessor(history).plays_by_month()

        assert len(by_month) == 12
        assert by_month[2] == 2  # March is index 2 (months are 1-12)
        assert by_month[6] == 1  # July is index 6
        assert by_month[0] == 0  # January

    def test_peak_listening_day(self) -> None:
        tracks = [make_track_at(hour=12, day_of_week=2) for _ in range(3)]
        tracks += [make_track_at(hour=12, day_of_week=5)]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        assert TimeAnalysisProcessor(history).peak_listening_day() == 2

    def test_peak_day_overall(self) -> None:
        tracks = [
            Track(
                title="A",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=datetime(2024, 3, 15, h, 0),
                user="test",
            )
            for h in (9, 10, 11)
        ]
        tracks.append(
            Track(
                title="B",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=datetime(2024, 3, 16, 9, 0),
                user="test",
            )
        )
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        peak = TimeAnalysisProcessor(history).peak_day_overall()

        assert peak == {"date": "2024-03-15", "plays": 3}

    def test_longest_streak(self) -> None:
        # Three consecutive days, then a gap, then two more consecutive days
        dates = [1, 2, 3, 10, 11]
        tracks = [
            Track(
                title=f"Song {d}",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=datetime(2024, 1, d, 12, 0),
                user="test",
            )
            for d in dates
        ]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        assert TimeAnalysisProcessor(history).longest_streak() == 3

    def test_day_anthem(self) -> None:
        tracks = [make_track_at(hour=12, day_of_week=3) for _ in range(2)]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        anthem = TimeAnalysisProcessor(history).day_anthem(3)

        assert anthem is not None
        assert anthem["day"] == "Thursday"
        assert anthem["plays"] == 2

    def test_day_anthem_returns_none_when_nothing_played_that_day(self) -> None:
        tracks = [make_track_at(hour=12, day_of_week=0)]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        assert TimeAnalysisProcessor(history).day_anthem(6) is None

    def test_most_repeated_single_day(self) -> None:
        same_day = datetime(2024, 5, 1, 20, 0)
        tracks = [
            Track(
                title="Repeat",
                artist="Artist",
                album="Album",
                duration_ms=180000,
                played_at=same_day,
                user="test",
            )
            for _ in range(4)
        ]
        history = ListeningHistory(user="test", year=2024, tracks=tracks)

        result = TimeAnalysisProcessor(history).most_repeated_single_day()

        assert result == {"track": "Repeat", "artist": "Artist", "date": "2024-05-01", "plays": 4}


class TestTimeAnalysisEmptyHistory:
    """Every stat has a graceful empty-history default instead of an IndexError."""

    def _empty_processor(self) -> TimeAnalysisProcessor:
        return TimeAnalysisProcessor(ListeningHistory(user="test", year=2024, tracks=[]))

    def test_peak_listening_hour_defaults_to_zero(self) -> None:
        assert self._empty_processor().peak_listening_hour() == 0

    def test_peak_listening_day_defaults_to_zero(self) -> None:
        assert self._empty_processor().peak_listening_day() == 0

    def test_peak_day_overall_defaults_to_none_date(self) -> None:
        assert self._empty_processor().peak_day_overall() == {"date": None, "plays": 0}

    def test_longest_streak_defaults_to_zero(self) -> None:
        assert self._empty_processor().longest_streak() == 0

    def test_late_night_anthem_defaults_to_none(self) -> None:
        assert self._empty_processor().late_night_anthem() is None

    def test_day_anthem_defaults_to_none(self) -> None:
        assert self._empty_processor().day_anthem(0) is None

    def test_most_repeated_single_day_defaults_to_none(self) -> None:
        assert self._empty_processor().most_repeated_single_day() is None
