# ABOUTME: Time analysis processor for listening patterns.
# ABOUTME: Analyzes plays by hour, day, month and identifies quirky temporal stats.

from collections import Counter
from datetime import datetime

from last_wrapped.extractors.plex import ListeningHistory


class TimeAnalysisProcessor:
    """Analyzes temporal patterns in listening history."""

    def __init__(self, history: ListeningHistory) -> None:
        self.history = history

    def plays_by_hour(self) -> list[int]:
        """Count plays per hour of day (0-23)."""
        hour_counts = Counter(track.played_at.hour for track in self.history.tracks)
        return [hour_counts.get(hour, 0) for hour in range(24)]

    def plays_by_day_of_week(self) -> list[int]:
        """Count plays per day of week (0=Monday, 6=Sunday)."""
        day_counts = Counter(
            track.played_at.weekday() for track in self.history.tracks
        )
        return [day_counts.get(day, 0) for day in range(7)]

    def plays_by_month(self) -> list[int]:
        """Count plays per month (1-12)."""
        month_counts = Counter(track.played_at.month for track in self.history.tracks)
        return [month_counts.get(month, 0) for month in range(1, 13)]

    def peak_listening_hour(self) -> int:
        """Find hour with most plays."""
        hour_counts = Counter(track.played_at.hour for track in self.history.tracks)
        return hour_counts.most_common(1)[0][0] if hour_counts else 0

    def peak_listening_day(self) -> int:
        """Find day of week with most plays (0=Monday, 6=Sunday)."""
        day_counts = Counter(
            track.played_at.weekday() for track in self.history.tracks
        )
        return day_counts.most_common(1)[0][0] if day_counts else 0

    def peak_day_overall(self) -> dict:
        """Find the single date with most plays."""
        date_counts = Counter(
            track.played_at.date() for track in self.history.tracks
        )
        if not date_counts:
            return {"date": None, "plays": 0}

        most_common_date, play_count = date_counts.most_common(1)[0]
        return {
            "date": most_common_date.isoformat(),
            "plays": play_count,
        }

    def longest_streak(self) -> int:
        """Find longest consecutive days with at least one play."""
        if not self.history.tracks:
            return 0

        # Get all unique dates sorted
        dates = sorted(set(track.played_at.date() for track in self.history.tracks))

        if not dates:
            return 0

        max_streak = 1
        current_streak = 1

        for i in range(1, len(dates)):
            days_diff = (dates[i] - dates[i - 1]).days
            if days_diff == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        return max_streak

    def late_night_anthem(self) -> dict | None:
        """Find most played track between midnight and 4am."""
        late_night_tracks = [
            track
            for track in self.history.tracks
            if 0 <= track.played_at.hour < 4
        ]

        if not late_night_tracks:
            return None

        track_counts = Counter(
            (track.title, track.artist) for track in late_night_tracks
        )
        most_common, play_count = track_counts.most_common(1)[0]
        title, artist = most_common

        return {
            "track": title,
            "artist": artist,
            "plays_after_midnight": play_count,
        }

    def day_anthem(self, day_of_week: int) -> dict | None:
        """Find most played track on specific day of week (0=Monday, 6=Sunday)."""
        day_tracks = [
            track
            for track in self.history.tracks
            if track.played_at.weekday() == day_of_week
        ]

        if not day_tracks:
            return None

        track_counts = Counter((track.title, track.artist) for track in day_tracks)
        most_common, play_count = track_counts.most_common(1)[0]
        title, artist = most_common

        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        return {
            "track": title,
            "artist": artist,
            "day": day_names[day_of_week],
            "plays": play_count,
        }

    def most_repeated_single_day(self) -> dict | None:
        """Find the track played most times on a single day."""
        if not self.history.tracks:
            return None

        # Group tracks by (date, title, artist)
        day_track_counts: Counter = Counter()
        for track in self.history.tracks:
            key = (track.played_at.date(), track.title, track.artist)
            day_track_counts[key] += 1

        if not day_track_counts:
            return None

        most_common, play_count = day_track_counts.most_common(1)[0]
        date, title, artist = most_common

        return {
            "track": title,
            "artist": artist,
            "date": date.isoformat(),
            "plays": play_count,
        }
