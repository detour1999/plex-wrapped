# ABOUTME: Orchestrates the complete Last Wrapped workflow from extraction to deployment.
# ABOUTME: Coordinates Plex extraction, stats processing, AI generation, and hosting deployment.

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from last_wrapped.ai.generators import (
    AuraGenerator,
    HotTakesGenerator,
    NarrativeGenerator,
    PersonalityGenerator,
    RoastGenerator,
    SuggestionsGenerator,
    SuperlativesGenerator,
)
from last_wrapped.ai.provider import get_provider
from last_wrapped.config import Config
from last_wrapped.extractors.plex import PlexExtractor
from last_wrapped.processors.stats import StatsProcessor
from last_wrapped.processors.time_analysis import TimeAnalysisProcessor

console = Console()


class Orchestrator:
    """Orchestrates the complete Last Wrapped workflow."""

    def __init__(self, config: Config) -> None:
        """Initialize orchestrator with configuration.

        Args:
            config: Validated configuration object
        """
        self.config = config
        self.output_dir = config.output_dir

    def extract(self) -> None:
        """Extract listening history from Plex server."""
        console.print("[bold blue]Extracting listening history from Plex...[/bold blue]")

        extractor = PlexExtractor(url=self.config.plex.url, token=self.config.plex.token)
        extractor.connect()

        start_date = datetime(self.config.year, 1, 1)
        end_date = datetime(self.config.year, 12, 31, 23, 59, 59)

        histories = extractor.extract_all_users(
            year=self.config.year,
            start_date=start_date,
            end_date=end_date,
        )

        # Save extracted data
        data_dir = self.output_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        for history in histories:
            user_file = data_dir / f"{history.user}_raw.json"
            with open(user_file, "w") as f:
                json.dump(history.model_dump(mode="json"), f, indent=2, default=str)

        console.print(
            f"[green]Extracted data for {len(histories)} users to {data_dir}[/green]"
        )

    def process(self) -> None:
        """Process extracted data and generate insights."""
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
        for raw_file in raw_files:
            username = raw_file.stem.replace("_raw", "")
            console.print(f"Processing user: {username}")

            # Load raw history
            with open(raw_file) as f:
                history_data = json.load(f)

            from last_wrapped.extractors.plex import ListeningHistory

            history = ListeningHistory(**history_data)

            # Generate stats
            stats_processor = StatsProcessor(history)
            time_processor = TimeAnalysisProcessor(history)

            stats = {
                "total": stats_processor.total_stats(),
                "top_artists": [
                    {
                        "name": item.name,
                        "plays": item.plays,
                        "minutes": item.minutes,
                        "image_url": item.image_url,
                    }
                    for item in stats_processor.top_artists(10)
                ],
                "top_tracks": [
                    {
                        "name": item.name,
                        "artist": item.artist,
                        "album": item.album,
                        "plays": item.plays,
                        "minutes": item.minutes,
                        "image_url": item.image_url,
                    }
                    for item in stats_processor.top_tracks(10)
                ],
                "top_albums": [
                    {
                        "name": item.name,
                        "artist": item.artist,
                        "plays": item.plays,
                        "minutes": item.minutes,
                        "image_url": item.image_url,
                    }
                    for item in stats_processor.top_albums(10)
                ],
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

                generators = [
                    ("narrative", NarrativeGenerator(provider)),
                    ("personality", PersonalityGenerator(provider)),
                    ("roast", RoastGenerator(provider)),
                    ("aura", AuraGenerator(provider)),
                    ("superlatives", SuperlativesGenerator(provider)),
                    ("hot_takes", HotTakesGenerator(provider)),
                    ("suggestions", SuggestionsGenerator(provider)),
                ]

                ai_content = {}
                for name, generator in generators:
                    try:
                        result = generator.generate(stats)
                        ai_content[name] = result
                    except Exception as e:
                        console.print(f"  [yellow]Warning: Failed to generate {name}: {e}[/yellow]")
                        ai_content[name] = {}

                stats["ai_content"] = ai_content

            # Save processed data
            processed_file = data_dir / f"{username}_processed.json"
            with open(processed_file, "w") as f:
                json.dump(stats, f, indent=2, default=str)

            console.print(f"  [green]Saved processed data to {processed_file}[/green]")

    def build(self) -> None:
        """Build the frontend application with processed data."""
        console.print("[bold blue]Building frontend application...[/bold blue]")

        # Check for frontend directory
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            raise RuntimeError(
                f"Frontend directory not found: {frontend_dir}. Make sure you're in the project root."
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

    def deploy(self) -> None:
        """Deploy the built application to hosting provider."""
        console.print("[bold blue]Deploying to hosting provider...[/bold blue]")

        provider = self.config.hosting.provider

        if provider == "none":
            console.print("[yellow]No hosting provider configured. Skipping deployment.[/yellow]")
            return

        frontend_dir = Path("frontend")
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

        if config.api_token:
            cmd.extend(["--api-token", config.api_token])

        try:
            subprocess.run(cmd, check=True)
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
            "[bold magenta]Running complete Last Wrapped workflow...[/bold magenta]"
        )

        try:
            self.extract()
            self.process()
            self.build()
            self.deploy()

            console.print(
                "[bold green]Complete! Your Last Wrapped is live![/bold green]"
            )
        except Exception as e:
            console.print(f"[bold red]Workflow failed: {e}[/bold red]")
            raise
