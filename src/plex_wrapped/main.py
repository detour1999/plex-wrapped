# ABOUTME: Main CLI entry point for plex-wrapped using Typer.
# ABOUTME: Provides commands: init, generate, extract, process, build, deploy, preview.

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from plex_wrapped.config import load_config
from plex_wrapped.orchestrator import Orchestrator

app = typer.Typer(
    name="plex-wrapped",
    help="Self-hostable Spotify Wrapped for Plex servers",
    invoke_without_command=True,
)
console = Console()


def detect_frontend_directory() -> Optional[Path]:
    """Detect frontend directory by searching current and parent directories.

    Searches current directory and up to 3 parent directories for frontend/.

    Returns:
        Path to frontend directory if found, None otherwise
    """
    cwd = Path.cwd()
    candidates = [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]

    for candidate in candidates:
        frontend_dir = candidate / "frontend"
        if frontend_dir.is_dir():
            return frontend_dir

    return None


@app.callback()
def main(ctx: typer.Context) -> None:
    """Launch the TUI setup wizard when no command is given."""
    if ctx.invoked_subcommand is None:
        from plex_wrapped.setup_tui import SetupApp

        setup = SetupApp()
        setup.run()


def get_orchestrator(config_path: str) -> Orchestrator:
    """Load config and create orchestrator instance.

    Args:
        config_path: Path to configuration file

    Returns:
        Orchestrator instance

    Raises:
        SystemExit: If config loading fails
    """
    try:
        config = load_config(Path(config_path))
        return Orchestrator(config)
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")
        sys.exit(1)


@app.command()
def init() -> None:
    """Initialize Plex Wrapped with an interactive setup wizard."""
    from plex_wrapped.setup_tui import SetupApp

    setup = SetupApp()
    setup.run()


@app.command()
def generate(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Generate a complete Wrapped experience from start to finish."""
    orchestrator = get_orchestrator(config)
    try:
        orchestrator.run_all()
    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        sys.exit(1)


@app.command()
def extract(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Extract listening history from Plex server."""
    orchestrator = get_orchestrator(config)
    try:
        orchestrator.extract()
    except Exception as e:
        console.print(f"[red]Extraction failed: {e}[/red]")
        sys.exit(1)


@app.command()
def process(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Process extracted data and generate insights."""
    orchestrator = get_orchestrator(config)
    try:
        orchestrator.process()
    except Exception as e:
        console.print(f"[red]Processing failed: {e}[/red]")
        sys.exit(1)


@app.command()
def build(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Build the frontend application with processed data."""
    orchestrator = get_orchestrator(config)
    try:
        orchestrator.build()
    except Exception as e:
        console.print(f"[red]Build failed: {e}[/red]")
        sys.exit(1)


@app.command()
def deploy(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Deploy the built application to hosting."""
    orchestrator = get_orchestrator(config)
    try:
        orchestrator.deploy()
    except Exception as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        sys.exit(1)


@app.command()
def preview() -> None:
    """Preview the Wrapped experience locally."""
    frontend_dir = detect_frontend_directory()
    if frontend_dir is None:
        console.print(
            "[red]Frontend directory not found. Make sure you're in the project root or a subdirectory.[/red]"
        )
        sys.exit(1)

    console.print("[bold blue]Starting preview server...[/bold blue]")
    try:
        subprocess.run(["npm", "run", "preview"], cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Preview failed: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Preview server stopped[/yellow]")


if __name__ == "__main__":
    app()
