# ABOUTME: Main CLI entry point for last-wrapped using Typer.
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
    """Initialize a new Last Wrapped project configuration."""
    console.print("[yellow]init command not yet implemented[/yellow]")


@app.command()
def generate(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Generate a complete Wrapped experience from start to finish."""
    console.print("[yellow]generate command not yet implemented[/yellow]")


@app.command()
def extract(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Extract listening history from Plex server."""
    console.print("[yellow]extract command not yet implemented[/yellow]")


@app.command()
def process(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Process extracted data and generate insights."""
    console.print("[yellow]process command not yet implemented[/yellow]")


@app.command()
def build(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Build the frontend application with processed data."""
    console.print("[yellow]build command not yet implemented[/yellow]")


@app.command()
def deploy(
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file")
) -> None:
    """Deploy the built application to hosting."""
    console.print("[yellow]deploy command not yet implemented[/yellow]")


@app.command()
def preview() -> None:
    """Preview the Wrapped experience locally."""
    console.print("[yellow]preview command not yet implemented[/yellow]")


if __name__ == "__main__":
    app()
