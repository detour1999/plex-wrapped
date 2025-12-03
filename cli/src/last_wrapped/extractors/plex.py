# ABOUTME: Plex data extractor for fetching listening history from Plex servers.
# ABOUTME: Supports multi-user extraction with filtering by year and date ranges.

from datetime import datetime
from typing import Optional

from plexapi.server import PlexServer
from pydantic import BaseModel, Field


class Track(BaseModel):
    """Represents a single track listening event."""

    title: str
    artist: str
    album: str
    duration_ms: int
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

        # Get shared users
        for user in account.users():
            users.append(user.username)

        return users

    def extract_user_history(
        self,
        username: str,
        year: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ListeningHistory:
        """Extract listening history for a specific user.

        Args:
            username: Plex username to extract history for
            year: Year to extract (for metadata)
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)

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

        # Get user's listening history
        tracks = []
        try:
            # Get all track plays for the user
            history_items = music_library.history(
                accountID=self._get_user_account_id(username),
                mindate=start_date,
                maxdate=end_date,
            )

            for item in history_items:
                # Extract track information
                track = Track(
                    title=item.title,
                    artist=item.grandparentTitle or "Unknown Artist",
                    album=item.parentTitle or "Unknown Album",
                    duration_ms=item.duration if hasattr(item, "duration") else 0,
                    played_at=item.viewedAt,
                    user=username,
                    genre=", ".join([g.tag for g in item.genres]) if hasattr(item, "genres") and item.genres else None,
                    thumb_url=item.thumb if hasattr(item, "thumb") else None,
                )
                tracks.append(track)

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
                    if user.username == username:
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
    ) -> list[ListeningHistory]:
        """Extract listening history for all users.

        Args:
            year: Year to extract (for metadata)
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)

        Returns:
            List of ListeningHistory objects, one per user

        Raises:
            RuntimeError: If not connected to server
        """
        if not self._server:
            raise RuntimeError("Not connected. Call connect() first.")

        users = self.get_users()
        histories = []

        for username in users:
            try:
                history = self.extract_user_history(
                    username=username,
                    year=year,
                    start_date=start_date,
                    end_date=end_date,
                )
                if history.total_tracks > 0:
                    histories.append(history)
            except Exception as e:
                # Log but continue with other users
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
        if account.username == username:
            return account.id

        # Check shared users
        for user in account.users():
            if user.username == username:
                return user.id

        raise ValueError(f"User {username} not found on Plex server")
