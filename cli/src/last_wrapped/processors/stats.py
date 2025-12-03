# ABOUTME: Stats processor for calculating top tracks, artists, and albums.
# ABOUTME: Aggregates listening history data and ranks by play count.

from dataclasses import dataclass
from collections import Counter
from typing import Any

from last_wrapped.extractors.plex import ListeningHistory


@dataclass
class TopItem:
    """Represents a top item (track, artist, or album) with stats."""

    name: str
    plays: int
    minutes: float
    artist: str | None = None
    album: str | None = None
    image_url: str | None = None


class StatsProcessor:
    """Processes listening history to generate statistics."""

    def __init__(self, history: ListeningHistory) -> None:
        """Initialize with listening history data."""
        self.history = history

    def top_artists(self, limit: int = 10) -> list[TopItem]:
        """Get top artists by play count.

        Args:
            limit: Maximum number of artists to return

        Returns:
            List of TopItem objects sorted by play count (descending)
        """
        artist_plays = Counter(track.artist for track in self.history.tracks)
        artist_minutes: dict[str, float] = {}
        artist_images: dict[str, str | None] = {}

        for track in self.history.tracks:
            artist = track.artist
            artist_minutes[artist] = artist_minutes.get(artist, 0.0) + track.duration_minutes

            # Store first thumb_url we see for each artist
            if artist not in artist_images:
                artist_images[artist] = track.thumb_url

        top_items = [
            TopItem(
                name=artist,
                plays=plays,
                minutes=artist_minutes[artist],
                artist=None,
                album=None,
                image_url=artist_images.get(artist),
            )
            for artist, plays in artist_plays.most_common(limit)
        ]

        return top_items

    def top_tracks(self, limit: int = 10) -> list[TopItem]:
        """Get top tracks by play count.

        Args:
            limit: Maximum number of tracks to return

        Returns:
            List of TopItem objects sorted by play count (descending)
        """
        track_key_plays: Counter[tuple[str, str]] = Counter()
        track_info: dict[tuple[str, str], dict[str, Any]] = {}

        for track in self.history.tracks:
            key = (track.title, track.artist)
            track_key_plays[key] += 1

            if key not in track_info:
                track_info[key] = {
                    "album": track.album,
                    "duration_minutes": track.duration_minutes,
                    "thumb_url": track.thumb_url,
                }

        top_items = []
        for (title, artist), plays in track_key_plays.most_common(limit):
            info = track_info[(title, artist)]
            minutes = info["duration_minutes"] * plays

            top_items.append(
                TopItem(
                    name=title,
                    plays=plays,
                    minutes=minutes,
                    artist=artist,
                    album=info["album"],
                    image_url=info["thumb_url"],
                )
            )

        return top_items

    def top_albums(self, limit: int = 10) -> list[TopItem]:
        """Get top albums by play count.

        Args:
            limit: Maximum number of albums to return

        Returns:
            List of TopItem objects sorted by play count (descending)
        """
        album_key_plays: Counter[tuple[str, str]] = Counter()
        album_minutes: dict[tuple[str, str], float] = {}
        album_images: dict[tuple[str, str], str | None] = {}

        for track in self.history.tracks:
            key = (track.album, track.artist)
            album_key_plays[key] += 1
            album_minutes[key] = album_minutes.get(key, 0.0) + track.duration_minutes

            # Store first thumb_url we see for each album
            if key not in album_images:
                album_images[key] = track.thumb_url

        top_items = [
            TopItem(
                name=album,
                plays=plays,
                minutes=album_minutes[(album, artist)],
                artist=artist,
                album=None,
                image_url=album_images.get((album, artist)),
            )
            for (album, artist), plays in album_key_plays.most_common(limit)
        ]

        return top_items

    def total_stats(self) -> dict[str, Any]:
        """Calculate total listening statistics.

        Returns:
            Dictionary containing:
                - total_tracks: Total number of plays
                - total_minutes: Total listening time in minutes
                - unique_artists: Number of unique artists
                - unique_albums: Number of unique albums
                - unique_tracks: Number of unique tracks
        """
        total_tracks = len(self.history.tracks)
        total_minutes = sum(track.duration_minutes for track in self.history.tracks)

        unique_artists = len({track.artist for track in self.history.tracks})
        unique_albums = len({track.album for track in self.history.tracks})
        unique_tracks = len({(track.title, track.artist) for track in self.history.tracks})

        return {
            "total_tracks": total_tracks,
            "total_minutes": total_minutes,
            "unique_artists": unique_artists,
            "unique_albums": unique_albums,
            "unique_tracks": unique_tracks,
        }
