# ABOUTME: Main CLI entry point for last-wrapped using Typer.
# ABOUTME: Provides commands: init, generate, extract, process, build, deploy, preview.

import subprocess
import sys
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
    """Initialize a new Last Wrapped project configuration."""
    console.print("[yellow]init command not yet implemented[/yellow]")


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
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        console.print(
            "[red]Frontend directory not found. Make sure you're in the project root.[/red]"
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
