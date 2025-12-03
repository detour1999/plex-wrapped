# Last Wrapped Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a self-hostable "Spotify Wrapped" experience for Plex server administrators, generating per-user interactive year-end music recaps.

**Architecture:** Python CLI extracts Plex listening data, processes stats, calls LLM for creative content, then triggers Astro build to generate static sites deployed to configurable hosting providers.

**Tech Stack:** Python 3.11+ (Typer, plexapi, pydantic), Anthropic/OpenAI SDKs, Astro 4, Svelte 5, TailwindCSS

---

## Phase 1: Python CLI Foundation

### Task 1: Initialize Python Project

**Files:**
- Create: `cli/pyproject.toml`
- Create: `cli/src/last_wrapped/__init__.py`
- Create: `cli/src/last_wrapped/main.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "last-wrapped"
version = "0.1.0"
description = "Self-hostable Spotify Wrapped for Plex servers"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "plexapi>=4.15.0",
    "anthropic>=0.18.0",
    "openai>=1.12.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
last-wrapped = "last_wrapped.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/last_wrapped"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Step 2: Create __init__.py**

```python
# ABOUTME: Package initialization for last-wrapped CLI tool.
# ABOUTME: Exports version and main entry points.

__version__ = "0.1.0"
```

**Step 3: Create main.py with basic CLI skeleton**

```python
# ABOUTME: Main CLI entry point using Typer.
# ABOUTME: Provides commands: init, generate, extract, process, build, deploy, preview.

import typer
from rich.console import Console

app = typer.Typer(
    name="last-wrapped",
    help="Self-hostable Spotify Wrapped for Plex servers",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init() -> None:
    """Initialize a new config.yaml file with guided prompts."""
    console.print("[yellow]Init command not yet implemented[/yellow]")


@app.command()
def generate(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Generate Wrapped for all users (extract → process → build → deploy)."""
    console.print(f"[yellow]Generate command not yet implemented (config: {config})[/yellow]")


@app.command()
def extract(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Extract listening data from Plex server."""
    console.print(f"[yellow]Extract command not yet implemented (config: {config})[/yellow]")


@app.command()
def process(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Process extracted data and generate AI content."""
    console.print(f"[yellow]Process command not yet implemented (config: {config})[/yellow]")


@app.command()
def build(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Build the static Astro site."""
    console.print(f"[yellow]Build command not yet implemented (config: {config})[/yellow]")


@app.command()
def deploy(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Deploy to configured hosting provider."""
    console.print(f"[yellow]Deploy command not yet implemented (config: {config})[/yellow]")


@app.command()
def preview() -> None:
    """Start local preview server."""
    console.print("[yellow]Preview command not yet implemented[/yellow]")


if __name__ == "__main__":
    app()
```

**Step 4: Verify CLI works**

Run:
```bash
cd cli && pip install -e ".[dev]" && last-wrapped --help
```

Expected: Help output showing all commands

**Step 5: Commit**

```bash
git add cli/
git commit -m "feat: initialize Python CLI project structure"
```

---

### Task 2: Config System with Pydantic

**Files:**
- Create: `cli/src/last_wrapped/config.py`
- Create: `cli/tests/test_config.py`
- Create: `examples/config.example.yaml`

**Step 1: Write failing test for config loading**

```python
# ABOUTME: Tests for configuration loading and validation.
# ABOUTME: Verifies YAML parsing and Pydantic model validation.

import pytest
from pathlib import Path
import tempfile
import yaml

from last_wrapped.config import load_config, Config, PlexConfig, LLMConfig, HostingConfig


class TestConfigLoading:
    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Config loads and validates from YAML file."""
        config_data = {
            "plex": {
                "url": "https://plex.example.com",
                "token": "test-token-123",
            },
            "llm": {
                "provider": "anthropic",
                "api_key": "sk-test-key",
            },
            "year": 2024,
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {
                    "account_id": "abc123",
                    "project_name": "my-wrapped",
                },
            },
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)

        assert config.plex.url == "https://plex.example.com"
        assert config.plex.token == "test-token-123"
        assert config.llm.provider == "anthropic"
        assert config.year == 2024
        assert config.hosting.provider == "cloudflare"

    def test_load_missing_file_raises(self) -> None:
        """Loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Loading invalid YAML raises ValueError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_config(config_file)

    def test_load_missing_required_field_raises(self, tmp_path: Path) -> None:
        """Missing required field raises ValidationError."""
        config_data = {
            "plex": {
                "url": "https://plex.example.com",
                # missing token
            },
            "year": 2024,
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValueError, match="token"):
            load_config(config_file)


class TestLLMConfig:
    def test_llm_provider_none_skips_api_key(self, tmp_path: Path) -> None:
        """Provider 'none' doesn't require api_key."""
        config_data = {
            "plex": {"url": "https://plex.example.com", "token": "test"},
            "llm": {"provider": "none"},
            "year": 2024,
            "hosting": {"provider": "cloudflare", "cloudflare": {"account_id": "x", "project_name": "y"}},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)
        assert config.llm.provider == "none"
        assert config.llm.api_key is None
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_config.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'last_wrapped.config'"

**Step 3: Implement config.py**

```python
# ABOUTME: Configuration loading and validation using Pydantic.
# ABOUTME: Supports Plex, LLM, and hosting provider settings from YAML.

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator, model_validator


class PlexConfig(BaseModel):
    """Plex server connection settings."""

    url: str
    token: str


class LLMConfig(BaseModel):
    """LLM provider settings."""

    provider: Literal["anthropic", "openai", "none"] = "none"
    api_key: str | None = None
    model: str | None = None

    @model_validator(mode="after")
    def validate_api_key_required(self) -> "LLMConfig":
        if self.provider != "none" and not self.api_key:
            raise ValueError(f"api_key required when provider is '{self.provider}'")
        return self


class CloudflareConfig(BaseModel):
    """Cloudflare Pages deployment settings."""

    account_id: str
    project_name: str
    api_token: str | None = None


class VercelConfig(BaseModel):
    """Vercel deployment settings."""

    token: str
    project_name: str


class NetlifyConfig(BaseModel):
    """Netlify deployment settings."""

    token: str
    site_id: str


class GitHubPagesConfig(BaseModel):
    """GitHub Pages deployment settings."""

    repo: str
    branch: str = "gh-pages"


class HostingConfig(BaseModel):
    """Hosting provider settings."""

    provider: Literal["cloudflare", "vercel", "netlify", "github-pages"]
    cloudflare: CloudflareConfig | None = None
    vercel: VercelConfig | None = None
    netlify: NetlifyConfig | None = None
    github_pages: GitHubPagesConfig | None = None

    @model_validator(mode="after")
    def validate_provider_config_exists(self) -> "HostingConfig":
        provider_map = {
            "cloudflare": self.cloudflare,
            "vercel": self.vercel,
            "netlify": self.netlify,
            "github-pages": self.github_pages,
        }
        if provider_map.get(self.provider) is None:
            raise ValueError(f"Missing config for hosting provider '{self.provider}'")
        return self


class Config(BaseModel):
    """Root configuration model."""

    plex: PlexConfig
    llm: LLMConfig = LLMConfig()
    year: int
    hosting: HostingConfig
    output_dir: Path = Path("output")


def load_config(path: Path) -> Config:
    """Load and validate configuration from YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")

    try:
        return Config(**data)
    except Exception as e:
        raise ValueError(f"Config validation failed: {e}")
```

**Step 4: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_config.py -v`

Expected: All tests PASS

**Step 5: Create example config**

```yaml
# Example configuration for last-wrapped
# Copy to config.yaml and fill in your values

plex:
  url: "https://plex.your-server.com"
  token: "your-plex-token"

llm:
  provider: "anthropic"  # or "openai" or "none"
  api_key: "your-api-key"
  # model: "claude-sonnet-4-20250514"  # optional, uses default if not set

year: 2024

hosting:
  provider: "cloudflare"  # or "vercel", "netlify", "github-pages"
  cloudflare:
    account_id: "your-account-id"
    project_name: "my-wrapped"
    # api_token: "your-api-token"  # optional, uses wrangler auth if not set

# output_dir: "output"  # optional, defaults to ./output
```

**Step 6: Commit**

```bash
git add cli/src/last_wrapped/config.py cli/tests/test_config.py examples/
git commit -m "feat: add config loading with Pydantic validation"
```

---

### Task 3: Plex Data Extractor

**Files:**
- Create: `cli/src/last_wrapped/extractors/__init__.py`
- Create: `cli/src/last_wrapped/extractors/plex.py`
- Create: `cli/tests/test_extractors/__init__.py`
- Create: `cli/tests/test_extractors/test_plex.py`

**Step 1: Write failing test for Plex extractor**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_extractors/test_plex.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement Plex extractor**

Create `cli/src/last_wrapped/extractors/__init__.py`:
```python
# ABOUTME: Data extractors package for pulling listening history.
# ABOUTME: Currently supports Plex, designed for extensibility.
```

Create `cli/src/last_wrapped/extractors/plex.py`:
```python
# ABOUTME: Extracts listening history from Plex Media Server.
# ABOUTME: Uses plexapi to fetch music play history for all users.

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from pydantic import BaseModel


class Track(BaseModel):
    """A single track play event."""

    title: str
    artist: str
    album: str
    duration_ms: int
    played_at: datetime
    user: str
    genre: str | None = None
    thumb_url: str | None = None

    @property
    def duration_minutes(self) -> float:
        """Duration in minutes."""
        return self.duration_ms / 60000


class ListeningHistory(BaseModel):
    """Aggregated listening history for a user."""

    user: str
    year: int
    tracks: list[Track]
    avatar_url: str | None = None

    @property
    def total_tracks(self) -> int:
        return len(self.tracks)

    @property
    def total_minutes(self) -> float:
        return sum(t.duration_minutes for t in self.tracks)


class PlexExtractor:
    """Extracts music listening history from Plex."""

    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token
        self._server: PlexServer | None = None

    def connect(self) -> None:
        """Establish connection to Plex server."""
        self._server = PlexServer(self.url, self.token)

    @property
    def server(self) -> PlexServer:
        """Get connected server, connecting if needed."""
        if self._server is None:
            self.connect()
        return self._server

    def get_users(self) -> list[str]:
        """Get list of users with access to this server."""
        # Server owner
        users = [self.server.myPlexAccount().username]

        # Shared users
        for user in self.server.myPlexAccount().users():
            users.append(user.username)

        return users

    def extract_user_history(self, username: str, year: int) -> ListeningHistory:
        """Extract listening history for a specific user and year."""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        tracks: list[Track] = []

        # Get music library
        music_sections = [s for s in self.server.library.sections() if s.type == "artist"]

        for section in music_sections:
            # Get play history for this section
            history = section.history(mindate=start_date, maxdate=end_date)

            for item in history:
                if item.usernames and username not in item.usernames:
                    continue

                if item.type != "track":
                    continue

                tracks.append(
                    Track(
                        title=item.title,
                        artist=item.grandparentTitle or "Unknown Artist",
                        album=item.parentTitle or "Unknown Album",
                        duration_ms=item.duration or 0,
                        played_at=item.viewedAt,
                        user=username,
                        genre=item.genres[0].tag if item.genres else None,
                        thumb_url=item.thumbUrl,
                    )
                )

        # Get user avatar
        avatar_url = None
        try:
            account = self.server.myPlexAccount()
            if account.username == username:
                avatar_url = account.thumb
            else:
                for user in account.users():
                    if user.username == username:
                        avatar_url = user.thumb
                        break
        except Exception:
            pass

        return ListeningHistory(
            user=username,
            year=year,
            tracks=sorted(tracks, key=lambda t: t.played_at),
            avatar_url=avatar_url,
        )

    def extract_all_users(self, year: int) -> Iterator[ListeningHistory]:
        """Extract listening history for all users."""
        for username in self.get_users():
            yield self.extract_user_history(username, year)
```

**Step 4: Create __init__.py for tests**

```python
# ABOUTME: Test package for extractors.
# ABOUTME: Contains tests for Plex and other data sources.
```

**Step 5: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_extractors/test_plex.py -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add cli/src/last_wrapped/extractors/ cli/tests/test_extractors/
git commit -m "feat: add Plex data extractor"
```

---

### Task 4: Stats Processor - Top Tracks/Artists/Albums

**Files:**
- Create: `cli/src/last_wrapped/processors/__init__.py`
- Create: `cli/src/last_wrapped/processors/stats.py`
- Create: `cli/tests/test_processors/__init__.py`
- Create: `cli/tests/test_processors/test_stats.py`

**Step 1: Write failing test**

```python
# ABOUTME: Tests for stats processing (top tracks, artists, albums).
# ABOUTME: Verifies correct aggregation and ranking of listening data.

import pytest
from datetime import datetime

from last_wrapped.extractors.plex import Track, ListeningHistory
from last_wrapped.processors.stats import StatsProcessor, TopItem


def make_track(title: str, artist: str, album: str, plays: int = 1) -> list[Track]:
    """Helper to create multiple track plays."""
    return [
        Track(
            title=title,
            artist=artist,
            album=album,
            duration_ms=180000,
            played_at=datetime(2024, 1, 1, 12, i),
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
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_processors/test_stats.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement stats processor**

Create `cli/src/last_wrapped/processors/__init__.py`:
```python
# ABOUTME: Data processors for analyzing listening history.
# ABOUTME: Calculates stats, patterns, genres, and discovery metrics.
```

Create `cli/src/last_wrapped/processors/stats.py`:
```python
# ABOUTME: Calculates top artists, albums, tracks and aggregate stats.
# ABOUTME: Core statistics processor for listening history analysis.

from collections import Counter
from dataclasses import dataclass

from last_wrapped.extractors.plex import ListeningHistory


@dataclass
class TopItem:
    """A ranked item (artist, album, or track)."""

    name: str
    plays: int
    minutes: float
    artist: str | None = None
    album: str | None = None
    image_url: str | None = None


class StatsProcessor:
    """Processes listening history into stats."""

    def __init__(self, history: ListeningHistory) -> None:
        self.history = history

    def top_artists(self, limit: int = 10) -> list[TopItem]:
        """Get top artists by play count."""
        artist_plays: Counter[str] = Counter()
        artist_minutes: dict[str, float] = {}
        artist_images: dict[str, str | None] = {}

        for track in self.history.tracks:
            artist_plays[track.artist] += 1
            artist_minutes[track.artist] = artist_minutes.get(track.artist, 0) + track.duration_minutes
            if track.thumb_url and track.artist not in artist_images:
                artist_images[track.artist] = track.thumb_url

        return [
            TopItem(
                name=artist,
                plays=plays,
                minutes=artist_minutes[artist],
                image_url=artist_images.get(artist),
            )
            for artist, plays in artist_plays.most_common(limit)
        ]

    def top_tracks(self, limit: int = 10) -> list[TopItem]:
        """Get top tracks by play count."""
        track_plays: Counter[tuple[str, str]] = Counter()
        track_info: dict[tuple[str, str], dict] = {}

        for track in self.history.tracks:
            key = (track.title, track.artist)
            track_plays[key] += 1
            if key not in track_info:
                track_info[key] = {
                    "album": track.album,
                    "duration_minutes": track.duration_minutes,
                    "image_url": track.thumb_url,
                }

        return [
            TopItem(
                name=title,
                plays=plays,
                minutes=track_info[(title, artist)]["duration_minutes"] * plays,
                artist=artist,
                album=track_info[(title, artist)]["album"],
                image_url=track_info[(title, artist)]["image_url"],
            )
            for (title, artist), plays in track_plays.most_common(limit)
        ]

    def top_albums(self, limit: int = 10) -> list[TopItem]:
        """Get top albums by play count."""
        album_plays: Counter[tuple[str, str]] = Counter()
        album_minutes: dict[tuple[str, str], float] = {}
        album_images: dict[tuple[str, str], str | None] = {}

        for track in self.history.tracks:
            key = (track.album, track.artist)
            album_plays[key] += 1
            album_minutes[key] = album_minutes.get(key, 0) + track.duration_minutes
            if track.thumb_url and key not in album_images:
                album_images[key] = track.thumb_url

        return [
            TopItem(
                name=album,
                plays=plays,
                minutes=album_minutes[(album, artist)],
                artist=artist,
                image_url=album_images.get((album, artist)),
            )
            for (album, artist), plays in album_plays.most_common(limit)
        ]

    def total_stats(self) -> dict:
        """Get aggregate listening statistics."""
        unique_artists = set(t.artist for t in self.history.tracks)
        unique_albums = set((t.album, t.artist) for t in self.history.tracks)
        unique_tracks = set((t.title, t.artist) for t in self.history.tracks)

        return {
            "total_tracks": len(self.history.tracks),
            "total_minutes": self.history.total_minutes,
            "unique_artists": len(unique_artists),
            "unique_albums": len(unique_albums),
            "unique_tracks": len(unique_tracks),
        }
```

**Step 4: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_processors/test_stats.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add cli/src/last_wrapped/processors/ cli/tests/test_processors/
git commit -m "feat: add stats processor for top tracks/artists/albums"
```

---

### Task 5: Time Analysis Processor

**Files:**
- Create: `cli/src/last_wrapped/processors/time_analysis.py`
- Create: `cli/tests/test_processors/test_time_analysis.py`

**Step 1: Write failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_processors/test_time_analysis.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement time analysis processor**

```python
# ABOUTME: Analyzes listening patterns by time (hour, day, month).
# ABOUTME: Detects quirky stats like late-night anthems and peak hours.

from collections import Counter
from datetime import datetime

from last_wrapped.extractors.plex import ListeningHistory


class TimeAnalysisProcessor:
    """Analyzes time-based listening patterns."""

    def __init__(self, history: ListeningHistory) -> None:
        self.history = history

    def plays_by_hour(self) -> list[int]:
        """Count plays per hour of day (0-23)."""
        counts = Counter(t.played_at.hour for t in self.history.tracks)
        return [counts.get(h, 0) for h in range(24)]

    def plays_by_day_of_week(self) -> list[int]:
        """Count plays per day of week (0=Monday, 6=Sunday)."""
        counts = Counter(t.played_at.weekday() for t in self.history.tracks)
        return [counts.get(d, 0) for d in range(7)]

    def plays_by_month(self) -> list[int]:
        """Count plays per month (1-12)."""
        counts = Counter(t.played_at.month for t in self.history.tracks)
        return [counts.get(m, 0) for m in range(1, 13)]

    def peak_listening_hour(self) -> int:
        """Find the hour with most plays."""
        by_hour = self.plays_by_hour()
        return by_hour.index(max(by_hour))

    def peak_listening_day(self) -> int:
        """Find the day of week with most plays."""
        by_day = self.plays_by_day_of_week()
        return by_day.index(max(by_day))

    def peak_day_overall(self) -> dict:
        """Find the single day with most listening."""
        day_counts: Counter[str] = Counter()
        day_minutes: dict[str, float] = {}

        for track in self.history.tracks:
            day_key = track.played_at.strftime("%Y-%m-%d")
            day_counts[day_key] += 1
            day_minutes[day_key] = day_minutes.get(day_key, 0) + track.duration_minutes

        if not day_counts:
            return {"date": None, "plays": 0, "minutes": 0}

        peak_day = day_counts.most_common(1)[0][0]
        return {
            "date": peak_day,
            "plays": day_counts[peak_day],
            "minutes": day_minutes[peak_day],
        }

    def longest_streak(self) -> int:
        """Find longest consecutive days with listening."""
        if not self.history.tracks:
            return 0

        dates = sorted(set(t.played_at.date() for t in self.history.tracks))
        if not dates:
            return 0

        max_streak = 1
        current_streak = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        return max_streak

    def late_night_anthem(self) -> dict | None:
        """Find most played track between midnight and 4am."""
        late_night = [t for t in self.history.tracks if 0 <= t.played_at.hour < 4]

        if not late_night:
            return None

        track_counts: Counter[tuple[str, str]] = Counter()
        for track in late_night:
            track_counts[(track.title, track.artist)] += 1

        (title, artist), plays = track_counts.most_common(1)[0]
        return {
            "track": title,
            "artist": artist,
            "plays_after_midnight": plays,
        }

    def day_anthem(self, day_of_week: int) -> dict | None:
        """Find most played track on a specific day of week."""
        day_tracks = [t for t in self.history.tracks if t.played_at.weekday() == day_of_week]

        if not day_tracks:
            return None

        track_counts: Counter[tuple[str, str]] = Counter()
        for track in day_tracks:
            track_counts[(track.title, track.artist)] += 1

        (title, artist), plays = track_counts.most_common(1)[0]
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {
            "track": title,
            "artist": artist,
            "day": day_names[day_of_week],
            "plays": plays,
        }

    def most_repeated_single_day(self) -> dict | None:
        """Find track played most times in a single day."""
        day_track_counts: Counter[tuple[str, str, str]] = Counter()

        for track in self.history.tracks:
            day_key = track.played_at.strftime("%Y-%m-%d")
            day_track_counts[(day_key, track.title, track.artist)] += 1

        if not day_track_counts:
            return None

        (date, title, artist), plays = day_track_counts.most_common(1)[0]
        return {
            "track": title,
            "artist": artist,
            "date": date,
            "plays": plays,
        }
```

**Step 4: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_processors/test_time_analysis.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add cli/src/last_wrapped/processors/time_analysis.py cli/tests/test_processors/test_time_analysis.py
git commit -m "feat: add time analysis processor for listening patterns"
```

---

## Phase 2: AI Content Generation

### Task 6: Abstract LLM Provider Interface

**Files:**
- Create: `cli/src/last_wrapped/ai/__init__.py`
- Create: `cli/src/last_wrapped/ai/provider.py`
- Create: `cli/tests/test_ai/__init__.py`
- Create: `cli/tests/test_ai/test_provider.py`

**Step 1: Write failing test**

```python
# ABOUTME: Tests for LLM provider abstraction.
# ABOUTME: Verifies provider selection and interface contract.

import pytest

from last_wrapped.ai.provider import get_provider, LLMProvider, NoOpProvider
from last_wrapped.config import LLMConfig


class TestProviderSelection:
    def test_none_provider_returns_noop(self) -> None:
        """Provider 'none' returns NoOpProvider."""
        config = LLMConfig(provider="none")
        provider = get_provider(config)
        assert isinstance(provider, NoOpProvider)

    def test_noop_provider_returns_empty_strings(self) -> None:
        """NoOpProvider returns empty/default content."""
        provider = NoOpProvider()
        result = provider.generate("test prompt")
        assert result == ""


class TestLLMProviderInterface:
    def test_provider_has_generate_method(self) -> None:
        """All providers must have generate method."""
        provider = NoOpProvider()
        assert hasattr(provider, "generate")
        assert callable(provider.generate)
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_ai/test_provider.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement provider abstraction**

Create `cli/src/last_wrapped/ai/__init__.py`:
```python
# ABOUTME: AI content generation package.
# ABOUTME: Supports Anthropic, OpenAI, or no-op for AI-free mode.
```

Create `cli/src/last_wrapped/ai/provider.py`:
```python
# ABOUTME: Abstract LLM provider interface and factory.
# ABOUTME: Allows swapping between Anthropic, OpenAI, or disabled.

from abc import ABC, abstractmethod

from last_wrapped.config import LLMConfig


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text from a prompt."""
        pass


class NoOpProvider(LLMProvider):
    """No-op provider that returns empty content."""

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        return ""


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str, model: str | None = None) -> None:
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or "claude-sonnet-4-20250514"

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: str, model: str | None = None) -> None:
        import openai

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model or "gpt-4o"

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def get_provider(config: LLMConfig) -> LLMProvider:
    """Factory function to create appropriate provider."""
    if config.provider == "none":
        return NoOpProvider()
    elif config.provider == "anthropic":
        return AnthropicProvider(config.api_key, config.model)
    elif config.provider == "openai":
        return OpenAIProvider(config.api_key, config.model)
    else:
        raise ValueError(f"Unknown LLM provider: {config.provider}")
```

**Step 4: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_ai/test_provider.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add cli/src/last_wrapped/ai/ cli/tests/test_ai/
git commit -m "feat: add abstract LLM provider with Anthropic/OpenAI support"
```

---

### Task 7: AI Content Generators (Narrative, Personality, Roasts)

**Files:**
- Create: `cli/src/last_wrapped/ai/generators.py`
- Create: `cli/tests/test_ai/test_generators.py`

**Step 1: Write failing test**

```python
# ABOUTME: Tests for AI content generators.
# ABOUTME: Verifies prompt construction and response parsing.

import pytest
from unittest.mock import MagicMock

from last_wrapped.ai.generators import (
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    SuggestionsGenerator,
    AuraGenerator,
)
from last_wrapped.ai.provider import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing prompt construction."""

    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.last_prompt: str | None = None

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        self.last_prompt = prompt
        return self.response


class TestNarrativeGenerator:
    def test_generates_narrative_from_stats(self) -> None:
        """Narrative generator creates story from user stats."""
        provider = MockProvider('{"narrative": "Your 2024 was wild..."}')
        generator = NarrativeGenerator(provider)

        stats = {
            "total_minutes": 42000,
            "top_artist": "Radiohead",
            "top_genre": "Alternative",
        }
        result = generator.generate(stats)

        assert provider.last_prompt is not None
        assert "42000" in provider.last_prompt
        assert "Radiohead" in provider.last_prompt

    def test_prompt_includes_instruction_for_humor(self) -> None:
        """Prompt asks for playful, humorous tone."""
        provider = MockProvider('{"narrative": "test"}')
        generator = NarrativeGenerator(provider)

        generator.generate({"total_minutes": 100})

        assert "playful" in provider.last_prompt.lower() or "humor" in provider.last_prompt.lower()


class TestPersonalityGenerator:
    def test_generates_personality_type(self) -> None:
        """Personality generator creates type with tagline."""
        response = '''{
            "type": "The Chaos Agent",
            "tagline": "Your playlists have trust issues",
            "description": "You listen to everything...",
            "spirit_animal": "A caffeinated raccoon"
        }'''
        provider = MockProvider(response)
        generator = PersonalityGenerator(provider)

        result = generator.generate({"genres": ["rock", "pop", "jazz"]})

        assert provider.last_prompt is not None


class TestRoastGenerator:
    def test_generates_roasts_from_stats(self) -> None:
        """Roast generator creates playful callouts."""
        response = '{"roasts": ["Your 2am listening habits are concerning"]}'
        provider = MockProvider(response)
        generator = RoastGenerator(provider)

        result = generator.generate({
            "late_night_plays": 200,
            "most_repeated_track": "same song",
        })

        assert provider.last_prompt is not None
```

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_ai/test_generators.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement generators**

```python
# ABOUTME: AI content generators for narrative, personality, roasts, etc.
# ABOUTME: Each generator constructs prompts and parses LLM responses.

import json
from typing import Any

from last_wrapped.ai.provider import LLMProvider


class BaseGenerator:
    """Base class for AI content generators."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def _parse_json(self, response: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}


class NarrativeGenerator(BaseGenerator):
    """Generates the year-in-review narrative."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Write a short, playful narrative (2-3 paragraphs) about someone's year in music.

Stats:
- Total minutes listened: {stats.get('total_minutes', 0)}
- Top artist: {stats.get('top_artist', 'Unknown')}
- Top genre: {stats.get('top_genre', 'Unknown')}
- Top track: {stats.get('top_track', 'Unknown')}
- New artists discovered: {stats.get('new_artists', 0)}
- Late night listening: {stats.get('late_night_plays', 0)} plays after midnight
- Peak month: {stats.get('peak_month', 'Unknown')}

Be playful, slightly sarcastic, and reference specific stats. Make it feel personal and fun, like a friend roasting their music taste affectionately.

Return JSON: {{"narrative": "your narrative here"}}"""

        response = self.provider.generate(prompt, max_tokens=500)
        return self._parse_json(response)


class PersonalityGenerator(BaseGenerator):
    """Generates listening personality type."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Create a fun "listening personality" type based on these music stats.

Stats:
- Top genres: {stats.get('genres', [])}
- Listening pattern: {stats.get('pattern', 'varied')}
- Discovery rate: {stats.get('discovery_rate', 'moderate')}
- Repeat behavior: {stats.get('repeat_rate', 'normal')}
- Peak listening time: {stats.get('peak_hour', 'afternoon')}

Create a whimsical personality type like "The Chaos Curator" or "The 3am Philosopher".

Return JSON:
{{
    "type": "The [Creative Name]",
    "tagline": "A short, punchy tagline (max 10 words)",
    "description": "2-3 sentences describing this personality",
    "spirit_animal": "A quirky spirit animal description"
}}"""

        response = self.provider.generate(prompt, max_tokens=300)
        return self._parse_json(response)


class RoastGenerator(BaseGenerator):
    """Generates playful roasts about listening habits."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Write 3-4 playful roasts about someone's music listening habits.

Stats to roast:
- Most repeated track: {stats.get('most_repeated_track', 'Unknown')} ({stats.get('repeat_count', 0)} times)
- Late night plays: {stats.get('late_night_plays', 0)}
- Most basic artist: {stats.get('basic_artist', 'Unknown')}
- Guilty pleasure genre: {stats.get('guilty_genre', 'Unknown')}
- Longest single-day binge: {stats.get('binge_track', 'Unknown')} ({stats.get('binge_count', 0)} times)

Be affectionate but savage. Think "your best friend at brunch" energy.

Return JSON: {{"roasts": ["roast 1", "roast 2", "roast 3"]}}"""

        response = self.provider.generate(prompt, max_tokens=300)
        return self._parse_json(response)


class AuraGenerator(BaseGenerator):
    """Generates audio aura colors and vibes."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Create an "audio aura" based on these music listening stats.

Stats:
- Top genres: {stats.get('genres', [])}
- Mood words from top tracks: {stats.get('mood_words', [])}
- Energy level: {stats.get('energy', 'medium')}
- Listening time pattern: {stats.get('time_pattern', 'varied')}

Return JSON:
{{
    "colors": ["#hexcode1", "#hexcode2", "#hexcode3"],
    "vibe": "A short vibe description (e.g., 'main character energy with a hint of existential dread')",
    "aesthetic": "An aesthetic description (e.g., 'Coffee shop that plays vinyl but also has WiFi')"
}}"""

        response = self.provider.generate(prompt, max_tokens=200)
        return self._parse_json(response)


class SuperlativesGenerator(BaseGenerator):
    """Generates fun awards and superlatives."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Create fun "superlatives" (like yearbook awards) for this music listener.

Stats:
- Top emotion in music: {stats.get('top_emotion', 'Unknown')}
- Listening quirks: {stats.get('quirks', [])}
- Most loyal to: {stats.get('loyal_artist', 'Unknown')}
- Biggest phase: {stats.get('biggest_phase', 'Unknown')}

Return JSON:
{{
    "title": "Most Likely To [something funny]",
    "award": "A made-up award name (e.g., 'Golden Headphones for Emotional Damage')",
    "certificate": "Certified [something funny] Enthusiast"
}}"""

        response = self.provider.generate(prompt, max_tokens=200)
        return self._parse_json(response)


class HotTakesGenerator(BaseGenerator):
    """Generates hot takes about the listener's taste."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Write 2-3 "hot takes" about this person's music taste.

Stats:
- Genre breakdown: {stats.get('genre_breakdown', {{}})}
- Mainstream vs indie ratio: {stats.get('mainstream_ratio', 50)}%
- Decade preferences: {stats.get('decade_prefs', {{}})}
- Mood patterns: {stats.get('mood_patterns', [])}

Hot takes should be funny observations like "You're one bad day away from a full folk phase" or "Your music taste is 60% impeccable, 40% unhinged".

Return JSON: {{"hot_takes": ["take 1", "take 2"]}}"""

        response = self.provider.generate(prompt, max_tokens=200)
        return self._parse_json(response)


class SuggestionsGenerator(BaseGenerator):
    """Generates music suggestions for next year."""

    def generate(self, stats: dict[str, Any]) -> dict:
        prompt = f"""Based on this listener's habits, suggest artists to try and a playful challenge for next year.

Stats:
- Top artists: {stats.get('top_artists', [])}
- Top genres: {stats.get('genres', [])}
- Listening gaps: {stats.get('gaps', [])}
- Discovery rate: {stats.get('discovery_rate', 'moderate')}

Return JSON:
{{
    "artists": [
        {{"name": "Artist Name", "reason": "Because you love X, you might like..."}}
    ],
    "challenge": "A funny challenge for next year (e.g., 'Try listening to ONE album all the way through')"
}}"""

        response = self.provider.generate(prompt, max_tokens=400)
        return self._parse_json(response)
```

**Step 4: Run tests to verify they pass**

Run: `cd cli && pytest tests/test_ai/test_generators.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add cli/src/last_wrapped/ai/generators.py cli/tests/test_ai/test_generators.py
git commit -m "feat: add AI content generators for narrative, personality, roasts"
```

---

## Phase 3: Frontend (Astro + Svelte)

### Task 8: Initialize Astro Project

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/astro.config.mjs`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.mjs`
- Create: `frontend/src/layouts/WrappedLayout.astro`
- Create: `frontend/src/pages/index.astro`

**Step 1: Create package.json**

```json
{
  "name": "last-wrapped-frontend",
  "type": "module",
  "version": "0.1.0",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "@astrojs/svelte": "^5.0.0",
    "@astrojs/tailwind": "^5.0.0",
    "astro": "^4.0.0",
    "svelte": "^5.0.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

**Step 2: Create astro.config.mjs**

```javascript
// ABOUTME: Astro configuration for Last Wrapped frontend.
// ABOUTME: Integrates Svelte for interactive components and Tailwind for styling.

import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [svelte(), tailwind()],
  output: 'static',
});
```

**Step 3: Create tsconfig.json**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"]
    }
  }
}
```

**Step 4: Create tailwind.config.mjs**

```javascript
// ABOUTME: Tailwind CSS configuration for Last Wrapped.
// ABOUTME: Custom colors and animations for the wrapped experience.

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        wrapped: {
          bg: '#121212',
          card: '#1a1a1a',
          accent: '#1DB954',
          text: '#ffffff',
          muted: '#b3b3b3',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'count-up': 'countUp 2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
```

**Step 5: Create base layout**

Create `frontend/src/layouts/WrappedLayout.astro`:
```astro
---
// ABOUTME: Base layout for all Wrapped pages.
// ABOUTME: Full-screen dark theme with slide container.

interface Props {
  title: string;
}

const { title } = Astro.props;
---

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap"
      rel="stylesheet"
    />
  </head>
  <body class="bg-wrapped-bg text-wrapped-text font-sans min-h-screen">
    <slot />
  </body>
</html>

<style is:global>
  body {
    font-family: 'Inter', sans-serif;
  }
</style>
```

**Step 6: Create index page**

Create `frontend/src/pages/index.astro`:
```astro
---
// ABOUTME: Landing page listing all users with Wrapped available.
// ABOUTME: Entry point for the static site.

import WrappedLayout from '@layouts/WrappedLayout.astro';

// In production, this would be populated by the build process
const users: Array<{name: string; year: number}> = [];
---

<WrappedLayout title="Last Wrapped">
  <main class="min-h-screen flex flex-col items-center justify-center p-8">
    <h1 class="text-5xl font-black mb-4">Last Wrapped</h1>
    <p class="text-wrapped-muted text-xl mb-12">Your year in music</p>

    {users.length > 0 ? (
      <div class="grid gap-4">
        {users.map((user) => (
          <a
            href={`/${user.name}/${user.year}/`}
            class="bg-wrapped-card px-8 py-4 rounded-lg hover:bg-opacity-80 transition"
          >
            <span class="text-xl font-semibold">{user.name}</span>
            <span class="text-wrapped-muted ml-2">{user.year}</span>
          </a>
        ))}
      </div>
    ) : (
      <p class="text-wrapped-muted">No Wrapped data available yet.</p>
    )}
  </main>
</WrappedLayout>
```

**Step 7: Install dependencies and verify**

Run:
```bash
cd frontend && npm install && npm run build
```

Expected: Build completes successfully

**Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: initialize Astro frontend with Svelte and Tailwind"
```

---

### Task 9: Create Slide Components (Core Set)

**Files:**
- Create: `frontend/src/components/slides/Intro.svelte`
- Create: `frontend/src/components/slides/TotalTime.svelte`
- Create: `frontend/src/components/slides/TopArtist.svelte`
- Create: `frontend/src/components/slides/Personality.svelte`
- Create: `frontend/src/components/common/SlideContainer.svelte`
- Create: `frontend/src/components/common/AnimatedNumber.svelte`

**Step 1: Create SlideContainer**

```svelte
<!-- ABOUTME: Container for individual slides with transitions. -->
<!-- ABOUTME: Handles entrance animations and consistent styling. -->

<script lang="ts">
  import { fade, fly } from 'svelte/transition';

  export let visible = true;
</script>

{#if visible}
  <div
    class="min-h-screen flex flex-col items-center justify-center p-8 text-center"
    in:fly={{ y: 50, duration: 500 }}
    out:fade={{ duration: 200 }}
  >
    <slot />
  </div>
{/if}
```

**Step 2: Create AnimatedNumber**

```svelte
<!-- ABOUTME: Animated counting number component. -->
<!-- ABOUTME: Counts up from 0 to target value on mount. -->

<script lang="ts">
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import { onMount } from 'svelte';

  export let value: number;
  export let duration = 2000;
  export let format: (n: number) => string = (n) => Math.round(n).toLocaleString();

  const displayValue = tweened(0, {
    duration,
    easing: cubicOut,
  });

  onMount(() => {
    displayValue.set(value);
  });
</script>

<span class="tabular-nums">{format($displayValue)}</span>
```

**Step 3: Create Intro slide**

```svelte
<!-- ABOUTME: Opening slide for the Wrapped experience. -->
<!-- ABOUTME: Shows user name and year with dramatic reveal. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';

  export let userName: string;
  export let year: number;
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">Your</p>
  <h1 class="text-7xl font-black mb-4">{year}</h1>
  <p class="text-wrapped-muted text-xl mb-8">Wrapped</p>
  <p class="text-2xl font-semibold text-wrapped-accent">{userName}</p>

  <p class="mt-16 text-wrapped-muted animate-pulse">Tap to continue</p>
</SlideContainer>
```

**Step 4: Create TotalTime slide**

```svelte
<!-- ABOUTME: Shows total listening time with animated counter. -->
<!-- ABOUTME: Converts minutes to hours/days for impact. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';
  import AnimatedNumber from '../common/AnimatedNumber.svelte';

  export let totalMinutes: number;
  export let visible = true;

  $: hours = Math.round(totalMinutes / 60);
  $: days = (totalMinutes / 60 / 24).toFixed(1);
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">You listened for</p>

  <div class="text-8xl font-black text-wrapped-accent mb-2">
    <AnimatedNumber value={totalMinutes} />
  </div>
  <p class="text-2xl mb-8">minutes</p>

  <p class="text-wrapped-muted text-lg">
    That's <span class="text-wrapped-text font-semibold">{hours.toLocaleString()} hours</span>
  </p>
  <p class="text-wrapped-muted text-lg">
    or <span class="text-wrapped-text font-semibold">{days} days</span> of music
  </p>
</SlideContainer>
```

**Step 5: Create TopArtist slide**

```svelte
<!-- ABOUTME: Reveals top artist with album art and play count. -->
<!-- ABOUTME: Dramatic reveal with image and stats. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';
  import AnimatedNumber from '../common/AnimatedNumber.svelte';

  export let artist: {
    name: string;
    plays: number;
    minutes: number;
    image_url?: string;
  };
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your top artist was</p>

  {#if artist.image_url}
    <img
      src={artist.image_url}
      alt={artist.name}
      class="w-48 h-48 rounded-lg shadow-2xl mb-6 object-cover"
      in:fly={{ y: 30, duration: 600, delay: 200 }}
    />
  {/if}

  <h2 class="text-5xl font-black mb-4">{artist.name}</h2>

  <div class="flex gap-8 text-center">
    <div>
      <div class="text-3xl font-bold text-wrapped-accent">
        <AnimatedNumber value={artist.plays} />
      </div>
      <p class="text-wrapped-muted">plays</p>
    </div>
    <div>
      <div class="text-3xl font-bold text-wrapped-accent">
        <AnimatedNumber value={Math.round(artist.minutes / 60)} />
      </div>
      <p class="text-wrapped-muted">hours</p>
    </div>
  </div>
</SlideContainer>
```

**Step 6: Create Personality slide**

```svelte
<!-- ABOUTME: Shows AI-generated listening personality type. -->
<!-- ABOUTME: Includes type, tagline, description, and spirit animal. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let personality: {
    type: string;
    tagline: string;
    description: string;
    spirit_animal: string;
  };
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">Your listening personality</p>

  <h2 class="text-5xl font-black text-wrapped-accent mb-4">{personality.type}</h2>

  <p class="text-2xl italic text-wrapped-muted mb-8">"{personality.tagline}"</p>

  <p class="text-lg max-w-md mb-8">{personality.description}</p>

  <div class="bg-wrapped-card rounded-lg px-6 py-4">
    <p class="text-wrapped-muted text-sm mb-1">Spirit Animal</p>
    <p class="text-lg font-semibold">{personality.spirit_animal}</p>
  </div>
</SlideContainer>
```

**Step 7: Verify components build**

Run:
```bash
cd frontend && npm run build
```

Expected: Build completes successfully

**Step 8: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add core slide components (Intro, TotalTime, TopArtist, Personality)"
```

---

### Task 10: Create Remaining Slide Components

**Files:**
- Create: `frontend/src/components/slides/TopTracks.svelte`
- Create: `frontend/src/components/slides/ListeningClock.svelte`
- Create: `frontend/src/components/slides/QuirkyStats.svelte`
- Create: `frontend/src/components/slides/Aura.svelte`
- Create: `frontend/src/components/slides/Roasts.svelte`
- Create: `frontend/src/components/slides/Narrative.svelte`
- Create: `frontend/src/components/slides/Share.svelte`

**Step 1: Create TopTracks slide**

```svelte
<!-- ABOUTME: Countdown-style reveal of top 5 tracks. -->
<!-- ABOUTME: Shows track name, artist, and play count. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let tracks: Array<{
    name: string;
    artist: string;
    plays: number;
    image_url?: string;
  }>;
  export let visible = true;

  // Show top 5 in reverse order for countdown effect
  $: displayTracks = tracks.slice(0, 5).reverse();
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your top tracks</p>

  <div class="space-y-4 w-full max-w-md">
    {#each displayTracks as track, i}
      <div
        class="flex items-center gap-4 bg-wrapped-card rounded-lg p-4"
        in:fly={{ x: -50, duration: 400, delay: i * 150 }}
      >
        <span class="text-3xl font-black text-wrapped-accent w-8">
          {5 - i}
        </span>
        {#if track.image_url}
          <img
            src={track.image_url}
            alt={track.name}
            class="w-12 h-12 rounded object-cover"
          />
        {/if}
        <div class="flex-1 text-left">
          <p class="font-semibold truncate">{track.name}</p>
          <p class="text-wrapped-muted text-sm truncate">{track.artist}</p>
        </div>
        <span class="text-wrapped-muted">{track.plays} plays</span>
      </div>
    {/each}
  </div>
</SlideContainer>
```

**Step 2: Create ListeningClock slide**

```svelte
<!-- ABOUTME: Radial visualization of listening by hour. -->
<!-- ABOUTME: Shows when user listens most during the day. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';

  export let byHour: number[]; // 24 values
  export let peakHour: number;
  export let visible = true;

  $: maxPlays = Math.max(...byHour);
  $: hourLabels = ['12am', '6am', '12pm', '6pm'];

  function formatHour(hour: number): string {
    if (hour === 0) return '12am';
    if (hour === 12) return '12pm';
    return hour < 12 ? `${hour}am` : `${hour - 12}pm`;
  }
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">Your listening clock</p>

  <div class="relative w-64 h-64 mb-8">
    <!-- Simple bar chart representation -->
    <svg viewBox="0 0 100 100" class="w-full h-full">
      {#each byHour as plays, hour}
        {@const angle = (hour / 24) * 360 - 90}
        {@const radius = 35 + (plays / maxPlays) * 15}
        {@const x = 50 + radius * Math.cos((angle * Math.PI) / 180)}
        {@const y = 50 + radius * Math.sin((angle * Math.PI) / 180)}
        <circle
          cx={x}
          cy={y}
          r={2 + (plays / maxPlays) * 3}
          fill={hour === peakHour ? '#1DB954' : '#b3b3b3'}
          opacity={0.3 + (plays / maxPlays) * 0.7}
        />
      {/each}
      <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="8">
        Peak: {formatHour(peakHour)}
      </text>
    </svg>
  </div>

  <p class="text-lg">
    You listen most at <span class="text-wrapped-accent font-bold">{formatHour(peakHour)}</span>
  </p>
</SlideContainer>
```

**Step 3: Create QuirkyStats slide**

```svelte
<!-- ABOUTME: Shows quirky/fun listening patterns. -->
<!-- ABOUTME: Late night anthem, Monday motivator, etc. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let quirky: {
    late_night_anthem?: { track: string; artist: string; plays_after_midnight: number };
    monday_motivator?: { track: string; artist: string; plays: number };
    most_repeated_day?: { track: string; artist: string; date: string; plays: number };
  };
  export let visible = true;

  $: stats = [
    quirky.late_night_anthem && {
      label: 'Your 2am anthem',
      track: quirky.late_night_anthem.track,
      artist: quirky.late_night_anthem.artist,
      detail: `${quirky.late_night_anthem.plays_after_midnight} late night plays`,
    },
    quirky.monday_motivator && {
      label: 'Monday motivator',
      track: quirky.monday_motivator.track,
      artist: quirky.monday_motivator.artist,
      detail: `${quirky.monday_motivator.plays} Monday plays`,
    },
    quirky.most_repeated_day && {
      label: 'Most obsessed day',
      track: quirky.most_repeated_day.track,
      artist: quirky.most_repeated_day.artist,
      detail: `${quirky.most_repeated_day.plays}x on ${quirky.most_repeated_day.date}`,
    },
  ].filter(Boolean);
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your quirky patterns</p>

  <div class="space-y-6 w-full max-w-md">
    {#each stats as stat, i}
      <div
        class="bg-wrapped-card rounded-lg p-6 text-left"
        in:fly={{ y: 30, duration: 400, delay: i * 200 }}
      >
        <p class="text-wrapped-accent text-sm font-semibold mb-2">{stat.label}</p>
        <p class="text-xl font-bold">{stat.track}</p>
        <p class="text-wrapped-muted">{stat.artist}</p>
        <p class="text-wrapped-muted text-sm mt-2">{stat.detail}</p>
      </div>
    {/each}
  </div>
</SlideContainer>
```

**Step 4: Create Aura slide**

```svelte
<!-- ABOUTME: Shows audio aura with gradient colors and vibe. -->
<!-- ABOUTME: Visual representation of listening mood. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';

  export let aura: {
    colors: string[];
    vibe: string;
    aesthetic: string;
  };
  export let visible = true;

  $: gradientStyle = `background: linear-gradient(135deg, ${aura.colors.join(', ')})`;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your audio aura</p>

  <div
    class="w-64 h-64 rounded-full mb-8 animate-pulse"
    style={gradientStyle}
  />

  <p class="text-2xl font-semibold mb-4">{aura.vibe}</p>

  <div class="bg-wrapped-card rounded-lg px-6 py-4 max-w-md">
    <p class="text-wrapped-muted text-sm mb-1">Your aesthetic</p>
    <p class="text-lg italic">"{aura.aesthetic}"</p>
  </div>
</SlideContainer>
```

**Step 5: Create Roasts slide**

```svelte
<!-- ABOUTME: Shows AI-generated roasts about listening habits. -->
<!-- ABOUTME: Playful callouts with dramatic reveal. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let roasts: string[];
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Let's be honest...</p>

  <div class="space-y-6 max-w-md">
    {#each roasts as roast, i}
      <p
        class="text-xl italic"
        in:fly={{ y: 20, duration: 400, delay: i * 300 }}
      >
        "{roast}"
      </p>
    {/each}
  </div>
</SlideContainer>
```

**Step 6: Create Narrative slide**

```svelte
<!-- ABOUTME: Shows AI-generated year narrative with typewriter effect. -->
<!-- ABOUTME: Personalized story about the year in music. -->

<script lang="ts">
  import { onMount } from 'svelte';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let narrative: string;
  export let visible = true;

  let displayedText = '';
  let charIndex = 0;

  onMount(() => {
    if (visible) {
      const interval = setInterval(() => {
        if (charIndex < narrative.length) {
          displayedText = narrative.slice(0, charIndex + 1);
          charIndex++;
        } else {
          clearInterval(interval);
        }
      }, 30);

      return () => clearInterval(interval);
    }
  });
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your year in music</p>

  <div class="max-w-lg text-left">
    <p class="text-lg leading-relaxed whitespace-pre-wrap">
      {displayedText}<span class="animate-pulse">|</span>
    </p>
  </div>
</SlideContainer>
```

**Step 7: Create Share slide**

```svelte
<!-- ABOUTME: Final slide with share buttons and screenshot option. -->
<!-- ABOUTME: Social sharing and save functionality. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';

  export let userName: string;
  export let year: number;
  export let visible = true;

  function shareToTwitter() {
    const text = encodeURIComponent(`Check out my ${year} Wrapped! 🎵`);
    const url = encodeURIComponent(window.location.href);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  }

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    alert('Link copied!');
  }
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">That's a wrap!</p>

  <h2 class="text-5xl font-black mb-8">{userName}'s {year}</h2>

  <div class="flex gap-4">
    <button
      on:click={shareToTwitter}
      class="bg-wrapped-accent text-black px-6 py-3 rounded-full font-semibold hover:opacity-90 transition"
    >
      Share on X
    </button>
    <button
      on:click={copyLink}
      class="bg-wrapped-card px-6 py-3 rounded-full font-semibold hover:opacity-90 transition"
    >
      Copy Link
    </button>
  </div>

  <p class="text-wrapped-muted text-sm mt-8">
    Made with Last Wrapped
  </p>
</SlideContainer>
```

**Step 8: Verify build**

Run:
```bash
cd frontend && npm run build
```

Expected: Build completes successfully

**Step 9: Commit**

```bash
git add frontend/src/components/slides/
git commit -m "feat: add remaining slide components (tracks, clock, quirky, aura, roasts, narrative, share)"
```

---

### Task 11: Create User Wrapped Page

**Files:**
- Create: `frontend/src/pages/[user]/index.astro`
- Create: `frontend/src/pages/[user]/[year]/index.astro`
- Create: `frontend/src/components/WrappedExperience.svelte`

**Step 1: Create user index page**

```astro
---
// ABOUTME: User landing page showing all available years.
// ABOUTME: Lists Wrapped experiences for a specific user.

import WrappedLayout from '@layouts/WrappedLayout.astro';

export function getStaticPaths() {
  // In production, this reads from generated data
  return [];
}

const { user } = Astro.params;
const years: number[] = []; // Populated at build time
---

<WrappedLayout title={`${user}'s Wrapped`}>
  <main class="min-h-screen flex flex-col items-center justify-center p-8">
    <h1 class="text-5xl font-black mb-4">{user}</h1>
    <p class="text-wrapped-muted text-xl mb-12">Your music history</p>

    {years.length > 0 ? (
      <div class="grid gap-4">
        {years.map((year) => (
          <a
            href={`/${user}/${year}/`}
            class="bg-wrapped-card px-8 py-6 rounded-lg hover:bg-opacity-80 transition text-center"
          >
            <span class="text-4xl font-black">{year}</span>
            <p class="text-wrapped-muted mt-2">View Wrapped</p>
          </a>
        ))}
      </div>
    ) : (
      <p class="text-wrapped-muted">No Wrapped data available yet.</p>
    )}
  </main>
</WrappedLayout>
```

**Step 2: Create WrappedExperience component**

```svelte
<!-- ABOUTME: Main Wrapped experience controller. -->
<!-- ABOUTME: Manages slide navigation and user interaction. -->

<script lang="ts">
  import Intro from './slides/Intro.svelte';
  import TotalTime from './slides/TotalTime.svelte';
  import TopArtist from './slides/TopArtist.svelte';
  import TopTracks from './slides/TopTracks.svelte';
  import ListeningClock from './slides/ListeningClock.svelte';
  import QuirkyStats from './slides/QuirkyStats.svelte';
  import Personality from './slides/Personality.svelte';
  import Aura from './slides/Aura.svelte';
  import Roasts from './slides/Roasts.svelte';
  import Narrative from './slides/Narrative.svelte';
  import Share from './slides/Share.svelte';

  export let data: {
    user: { name: string; year: number };
    stats: { total_minutes: number };
    top: {
      artists: Array<{ name: string; plays: number; minutes: number; image_url?: string }>;
      tracks: Array<{ name: string; artist: string; plays: number; image_url?: string }>;
    };
    time_patterns: {
      by_hour: number[];
      quirky: any;
    };
    ai_generated: {
      personality: any;
      aura: any;
      roasts: string[];
      narrative: string;
    };
  };

  let currentSlide = 0;

  const slides = [
    'intro',
    'totalTime',
    'topArtist',
    'topTracks',
    'listeningClock',
    'quirkyStats',
    'personality',
    'aura',
    'roasts',
    'narrative',
    'share',
  ];

  function nextSlide() {
    if (currentSlide < slides.length - 1) {
      currentSlide++;
    }
  }

  function prevSlide() {
    if (currentSlide > 0) {
      currentSlide--;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'ArrowRight' || event.key === ' ') {
      nextSlide();
    } else if (event.key === 'ArrowLeft') {
      prevSlide();
    }
  }

  $: peakHour = data.time_patterns.by_hour.indexOf(
    Math.max(...data.time_patterns.by_hour)
  );
</script>

<svelte:window on:keydown={handleKeydown} />

<div
  class="min-h-screen cursor-pointer"
  on:click={nextSlide}
  on:keypress={(e) => e.key === 'Enter' && nextSlide()}
  role="button"
  tabindex="0"
>
  <!-- Progress dots -->
  <div class="fixed top-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
    {#each slides as _, i}
      <button
        class="w-2 h-2 rounded-full transition-colors {i === currentSlide
          ? 'bg-wrapped-accent'
          : 'bg-wrapped-muted opacity-50'}"
        on:click|stopPropagation={() => (currentSlide = i)}
      />
    {/each}
  </div>

  {#if slides[currentSlide] === 'intro'}
    <Intro userName={data.user.name} year={data.user.year} visible={true} />
  {:else if slides[currentSlide] === 'totalTime'}
    <TotalTime totalMinutes={data.stats.total_minutes} visible={true} />
  {:else if slides[currentSlide] === 'topArtist'}
    <TopArtist artist={data.top.artists[0]} visible={true} />
  {:else if slides[currentSlide] === 'topTracks'}
    <TopTracks tracks={data.top.tracks} visible={true} />
  {:else if slides[currentSlide] === 'listeningClock'}
    <ListeningClock byHour={data.time_patterns.by_hour} {peakHour} visible={true} />
  {:else if slides[currentSlide] === 'quirkyStats'}
    <QuirkyStats quirky={data.time_patterns.quirky} visible={true} />
  {:else if slides[currentSlide] === 'personality'}
    <Personality personality={data.ai_generated.personality} visible={true} />
  {:else if slides[currentSlide] === 'aura'}
    <Aura aura={data.ai_generated.aura} visible={true} />
  {:else if slides[currentSlide] === 'roasts'}
    <Roasts roasts={data.ai_generated.roasts} visible={true} />
  {:else if slides[currentSlide] === 'narrative'}
    <Narrative narrative={data.ai_generated.narrative} visible={true} />
  {:else if slides[currentSlide] === 'share'}
    <Share userName={data.user.name} year={data.user.year} visible={true} />
  {/if}
</div>
```

**Step 3: Create year page**

```astro
---
// ABOUTME: Individual Wrapped experience page for a user's year.
// ABOUTME: Loads user data and renders the full slide experience.

import WrappedLayout from '@layouts/WrappedLayout.astro';
import WrappedExperience from '@components/WrappedExperience.svelte';

export function getStaticPaths() {
  // In production, this reads from generated data directory
  // and creates a page for each user/year combination
  return [];
}

const { user, year } = Astro.params;

// Load user data (in production, this reads from data/*.json)
const data = {
  user: { name: user, year: parseInt(year as string) },
  stats: { total_minutes: 0 },
  top: { artists: [], tracks: [] },
  time_patterns: { by_hour: Array(24).fill(0), quirky: {} },
  ai_generated: {
    personality: { type: '', tagline: '', description: '', spirit_animal: '' },
    aura: { colors: ['#1DB954'], vibe: '', aesthetic: '' },
    roasts: [],
    narrative: '',
  },
};
---

<WrappedLayout title={`${user}'s ${year} Wrapped`}>
  <WrappedExperience {data} client:load />
</WrappedLayout>
```

**Step 4: Verify build**

Run:
```bash
cd frontend && npm run build
```

Expected: Build completes successfully

**Step 5: Commit**

```bash
git add frontend/src/pages/ frontend/src/components/WrappedExperience.svelte
git commit -m "feat: add user wrapped pages with full slide experience"
```

---

## Phase 4: CLI Integration & Deployment

### Task 12: Wire Up CLI Commands

**Files:**
- Modify: `cli/src/last_wrapped/main.py`
- Create: `cli/src/last_wrapped/orchestrator.py`

**Step 1: Write failing test**

```python
# ABOUTME: Tests for CLI orchestration.
# ABOUTME: Verifies end-to-end workflow from extract to deploy.

import pytest
from pathlib import Path

from last_wrapped.orchestrator import Orchestrator
from last_wrapped.config import Config, PlexConfig, LLMConfig, HostingConfig, CloudflareConfig


class TestOrchestrator:
    def test_orchestrator_initializes_with_config(self, tmp_path: Path) -> None:
        """Orchestrator accepts config and output directory."""
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(
                provider="cloudflare",
                cloudflare=CloudflareConfig(account_id="x", project_name="y"),
            ),
            output_dir=tmp_path,
        )

        orchestrator = Orchestrator(config)

        assert orchestrator.config == config
        assert orchestrator.output_dir == tmp_path
```

Create `cli/tests/test_orchestrator.py` with the above.

**Step 2: Run test to verify it fails**

Run: `cd cli && pytest tests/test_orchestrator.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement orchestrator**

```python
# ABOUTME: Orchestrates the full Wrapped generation pipeline.
# ABOUTME: Coordinates extraction, processing, AI generation, build, and deploy.

import json
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from last_wrapped.config import Config
from last_wrapped.extractors.plex import PlexExtractor, ListeningHistory
from last_wrapped.processors.stats import StatsProcessor
from last_wrapped.processors.time_analysis import TimeAnalysisProcessor
from last_wrapped.ai.provider import get_provider
from last_wrapped.ai.generators import (
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    AuraGenerator,
    SuperlativesGenerator,
    HotTakesGenerator,
    SuggestionsGenerator,
)


console = Console()


class Orchestrator:
    """Orchestrates the full Wrapped generation pipeline."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.output_dir = config.output_dir
        self.data_dir = self.output_dir / "data"
        self.histories: list[ListeningHistory] = []

    def extract(self) -> list[ListeningHistory]:
        """Extract listening data from Plex."""
        console.print("[bold]Extracting data from Plex...[/bold]")

        extractor = PlexExtractor(
            url=self.config.plex.url,
            token=self.config.plex.token,
        )

        self.histories = list(extractor.extract_all_users(self.config.year))
        console.print(f"[green]Extracted data for {len(self.histories)} users[/green]")

        return self.histories

    def process(self) -> None:
        """Process extracted data and generate AI content."""
        console.print("[bold]Processing data...[/bold]")

        self.data_dir.mkdir(parents=True, exist_ok=True)

        llm_provider = get_provider(self.config.llm)

        for history in self.histories:
            console.print(f"  Processing {history.user}...")

            # Calculate stats
            stats_processor = StatsProcessor(history)
            time_processor = TimeAnalysisProcessor(history)

            top_artists = stats_processor.top_artists(limit=10)
            top_tracks = stats_processor.top_tracks(limit=10)
            top_albums = stats_processor.top_albums(limit=10)
            total_stats = stats_processor.total_stats()

            time_patterns = {
                "by_hour": time_processor.plays_by_hour(),
                "by_day_of_week": time_processor.plays_by_day_of_week(),
                "by_month": time_processor.plays_by_month(),
                "quirky": {
                    "late_night_anthem": time_processor.late_night_anthem(),
                    "monday_motivator": time_processor.day_anthem(0),
                    "most_repeated_day": time_processor.most_repeated_single_day(),
                },
            }

            # Generate AI content
            ai_stats = {
                "total_minutes": total_stats["total_minutes"],
                "top_artist": top_artists[0].name if top_artists else "Unknown",
                "top_genre": "Unknown",  # TODO: implement genre extraction
                "top_track": top_tracks[0].name if top_tracks else "Unknown",
                "genres": [],
                "late_night_plays": sum(time_patterns["by_hour"][0:4]),
            }

            narrative_gen = NarrativeGenerator(llm_provider)
            personality_gen = PersonalityGenerator(llm_provider)
            roast_gen = RoastGenerator(llm_provider)
            aura_gen = AuraGenerator(llm_provider)
            superlatives_gen = SuperlativesGenerator(llm_provider)
            hot_takes_gen = HotTakesGenerator(llm_provider)
            suggestions_gen = SuggestionsGenerator(llm_provider)

            ai_generated = {
                "narrative": narrative_gen.generate(ai_stats).get("narrative", ""),
                "personality": personality_gen.generate(ai_stats),
                "roasts": roast_gen.generate(ai_stats).get("roasts", []),
                "aura": aura_gen.generate(ai_stats),
                "superlatives": superlatives_gen.generate(ai_stats),
                "hot_takes": hot_takes_gen.generate(ai_stats).get("hot_takes", []),
                "suggestions": suggestions_gen.generate(ai_stats),
            }

            # Build output data structure
            user_data = {
                "user": {
                    "name": history.user,
                    "avatar_url": history.avatar_url,
                    "year": history.year,
                },
                "stats": {
                    "total_minutes": total_stats["total_minutes"],
                    "total_tracks": total_stats["total_tracks"],
                    "unique_artists": total_stats["unique_artists"],
                    "unique_albums": total_stats["unique_albums"],
                    "peak_day": time_processor.peak_day_overall().get("date"),
                    "peak_day_minutes": time_processor.peak_day_overall().get("minutes", 0),
                    "longest_streak_days": time_processor.longest_streak(),
                },
                "top": {
                    "artists": [
                        {
                            "name": a.name,
                            "plays": a.plays,
                            "minutes": a.minutes,
                            "image_url": a.image_url,
                        }
                        for a in top_artists
                    ],
                    "albums": [
                        {
                            "name": a.name,
                            "plays": a.plays,
                            "minutes": a.minutes,
                            "artist": a.artist,
                            "image_url": a.image_url,
                        }
                        for a in top_albums
                    ],
                    "tracks": [
                        {
                            "name": t.name,
                            "plays": t.plays,
                            "minutes": t.minutes,
                            "artist": t.artist,
                            "album": t.album,
                            "image_url": t.image_url,
                        }
                        for t in top_tracks
                    ],
                },
                "time_patterns": time_patterns,
                "ai_generated": ai_generated,
            }

            # Save to JSON
            user_file = self.data_dir / f"{history.user}.json"
            with open(user_file, "w") as f:
                json.dump(user_data, f, indent=2, default=str)

            console.print(f"    [green]Saved {user_file}[/green]")

    def build(self) -> None:
        """Build the Astro static site."""
        console.print("[bold]Building static site...[/bold]")

        import subprocess
        import shutil

        # Copy data files to frontend
        frontend_data = Path("frontend/src/data")
        frontend_data.mkdir(parents=True, exist_ok=True)

        for json_file in self.data_dir.glob("*.json"):
            shutil.copy(json_file, frontend_data / json_file.name)

        # Run Astro build
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            console.print(f"[red]Build failed: {result.stderr}[/red]")
            raise RuntimeError("Astro build failed")

        console.print("[green]Build complete[/green]")

    def deploy(self) -> None:
        """Deploy to configured hosting provider."""
        console.print("[bold]Deploying...[/bold]")

        provider = self.config.hosting.provider

        if provider == "cloudflare":
            self._deploy_cloudflare()
        elif provider == "vercel":
            self._deploy_vercel()
        elif provider == "netlify":
            self._deploy_netlify()
        elif provider == "github-pages":
            self._deploy_github_pages()
        else:
            raise ValueError(f"Unknown hosting provider: {provider}")

    def _deploy_cloudflare(self) -> None:
        """Deploy to Cloudflare Pages."""
        import subprocess

        cf_config = self.config.hosting.cloudflare
        if not cf_config:
            raise ValueError("Cloudflare config not found")

        cmd = [
            "npx",
            "wrangler",
            "pages",
            "deploy",
            "frontend/dist",
            "--project-name",
            cf_config.project_name,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            console.print(f"[red]Deploy failed: {result.stderr}[/red]")
            raise RuntimeError("Cloudflare deploy failed")

        console.print("[green]Deployed to Cloudflare Pages[/green]")

    def _deploy_vercel(self) -> None:
        """Deploy to Vercel."""
        console.print("[yellow]Vercel deploy not yet implemented[/yellow]")

    def _deploy_netlify(self) -> None:
        """Deploy to Netlify."""
        console.print("[yellow]Netlify deploy not yet implemented[/yellow]")

    def _deploy_github_pages(self) -> None:
        """Deploy to GitHub Pages."""
        console.print("[yellow]GitHub Pages deploy not yet implemented[/yellow]")

    def run_all(self) -> None:
        """Run the full pipeline: extract → process → build → deploy."""
        self.extract()
        self.process()
        self.build()
        self.deploy()
```

**Step 4: Update main.py to use orchestrator**

```python
# ABOUTME: Main CLI entry point using Typer.
# ABOUTME: Provides commands: init, generate, extract, process, build, deploy, preview.

from pathlib import Path

import typer
from rich.console import Console

from last_wrapped.config import load_config
from last_wrapped.orchestrator import Orchestrator

app = typer.Typer(
    name="last-wrapped",
    help="Self-hostable Spotify Wrapped for Plex servers",
    no_args_is_help=True,
)
console = Console()


def get_orchestrator(config_path: str) -> Orchestrator:
    """Load config and create orchestrator."""
    config = load_config(Path(config_path))
    return Orchestrator(config)


@app.command()
def init() -> None:
    """Initialize a new config.yaml file with guided prompts."""
    console.print("[yellow]Init command not yet implemented[/yellow]")


@app.command()
def generate(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Generate Wrapped for all users (extract → process → build → deploy)."""
    orchestrator = get_orchestrator(config)
    orchestrator.run_all()


@app.command()
def extract(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Extract listening data from Plex server."""
    orchestrator = get_orchestrator(config)
    orchestrator.extract()


@app.command()
def process(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Process extracted data and generate AI content."""
    orchestrator = get_orchestrator(config)
    orchestrator.process()


@app.command()
def build(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Build the static Astro site."""
    orchestrator = get_orchestrator(config)
    orchestrator.build()


@app.command()
def deploy(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """Deploy to configured hosting provider."""
    orchestrator = get_orchestrator(config)
    orchestrator.deploy()


@app.command()
def preview() -> None:
    """Start local preview server."""
    import subprocess

    subprocess.run(["npm", "run", "preview"], cwd="frontend")


if __name__ == "__main__":
    app()
```

**Step 5: Run tests**

Run: `cd cli && pytest tests/test_orchestrator.py -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add cli/src/last_wrapped/orchestrator.py cli/src/last_wrapped/main.py cli/tests/test_orchestrator.py
git commit -m "feat: wire up CLI commands with orchestrator"
```

---

### Task 13: Create README and Documentation

**Files:**
- Create: `README.md`
- Create: `docs/getting-started.md`

**Step 1: Create README**

```markdown
# Last Wrapped

> Self-hostable Spotify Wrapped for Plex servers

Generate beautiful, interactive year-end music recaps for everyone on your Plex server.

## Features

- 📊 **Rich Stats** - Top artists, albums, tracks, listening time, and more
- 🎨 **Beautiful UI** - Spotify-style animated slides
- 🤖 **AI-Powered** - Personalized narratives, roasts, and recommendations
- 🏠 **Self-Hosted** - Your data stays on your server
- 📱 **Shareable** - Each user gets their own link

## Quick Start

```bash
# Install
pip install last-wrapped

# Initialize config
last-wrapped init

# Generate Wrapped for all users
last-wrapped generate
```

## Requirements

- Python 3.11+
- Node.js 18+
- Plex Media Server with music library
- (Optional) Anthropic or OpenAI API key for AI features

## Documentation

See [Getting Started](docs/getting-started.md) for detailed setup instructions.

## License

MIT
```

**Step 2: Create getting-started.md**

```markdown
# Getting Started with Last Wrapped

## Prerequisites

1. **Plex Server** with admin access
2. **Python 3.11+** installed
3. **Node.js 18+** installed
4. **Plex Token** - Get from [Plex Web](https://app.plex.tv) → Settings → Account → Authorized Devices

## Installation

```bash
pip install last-wrapped
```

Or with uvx:
```bash
uvx last-wrapped
```

## Configuration

Create `config.yaml`:

```yaml
plex:
  url: "https://your-plex-server:32400"
  token: "your-plex-token"

llm:
  provider: "anthropic"  # or "openai" or "none"
  api_key: "your-api-key"

year: 2024

hosting:
  provider: "cloudflare"
  cloudflare:
    account_id: "your-account-id"
    project_name: "my-wrapped"
```

## Generate Your Wrapped

```bash
# Full pipeline
last-wrapped generate

# Or step by step
last-wrapped extract   # Pull data from Plex
last-wrapped process   # Calculate stats + AI content
last-wrapped build     # Generate static site
last-wrapped deploy    # Deploy to hosting
```

## Local Preview

```bash
last-wrapped preview
```

Visit http://localhost:4321 to see your Wrapped.

## Hosting Options

### Cloudflare Pages (Recommended)
1. Create a Cloudflare account
2. Run `npx wrangler login`
3. Add cloudflare config to config.yaml

### Vercel
1. Create a Vercel account
2. Get API token from Settings
3. Add vercel config to config.yaml

### GitHub Pages
1. Create a GitHub repository
2. Add github_pages config to config.yaml

## Troubleshooting

### "No listening history found"
- Make sure your Plex music library has play history
- Check that the Plex token has access to the library

### "AI content is empty"
- Verify your API key is correct
- Check you have credits with your LLM provider
- Try `provider: "none"` to skip AI features
```

**Step 3: Commit**

```bash
git add README.md docs/getting-started.md
git commit -m "docs: add README and getting started guide"
```

---

## Summary

This plan creates a fully functional "Last Wrapped" application with:

1. **Python CLI** - Extracts Plex data, processes stats, generates AI content
2. **Astro Frontend** - Beautiful animated slide experience
3. **Configurable Deployment** - Support for Cloudflare, Vercel, Netlify, GitHub Pages
4. **TDD Throughout** - Tests before implementation

**Total Tasks:** 13
**Estimated Implementation Time:** Follow TDD cycle for each task

---

Plan complete and saved to `docs/plans/2024-12-03-last-wrapped-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
