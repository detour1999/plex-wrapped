# ABOUTME: Orchestrates the complete Plex Wrapped workflow from extraction to deployment.
# ABOUTME: Coordinates Plex extraction, stats processing, AI generation, and hosting deployment.

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# Type alias for progress callbacks: (message: str) -> None
ProgressCallback = Callable[[str], None]

from rich.console import Console

import httpx

from plex_wrapped.utils import slugify
from plex_wrapped.ai.generators import (
    AuraGenerator,
    HotTakesGenerator,
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    SuggestionsGenerator,
    SuperlativesGenerator,
    ThemeGenerator,
)
from plex_wrapped.ai.provider import get_provider
from plex_wrapped.config import Config
from plex_wrapped.extractors.plex import PlexExtractor
from plex_wrapped.processors.stats import StatsProcessor
from plex_wrapped.processors.time_analysis import TimeAnalysisProcessor

console = Console()


class Orchestrator:
    """Orchestrates the complete Plex Wrapped workflow."""

    def __init__(self, config: Config) -> None:
        """Initialize orchestrator with configuration.

        Args:
            config: Validated configuration object
        """
        self.config = config
        self.output_dir = config.output_dir
        self.project_root = config.project_root

    def extract(self, on_progress: Optional[ProgressCallback] = None) -> None:
        """Extract listening history from Plex server.

        Args:
            on_progress: Optional callback for progress updates
        """
        console.print("[bold blue]Extracting listening history from Plex...[/bold blue]")

        extractor = PlexExtractor(url=self.config.plex.url, token=self.config.plex.token)
        extractor.connect()

        start_date = datetime(self.config.year, 1, 1)
        end_date = datetime(self.config.year, 12, 31, 23, 59, 59)

        histories = extractor.extract_all_users(
            year=self.config.year,
            start_date=start_date,
            end_date=end_date,
            on_progress=on_progress,
        )

        # Save extracted data and download images
        data_dir = self.output_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        for i, history in enumerate(histories):
            # Download images while we have the live Plex connection
            msg = f"Downloading images for {history.user} ({i + 1}/{len(histories)})..."
            console.print(f"  {msg}")
            if on_progress:
                on_progress(msg)
            self._download_images_for_user(history, extractor, on_progress)

            user_file = data_dir / f"{history.user}_{self.config.year}_raw.json"
            with open(user_file, "w") as f:
                json.dump(history.model_dump(mode="json"), f, indent=2, default=str)

        console.print(
            f"[green]Extracted data for {len(histories)} users to {data_dir}[/green]"
        )

    def _download_images_for_user(
        self,
        history,
        extractor: PlexExtractor,
        on_progress: Optional[ProgressCallback] = None,
    ) -> None:
        """Download images only for top artists, tracks, and albums.

        Image Matching Algorithm:
        -------------------------
        1. Historical track data contains thumb URLs, but these become stale over time
           as Plex regenerates thumbnails or library metadata changes.

        2. To get current valid URLs, we search the live Plex library for each item:
           - Artists: Direct search by artist name (title=name)
           - Albums: Search by album title, then match parentTitle to artist name
           - Tracks: Use album art - search for album, match artist, use album.thumb

        3. All image URLs include the Plex auth token as a query parameter:
           {plex_url}{thumb_path}?X-Plex-Token={token}

        4. Images are deduplicated by URL to avoid downloading the same image twice
           (e.g., multiple tracks from the same album share one image).

        5. Downloaded images are saved as:
           {output_dir}/images/{username}/{type}-{slugified-name}-{url-hash}.{ext}
           Example: artist-radiohead-a1b2c3d4.jpg

        6. The url-hash (first 8 chars of MD5) ensures uniqueness even when names collide.

        Args:
            history: ListeningHistory object with tracks
            extractor: PlexExtractor with active connection
            on_progress: Optional callback for progress updates
        """
        import hashlib

        images_dir = self.output_dir / "images" / history.user
        images_dir.mkdir(parents=True, exist_ok=True)

        # Calculate top items to know which images we need
        stats_processor = StatsProcessor(history)
        top_artists = stats_processor.top_artists(10)
        top_tracks = stats_processor.top_tracks(10)
        top_albums = stats_processor.top_albums(10)

        # Get the music library for lookups
        music_libraries = [
            section for section in extractor._server.library.sections() if section.type == "artist"
        ]
        if not music_libraries:
            console.print("    [yellow]No music library found, skipping images[/yellow]")
            return
        music_library = music_libraries[0]

        # Collect images to download by looking up items in current library
        images_to_download: list[tuple[str, str, str]] = []  # (url, filename, item_key)

        # Look up top artists
        for item in top_artists:
            try:
                results = music_library.searchArtists(title=item.name, maxresults=1)
                if results and results[0].thumb:
                    url = f"{extractor.url}{results[0].thumb}?X-Plex-Token={extractor.token}"
                    filename = f"artist-{slugify(item.name)}"
                    images_to_download.append((url, filename, f"artist:{item.name}"))
            except Exception:
                pass

        # Look up top albums
        for item in top_albums:
            try:
                results = music_library.searchAlbums(title=item.name, maxresults=5)
                # Find album matching artist
                for album in results:
                    if album.parentTitle == item.artist and album.thumb:
                        url = f"{extractor.url}{album.thumb}?X-Plex-Token={extractor.token}"
                        filename = f"album-{slugify(item.artist or '')}-{slugify(item.name)}"
                        images_to_download.append((url, filename, f"album:{item.artist}:{item.name}"))
                        break
            except Exception:
                pass

        # Look up top tracks (use album art)
        for item in top_tracks:
            try:
                results = music_library.searchAlbums(title=item.album, maxresults=5)
                for album in results:
                    if album.parentTitle == item.artist and album.thumb:
                        url = f"{extractor.url}{album.thumb}?X-Plex-Token={extractor.token}"
                        filename = f"track-{slugify(item.artist or '')}-{slugify(item.name)}"
                        images_to_download.append((url, filename, f"track:{item.artist}:{item.name}"))
                        break
            except Exception:
                pass

        # Dedupe by URL
        seen_urls: set[str] = set()
        unique_images: list[tuple[str, str, str]] = []
        for url, filename, key in images_to_download:
            if url not in seen_urls:
                seen_urls.add(url)
                unique_images.append((url, filename, key))

        console.print(f"    [dim]Found {len(unique_images)} unique images to download[/dim]")

        # Track item key to local path for updating tracks later
        key_to_local: dict[str, str] = {}
        downloaded = 0
        failed = 0

        # Download each unique image
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            for url, name, key in unique_images:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{name}-{url_hash}.jpg"
                filepath = images_dir / filename
                local_path = f"/images/{history.user}/{filename}"

                # Skip if already downloaded
                if filepath.exists():
                    key_to_local[key] = local_path
                    continue

                # Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
                max_retries = 3
                retry_delay = 1.0
                success = False

                for attempt in range(max_retries):
                    try:
                        response = client.get(url)
                        response.raise_for_status()

                        # Adjust extension based on content type
                        content_type = response.headers.get("content-type", "image/jpeg")
                        if "png" in content_type:
                            filepath = filepath.with_suffix(".png")
                            local_path = local_path.replace(".jpg", ".png")
                        elif "webp" in content_type:
                            filepath = filepath.with_suffix(".webp")
                            local_path = local_path.replace(".jpg", ".webp")

                        filepath.write_bytes(response.content)
                        key_to_local[key] = local_path
                        downloaded += 1
                        success = True
                        break
                    except httpx.HTTPError:
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        continue
                    except Exception:
                        # Non-HTTP errors (filesystem, etc.) don't retry
                        break

                if not success:
                    failed += 1

        # Update track thumb_urls to local paths for matching top tracks
        # Create lookup for artist:album to local path
        album_to_local: dict[tuple[str, str], str] = {}
        for key, local_path in key_to_local.items():
            if key.startswith("album:") or key.startswith("track:"):
                parts = key.split(":", 2)
                if len(parts) >= 3:
                    artist = parts[1]
                    # For tracks, we stored track name but need album name
                    # Just use artist matching for now
                    for item in top_albums:
                        if item.artist == artist:
                            album_to_local[(artist, item.name)] = local_path

        for track in history.tracks:
            key = (track.artist, track.album)
            if key in album_to_local:
                track.thumb_url = album_to_local[key]

        console.print(f"    [green]Downloaded {downloaded} images[/green]", end="")
        if failed > 0:
            console.print(f" [yellow]({failed} failed)[/yellow]")
        else:
            console.print()

    def _build_image_mapping(self, username: str) -> dict[str, str]:
        """Build a mapping from slugified names to local image paths.

        Args:
            username: Username to get images for

        Returns:
            Dict mapping type:slugname to local path (e.g., "artist:nofx" -> "/images/milo/artist-nofx-xxx.jpg")
        """
        images_dir = self.output_dir / "images" / username
        if not images_dir.exists():
            return {}

        mapping: dict[str, str] = {}
        for img_file in images_dir.iterdir():
            if not img_file.is_file():
                continue
            name = img_file.stem
            local_path = f"/images/{username}/{img_file.name}"

            # Parse filename format: type-name-hash or type-artist-name-hash
            parts = name.rsplit("-", 1)  # Remove hash
            if len(parts) < 2:
                continue
            name_part = parts[0]

            if name_part.startswith("artist-"):
                artist_slug = name_part[7:]  # Remove "artist-"
                mapping[f"artist:{artist_slug}"] = local_path
            elif name_part.startswith("album-"):
                # Format: album-{artist}-{album}
                rest = name_part[6:]  # Remove "album-"
                mapping[f"album:{rest}"] = local_path
            elif name_part.startswith("track-"):
                # Format: track-{artist}-{track}
                rest = name_part[6:]  # Remove "track-"
                mapping[f"track:{rest}"] = local_path

        return mapping

    def process(self, on_progress: Optional[ProgressCallback] = None) -> None:
        """Process extracted data and generate insights.

        Args:
            on_progress: Optional callback for progress updates
        """
        console.print("[bold blue]Processing extracted data...[/bold blue]")

        data_dir = self.output_dir / "data"
        if not data_dir.exists():
            raise RuntimeError(
                f"Data directory not found: {data_dir}. Run extract first."
            )

        # Find all raw data files
        raw_files = list(data_dir.glob("*_raw.json"))
        if not raw_files:
            raise RuntimeError(f"No raw data files found in {data_dir}")

        # Get LLM provider
        provider = get_provider(self.config.llm)

        # Process each user's data
        for file_idx, raw_file in enumerate(raw_files):
            # Extract username and year from filename: {username}_{year}_raw.json
            stem = raw_file.stem  # e.g., "detour1999_2024_raw"
            if stem.endswith("_raw"):
                stem = stem[:-4]  # Remove "_raw" suffix

            # Extract username (everything before last underscore which should be year)
            parts = stem.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                username = parts[0]
                file_year = parts[1]
            else:
                # Fallback for old format files without year
                username = stem
                file_year = str(self.config.year)

            msg = f"Processing user {file_idx + 1}/{len(raw_files)}: {username} ({file_year})"
            console.print(msg)
            if on_progress:
                on_progress(msg)

            # Load raw history
            with open(raw_file) as f:
                history_data = json.load(f)

            from plex_wrapped.extractors.plex import ListeningHistory

            history = ListeningHistory(**history_data)

            # Build image mapping from downloaded images
            image_mapping = self._build_image_mapping(username)

            # Generate stats
            stats_processor = StatsProcessor(history)
            time_processor = TimeAnalysisProcessor(history)

            # Build stats with local image URLs where available
            top_artists = []
            for item in stats_processor.top_artists(10):
                artist_key = f"artist:{slugify(item.name)}"
                image_url = image_mapping.get(artist_key, item.image_url)
                top_artists.append({
                    "name": item.name,
                    "plays": item.plays,
                    "minutes": item.minutes,
                    "image_url": image_url,
                })

            top_tracks = []
            for item in stats_processor.top_tracks(10):
                track_key = f"track:{slugify(item.artist or '')}-{slugify(item.name)}"
                album_key = f"album:{slugify(item.artist or '')}-{slugify(item.album or '')}"
                image_url = image_mapping.get(track_key) or image_mapping.get(album_key) or item.image_url
                top_tracks.append({
                    "name": item.name,
                    "artist": item.artist,
                    "album": item.album,
                    "plays": item.plays,
                    "minutes": item.minutes,
                    "image_url": image_url,
                })

            top_albums = []
            for item in stats_processor.top_albums(10):
                album_key = f"album:{slugify(item.artist or '')}-{slugify(item.name)}"
                image_url = image_mapping.get(album_key, item.image_url)
                top_albums.append({
                    "name": item.name,
                    "artist": item.artist,
                    "plays": item.plays,
                    "minutes": item.minutes,
                    "image_url": image_url,
                })

            stats = {
                "user": username,
                "year": self.config.year,
                "total": stats_processor.total_stats(),
                "top_artists": top_artists,
                "top_tracks": top_tracks,
                "top_albums": top_albums,
                "time_analysis": {
                    "plays_by_hour": time_processor.plays_by_hour(),
                    "plays_by_day_of_week": time_processor.plays_by_day_of_week(),
                    "plays_by_month": time_processor.plays_by_month(),
                    "peak_listening_hour": time_processor.peak_listening_hour(),
                    "peak_listening_day": time_processor.peak_listening_day(),
                    "peak_day_overall": time_processor.peak_day_overall(),
                    "longest_streak": time_processor.longest_streak(),
                    "late_night_anthem": time_processor.late_night_anthem(),
                    "most_repeated_single_day": time_processor.most_repeated_single_day(),
                },
            }

            # Generate AI content if provider is not "none"
            if self.config.llm.provider != "none":
                console.print(f"  Generating AI insights for {username}...")
                if on_progress:
                    on_progress(f"  Generating AI insights for {username}...")

                generators = [
                    ("narrative", NarrativeGenerator(provider)),
                    ("personality", PersonalityGenerator(provider)),
                    ("roast", RoastGenerator(provider)),
                    ("aura", AuraGenerator(provider)),
                    ("superlatives", SuperlativesGenerator(provider)),
                    ("hot_takes", HotTakesGenerator(provider)),
                    ("suggestions", SuggestionsGenerator(provider)),
                    ("theme", ThemeGenerator(provider)),
                ]

                ai_content = {}
                for gen_idx, (name, generator) in enumerate(generators):
                    if on_progress:
                        on_progress(f"    Generating {name} ({gen_idx + 1}/{len(generators)})...")
                    try:
                        result = generator.generate(stats)
                        ai_content[name] = result
                    except Exception as e:
                        console.print(f"  [yellow]Warning: Failed to generate {name}: {e}[/yellow]")
                        if on_progress:
                            on_progress(f"    Warning: Failed to generate {name}: {e}")
                        ai_content[name] = {}

                stats["ai_content"] = ai_content

            # Save processed data
            processed_file = data_dir / f"{username}_{file_year}_processed.json"
            with open(processed_file, "w") as f:
                json.dump(stats, f, indent=2, default=str)

            console.print(f"  [green]Saved processed data to {processed_file}[/green]")

    def build(self) -> None:
        """Build the frontend application with processed data."""
        console.print("[bold blue]Building frontend application...[/bold blue]")

        # Check for frontend directory
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            raise RuntimeError(
                f"Frontend directory not found: {frontend_dir}. "
                f"Set project_root in config to the directory containing frontend/."
            )

        # Run npm build
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            console.print("[green]Frontend build completed successfully[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Build failed:[/red]\n{e.stderr}")
            raise RuntimeError(f"Frontend build failed: {e.stderr}") from e

        # Copy images from output directory to frontend dist
        images_src = self.output_dir / "images"
        images_dst = frontend_dir / "dist" / "images"
        if images_src.exists():
            import shutil

            if images_dst.exists():
                shutil.rmtree(images_dst)
            shutil.copytree(images_src, images_dst)
            console.print(f"[green]Copied images to {images_dst}[/green]")

    def deploy(self) -> None:
        """Deploy the built application to hosting provider."""
        console.print("[bold blue]Deploying to hosting provider...[/bold blue]")

        provider = self.config.hosting.provider

        if provider == "none":
            console.print("[yellow]No hosting provider configured. Skipping deployment.[/yellow]")
            return

        frontend_dir = self.project_root / "frontend"
        dist_dir = frontend_dir / "dist"

        if not dist_dir.exists():
            raise RuntimeError(
                f"Build directory not found: {dist_dir}. Run build first."
            )

        if provider == "cloudflare":
            self._deploy_cloudflare(dist_dir)
        elif provider == "vercel":
            self._deploy_vercel(dist_dir)
        elif provider == "netlify":
            self._deploy_netlify(dist_dir)
        elif provider == "github":
            self._deploy_github(dist_dir)
        else:
            raise ValueError(f"Unsupported hosting provider: {provider}")

    def _deploy_cloudflare(self, dist_dir: Path) -> None:
        """Deploy to Cloudflare Pages."""
        if not self.config.hosting.cloudflare:
            raise RuntimeError("Cloudflare config is missing")

        config = self.config.hosting.cloudflare

        cmd = [
            "npx",
            "wrangler",
            "pages",
            "deploy",
            str(dist_dir),
            "--project-name",
            config.project_name,
        ]

        # Set up environment with API token if provided
        env = None
        if config.api_token:
            import os
            env = os.environ.copy()
            env["CLOUDFLARE_API_TOKEN"] = config.api_token

        try:
            subprocess.run(cmd, check=True, env=env)
            console.print("[green]Deployed to Cloudflare Pages successfully[/green]")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Cloudflare deployment failed: {e}") from e

    def _deploy_vercel(self, dist_dir: Path) -> None:
        """Deploy to Vercel."""
        if not self.config.hosting.vercel:
            raise RuntimeError("Vercel config is missing")

        config = self.config.hosting.vercel

        cmd = ["npx", "vercel", "deploy", str(dist_dir), "--prod"]

        if config.token:
            cmd.extend(["--token", config.token])

        try:
            subprocess.run(cmd, check=True)
            console.print("[green]Deployed to Vercel successfully[/green]")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Vercel deployment failed: {e}") from e

    def _deploy_netlify(self, dist_dir: Path) -> None:
        """Deploy to Netlify."""
        if not self.config.hosting.netlify:
            raise RuntimeError("Netlify config is missing")

        config = self.config.hosting.netlify

        cmd = [
            "npx",
            "netlify",
            "deploy",
            "--prod",
            "--dir",
            str(dist_dir),
            "--site",
            config.site_id,
        ]

        if config.auth_token:
            cmd.extend(["--auth", config.auth_token])

        try:
            subprocess.run(cmd, check=True)
            console.print("[green]Deployed to Netlify successfully[/green]")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Netlify deployment failed: {e}") from e

    def _deploy_github(self, dist_dir: Path) -> None:
        """Deploy to GitHub Pages."""
        if not self.config.hosting.github:
            raise RuntimeError("GitHub Pages config is missing")

        config = self.config.hosting.github

        cmd = [
            "npx",
            "gh-pages",
            "--dist",
            str(dist_dir),
            "--repo",
            f"https://github.com/{config.repo}.git",
            "--branch",
            config.branch,
        ]

        try:
            subprocess.run(cmd, check=True)
            console.print("[green]Deployed to GitHub Pages successfully[/green]")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GitHub Pages deployment failed: {e}") from e

    def run_all(self) -> None:
        """Run the complete workflow: extract, process, build, and deploy."""
        console.print(
            "[bold magenta]Running complete Plex Wrapped workflow...[/bold magenta]"
        )

        try:
            self.extract()
            self.process()
            self.build()
            self.deploy()

            console.print(
                "[bold green]Complete! Your Plex Wrapped is live![/bold green]"
            )
        except Exception as e:
            console.print(f"[bold red]Workflow failed: {e}[/bold red]")
            raise
