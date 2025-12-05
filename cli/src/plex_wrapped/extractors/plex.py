# ABOUTME: Plex data extractor for fetching listening history from Plex servers.
# ABOUTME: Supports multi-user extraction with filtering by year and date ranges.

from datetime import datetime
from typing import Callable, Optional

from plexapi.server import PlexServer
from pydantic import BaseModel, Field

# Type alias for progress callbacks: (message: str) -> None
ProgressCallback = Callable[[str], None]


class Track(BaseModel):
    """Represents a single track listening event."""

    title: str
    artist: str
    album: str
    duration_ms: int = 0
    played_at: datetime
    user: str
    genre: Optional[str] = None
    thumb_url: Optional[str] = None

    @property
    def duration_minutes(self) -> float:
        """Convert duration from milliseconds to minutes."""
        return self.duration_ms / 60000.0


class ListeningHistory(BaseModel):
    """Aggregated listening history for a user."""

    user: str
    year: int
    tracks: list[Track] = Field(default_factory=list)
    avatar_url: Optional[str] = None

    @property
    def total_tracks(self) -> int:
        """Total number of tracks listened to."""
        return len(self.tracks)

    @property
    def total_minutes(self) -> float:
        """Total listening time in minutes."""
        return sum(track.duration_minutes for track in self.tracks)


class PlexExtractor:
    """Extracts listening history from Plex Media Server."""

    def __init__(self, url: str, token: str) -> None:
        """Initialize Plex extractor.

        Args:
            url: Plex server URL (e.g., 'https://plex.example.com')
            token: Plex authentication token
        """
        self.url = url
        self.token = token
        self._server: Optional[PlexServer] = None
        self._duration_cache: Optional[dict[tuple[str, str], int]] = None

    def connect(self) -> PlexServer:
        """Establish connection to Plex server.

        Returns:
            Connected PlexServer instance

        Raises:
            ConnectionError: If unable to connect to Plex server
        """
        try:
            self._server = PlexServer(self.url, self.token)
            return self._server
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Plex server: {e}") from e

    def get_users(self) -> list[str]:
        """Get list of usernames with access to the Plex server.

        Returns:
            List of username strings

        Raises:
            RuntimeError: If not connected to server
        """
        if not self._server:
            raise RuntimeError("Not connected. Call connect() first.")

        users = []
        # Get the account owner
        account = self._server.myPlexAccount()
        users.append(account.username)

        # Get shared users and managed/home users
        for user in account.users():
            # Managed users may have title instead of username
            name = user.username or user.title or getattr(user, "name", None)
            if name:
                users.append(name)

        return users

    def _build_track_duration_cache(
        self,
        music_library,
        on_progress: Optional[ProgressCallback] = None,
    ) -> dict[tuple[str, str], int]:
        """Build a cache mapping (title, artist) to duration_ms.

        Args:
            music_library: Plex music library section
            on_progress: Optional callback for progress updates

        Returns:
            Dictionary mapping (track_title, artist_name) tuples to duration in ms
        """
        cache: dict[tuple[str, str], int] = {}
        try:
            # Get all tracks from the library
            tracks = music_library.searchTracks()
            total = len(tracks) if hasattr(tracks, "__len__") else None

            for i, track in enumerate(tracks):
                key = (track.title, track.grandparentTitle or "Unknown Artist")
                if key not in cache and hasattr(track, "duration") and track.duration:
                    cache[key] = track.duration

                # Report progress every 100 tracks
                if on_progress and i % 100 == 0:
                    if total:
                        on_progress(f"  Building duration cache: {i:,}/{total:,} tracks")
                    else:
                        on_progress(f"  Building duration cache: {i:,} tracks scanned")

            if on_progress:
                on_progress(f"  Duration cache built: {len(cache):,} tracks indexed")

        except Exception:
            # Non-critical - just return empty cache if this fails
            pass
        return cache

    def extract_user_history(
        self,
        username: str,
        year: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> ListeningHistory:
        """Extract listening history for a specific user.

        Args:
            username: Plex username to extract history for
            year: Year to extract (for metadata)
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)
            on_progress: Optional callback for progress updates

        Returns:
            ListeningHistory object containing all listening events

        Raises:
            RuntimeError: If not connected to server
            ValueError: If user not found or no music libraries available
        """
        if not self._server:
            raise RuntimeError("Not connected. Call connect() first.")

        # Find music library
        music_libraries = [
            section for section in self._server.library.sections() if section.type == "artist"
        ]
        if not music_libraries:
            raise ValueError("No music libraries found on Plex server")

        music_library = music_libraries[0]

        # Build duration cache from library tracks (history items don't include duration)
        # Cache is built once and reused across all user extractions
        if self._duration_cache is None:
            if on_progress:
                on_progress("  Building track duration cache (first user only)...")
            self._duration_cache = self._build_track_duration_cache(music_library, on_progress)
        duration_cache = self._duration_cache

        # Get user's listening history
        tracks = []
        try:
            # Get all track plays for the user from server-level history
            # LibrarySection.history() doesn't support accountID, but PlexServer.history() does
            # PlexServer.history() only supports mindate, not maxdate - we filter manually
            if on_progress:
                on_progress(f"  Fetching history for {username}...")

            history_items = self._server.history(
                accountID=self._get_user_account_id(username),
                librarySectionID=music_library.key,
                mindate=start_date,
            )

            # Convert to list to get total count
            history_list = list(history_items)
            total_items = len(history_list)

            if on_progress:
                on_progress(f"  Processing {total_items:,} history items for {username}...")

            for i, item in enumerate(history_list):
                # Filter by end_date manually since plexapi doesn't support maxdate
                if end_date and hasattr(item, "viewedAt") and item.viewedAt > end_date:
                    continue

                # Skip tracks without essential data
                if not item.title or not hasattr(item, "viewedAt") or not item.viewedAt:
                    continue

                # Extract track information
                artist_name = item.grandparentTitle or "Unknown Artist"

                # Build full thumb URL with server base and token
                thumb_url = None
                if hasattr(item, "thumb") and item.thumb:
                    thumb_url = f"{self.url}{item.thumb}?X-Plex-Token={self.token}"

                # Look up duration from cache (history items don't have duration)
                duration_ms = duration_cache.get((item.title, artist_name), 0)

                track = Track(
                    title=item.title,
                    artist=artist_name,
                    album=item.parentTitle or "Unknown Album",
                    duration_ms=duration_ms,
                    played_at=item.viewedAt,
                    user=username,
                    genre=", ".join([g.tag for g in item.genres]) if hasattr(item, "genres") and item.genres else None,
                    thumb_url=thumb_url,
                )
                tracks.append(track)

                # Report progress every 500 items
                if on_progress and (i + 1) % 500 == 0:
                    on_progress(f"  Processing history: {i + 1:,}/{total_items:,} for {username}")

            if on_progress:
                on_progress(f"  Found {len(tracks):,} tracks for {username}")

        except Exception as e:
            raise ValueError(f"Failed to extract history for user {username}: {e}") from e

        # Get user avatar if available
        avatar_url = None
        try:
            account = self._server.myPlexAccount()
            if account.username == username:
                avatar_url = account.thumb if hasattr(account, "thumb") else None
            else:
                for user in account.users():
                    user_name = user.username or user.title or getattr(user, "name", None)
                    if user_name == username:
                        avatar_url = user.thumb if hasattr(user, "thumb") else None
                        break
        except Exception:
            # Avatar extraction is non-critical
            pass

        return ListeningHistory(
            user=username,
            year=year,
            tracks=tracks,
            avatar_url=avatar_url,
        )

    def extract_all_users(
        self,
        year: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[ListeningHistory]:
        """Extract listening history for all users.

        Args:
            year: Year to extract (for metadata)
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)
            on_progress: Optional callback for progress updates

        Returns:
            List of ListeningHistory objects, one per user

        Raises:
            RuntimeError: If not connected to server
        """
        if not self._server:
            raise RuntimeError("Not connected. Call connect() first.")

        users = self.get_users()
        histories = []

        if on_progress:
            on_progress(f"Found {len(users)} users to extract")

        for i, username in enumerate(users):
            if on_progress:
                on_progress(f"Extracting user {i + 1}/{len(users)}: {username}")

            try:
                history = self.extract_user_history(
                    username=username,
                    year=year,
                    start_date=start_date,
                    end_date=end_date,
                    on_progress=on_progress,
                )
                if history.total_tracks > 0:
                    histories.append(history)
            except Exception as e:
                # Log but continue with other users
                if on_progress:
                    on_progress(f"  Warning: Failed to extract history for {username}: {e}")
                else:
                    print(f"Warning: Failed to extract history for {username}: {e}")

        return histories

    def _get_user_account_id(self, username: str) -> int:
        """Get Plex account ID for a username.

        Args:
            username: Username to look up

        Returns:
            Account ID integer

        Raises:
            ValueError: If user not found
        """
        if not self._server:
            raise RuntimeError("Not connected. Call connect() first.")

        account = self._server.myPlexAccount()

        # Check if it's the account owner
        # Server owner uses local account ID 1, not their Plex.tv cloud ID
        if account.username == username:
            return 1

        # Check shared users and managed/home users
        for user in account.users():
            # Managed users may have title instead of username
            user_name = user.username or user.title or getattr(user, "name", None)
            if user_name == username:
                return user.id

        raise ValueError(f"User {username} not found on Plex server")
