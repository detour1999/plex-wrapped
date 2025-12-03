# ABOUTME: Interactive TUI setup wizard for Last Wrapped configuration using Textual.
# ABOUTME: Multi-screen wizard with validation for Plex, LLM, and hosting configuration.

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import anthropic
import openai
import yaml
from plexapi.server import PlexServer
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet, Static

from last_wrapped.extractors.plex import PlexExtractor


class WelcomeScreen(Screen):
    """Welcome screen with project description."""

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2 4;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    #description {
        text-align: center;
        padding: 1 0;
    }

    #get-started {
        width: 100%;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Create welcome screen layout."""
        yield Header()
        yield Container(
            Static("Last Wrapped", id="title"),
            Static("Self-hostable Spotify Wrapped for Plex servers", id="subtitle"),
            Static(
                "\nCreate beautiful year-end wrapped experiences for your Plex users.\n"
                "This wizard will guide you through:\n\n"
                "• Connecting to your Plex server\n"
                "• Configuring AI-powered insights\n"
                "• Setting up deployment hosting\n"
                "• Saving your configuration",
                id="description",
            ),
            Button("Get Started", variant="primary", id="get-started"),
            id="welcome-container",
        )
        yield Footer()

    @on(Button.Pressed, "#get-started")
    def go_to_plex(self) -> None:
        """Navigate to Plex configuration screen."""
        self.app.push_screen(PlexScreen())


class PlexScreen(Screen):
    """Plex server configuration screen."""

    CSS = """
    PlexScreen {
        align: center middle;
    }

    #plex-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2 4;
    }

    .screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
    }

    .input-field {
        width: 100%;
        margin-bottom: 1;
    }

    #status {
        margin-top: 1;
        min-height: 3;
    }

    .button-row {
        margin-top: 2;
        width: 100%;
        height: auto;
    }

    .button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create Plex configuration layout."""
        yield Header()
        yield Container(
            Static("Step 1/4: Plex Configuration", classes="screen-title"),
            Label("Plex Server URL", classes="field-label"),
            Input(
                placeholder="https://plex.example.com",
                id="plex-url",
                classes="input-field",
            ),
            Label("Plex Token", classes="field-label"),
            Input(placeholder="Your Plex token", password=True, id="plex-token", classes="input-field"),
            Static("", id="status"),
            Horizontal(
                Button("Back", variant="default", id="back"),
                Button("Test Connection", variant="primary", id="test"),
                Button("Next", variant="success", id="next", disabled=True),
                classes="button-row",
            ),
            id="plex-container",
        )
        yield Footer()

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        """Return to welcome screen."""
        self.app.pop_screen()

    @on(Button.Pressed, "#test")
    def test_connection(self) -> None:
        """Test Plex connection."""
        url_input = self.query_one("#plex-url", Input)
        token_input = self.query_one("#plex-token", Input)

        url = url_input.value.strip()
        token = token_input.value.strip()

        if not url or not token:
            self.show_status("Please enter both URL and token", "error")
            return

        self.test_plex_connection(url, token)

    @work(exclusive=True)
    async def test_plex_connection(self, url: str, token: str) -> None:
        """Test Plex connection in background worker."""
        status = self.query_one("#status", Static)
        next_button = self.query_one("#next", Button)

        status.update("[yellow]Testing connection...[/yellow]")
        next_button.disabled = True

        try:
            extractor = PlexExtractor(url, token)
            extractor.connect()
            users = extractor.get_users()

            app = self.app
            if isinstance(app, SetupApp):
                app.config_data["plex"] = {"url": url, "token": token}

            status.update(
                f"[green]✓ Connection successful![/green]\n"
                f"Found {len(users)} user(s): {', '.join(users)}"
            )
            next_button.disabled = False

        except Exception as e:
            status.update(f"[red]✗ Connection failed:[/red]\n{str(e)}")
            next_button.disabled = True

    @on(Button.Pressed, "#next")
    def go_to_llm(self) -> None:
        """Navigate to LLM configuration screen."""
        self.app.push_screen(LLMScreen())


class LLMScreen(Screen):
    """LLM provider configuration screen."""

    CSS = """
    LLMScreen {
        align: center middle;
    }

    #llm-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2 4;
    }

    .screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
    }

    #provider-set {
        margin: 1 0;
    }

    .input-field {
        width: 100%;
        margin-bottom: 1;
    }

    #status {
        margin-top: 1;
        min-height: 3;
    }

    .button-row {
        margin-top: 2;
        width: 100%;
        height: auto;
    }

    .button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create LLM configuration layout."""
        yield Header()
        yield Container(
            Static("Step 2/4: LLM Configuration", classes="screen-title"),
            Static("LLM providers generate AI-powered insights and summaries.", classes="field-label"),
            Label("Choose Provider", classes="field-label"),
            RadioSet(
                RadioButton("Anthropic (Claude)", id="anthropic", value=True),
                RadioButton("OpenAI (GPT)", id="openai"),
                id="provider-set",
            ),
            Label("API Key", classes="field-label"),
            Input(placeholder="Your API key", password=True, id="api-key", classes="input-field"),
            Static("", id="status"),
            Horizontal(
                Button("Back", variant="default", id="back"),
                Button("Validate", variant="primary", id="validate"),
                Button("Next", variant="success", id="next", disabled=True),
                classes="button-row",
            ),
            id="llm-container",
        )
        yield Footer()

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        """Return to Plex screen."""
        self.app.pop_screen()

    @on(Button.Pressed, "#validate")
    def validate_api_key(self) -> None:
        """Validate LLM API key."""
        provider_set = self.query_one("#provider-set", RadioSet)
        api_key_input = self.query_one("#api-key", Input)

        api_key = api_key_input.value.strip()
        provider = "anthropic" if provider_set.pressed_button.id == "anthropic" else "openai"

        if not api_key:
            self.show_status("Please enter an API key", "error")
            return

        self.test_llm_key(provider, api_key)

    @work(exclusive=True)
    async def test_llm_key(self, provider: str, api_key: str) -> None:
        """Test LLM API key in background worker."""
        status = self.query_one("#status", Static)
        next_button = self.query_one("#next", Button)

        status.update("[yellow]Validating API key...[/yellow]")
        next_button.disabled = True

        try:
            if provider == "anthropic":
                client = anthropic.Anthropic(api_key=api_key)
                # Test with a minimal request
                client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
            else:
                client = openai.OpenAI(api_key=api_key)
                # Test with a minimal request
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )

            app = self.app
            if isinstance(app, SetupApp):
                app.config_data["llm"] = {
                    "provider": provider,
                    "api_key": api_key
                }

            status.update(f"[green]✓ API key validated successfully![/green]\n{provider.capitalize()} is ready.")
            next_button.disabled = False

        except Exception as e:
            status.update(f"[red]✗ Validation failed:[/red]\n{str(e)}")
            next_button.disabled = True

    def show_status(self, message: str, status_type: str) -> None:
        """Update status message."""
        status = self.query_one("#status", Static)
        if status_type == "error":
            status.update(f"[red]{message}[/red]")
        else:
            status.update(f"[yellow]{message}[/yellow]")

    @on(Button.Pressed, "#next")
    def go_to_hosting(self) -> None:
        """Navigate to hosting configuration screen."""
        self.app.push_screen(HostingScreen())


class HostingScreen(Screen):
    """Hosting provider configuration screen."""

    CSS = """
    HostingScreen {
        align: center middle;
    }

    #hosting-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2 4;
    }

    .screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
    }

    #provider-set {
        margin: 1 0;
    }

    #dynamic-fields {
        margin: 1 0;
        min-height: 10;
    }

    .input-field {
        width: 100%;
        margin-bottom: 1;
    }

    .button-row {
        margin-top: 2;
        width: 100%;
        height: auto;
    }

    .button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create hosting configuration layout."""
        yield Header()
        yield Container(
            Static("Step 3/4: Hosting Configuration", classes="screen-title"),
            Label("Choose Hosting Provider", classes="field-label"),
            RadioSet(
                RadioButton("Cloudflare Pages", id="cloudflare", value=True),
                RadioButton("Vercel", id="vercel"),
                RadioButton("Netlify", id="netlify"),
                RadioButton("GitHub Pages", id="github"),
                id="provider-set",
            ),
            Container(id="dynamic-fields"),
            Horizontal(
                Button("Back", variant="default", id="back"),
                Button("Next", variant="success", id="next"),
                classes="button-row",
            ),
            id="hosting-container",
        )
        yield Footer()

        # Initialize with default provider fields
        self.update_fields("cloudflare")

    @on(RadioSet.Changed, "#provider-set")
    def on_provider_changed(self, event: RadioSet.Changed) -> None:
        """Update fields when provider changes."""
        if event.pressed.id:
            self.update_fields(event.pressed.id)

    def update_fields(self, provider: str) -> None:
        """Update dynamic fields based on selected provider."""
        container = self.query_one("#dynamic-fields", Container)
        container.remove_children()

        if provider == "cloudflare":
            container.mount(
                Label("Account ID", classes="field-label"),
                Input(placeholder="Your Cloudflare account ID", id="account-id", classes="input-field"),
                Label("Project Name", classes="field-label"),
                Input(placeholder="Your project name", id="project-name", classes="input-field"),
            )
        elif provider == "vercel":
            container.mount(
                Label("Token", classes="field-label"),
                Input(placeholder="Your Vercel token", password=True, id="token", classes="input-field"),
                Label("Project Name", classes="field-label"),
                Input(placeholder="Your project name", id="project-name", classes="input-field"),
            )
        elif provider == "netlify":
            container.mount(
                Label("Token", classes="field-label"),
                Input(placeholder="Your Netlify token", password=True, id="token", classes="input-field"),
                Label("Site ID", classes="field-label"),
                Input(placeholder="Your site ID", id="site-id", classes="input-field"),
            )
        elif provider == "github":
            container.mount(
                Label("Repository", classes="field-label"),
                Input(placeholder="username/repo", id="repo", classes="input-field"),
                Label("Branch", classes="field-label"),
                Input(placeholder="gh-pages", value="gh-pages", id="branch", classes="input-field"),
            )

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        """Return to LLM screen."""
        self.app.pop_screen()

    @on(Button.Pressed, "#next")
    def go_to_summary(self) -> None:
        """Navigate to summary screen."""
        provider_set = self.query_one("#provider-set", RadioSet)
        provider = provider_set.pressed_button.id if provider_set.pressed_button else "cloudflare"

        # Collect provider-specific config
        config: Dict[str, Any] = {}

        if provider == "cloudflare":
            account_id = self.query_one("#account-id", Input).value.strip()
            project_name = self.query_one("#project-name", Input).value.strip()
            config = {
                "account_id": account_id,
                "project_name": project_name,
            }
        elif provider == "vercel":
            token = self.query_one("#token", Input).value.strip()
            project_name = self.query_one("#project-name", Input).value.strip()
            config = {
                "token": token,
                "project_name": project_name,
            }
        elif provider == "netlify":
            token = self.query_one("#token", Input).value.strip()
            site_id = self.query_one("#site-id", Input).value.strip()
            config = {
                "auth_token": token,
                "site_id": site_id,
            }
        elif provider == "github":
            repo = self.query_one("#repo", Input).value.strip()
            branch = self.query_one("#branch", Input).value.strip() or "gh-pages"
            config = {
                "repo": repo,
                "branch": branch,
            }

        app = self.app
        if isinstance(app, SetupApp):
            app.config_data["hosting"] = {
                "provider": provider,
                provider: config
            }

        self.app.push_screen(SummaryScreen())


class SummaryScreen(Screen):
    """Configuration summary and save screen."""

    CSS = """
    SummaryScreen {
        align: center middle;
    }

    #summary-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2 4;
    }

    .screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    #config-summary {
        margin: 1 0;
        padding: 1;
        background: $panel;
        border: solid $primary;
        min-height: 15;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
    }

    .input-field {
        width: 100%;
        margin-bottom: 1;
    }

    #status {
        margin-top: 1;
        min-height: 3;
    }

    .button-row {
        margin-top: 2;
        width: 100%;
        height: auto;
    }

    .button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create summary screen layout."""
        yield Header()
        yield Container(
            Static("Step 4/4: Review and Save", classes="screen-title"),
            Static(self.build_summary(), id="config-summary"),
            Label("Year", classes="field-label"),
            Input(value=str(datetime.now().year), id="year", classes="input-field"),
            Label("Output Directory", classes="field-label"),
            Input(value="dist", id="output-dir", classes="input-field"),
            Static("", id="status"),
            Horizontal(
                Button("Back", variant="default", id="back"),
                Button("Save Config", variant="success", id="save"),
                classes="button-row",
            ),
            id="summary-container",
        )
        yield Footer()

    def build_summary(self) -> str:
        """Build configuration summary text."""
        app = self.app
        if not isinstance(app, SetupApp):
            return "No configuration data available"

        config = app.config_data
        lines = ["[bold]Configuration Summary[/bold]\n"]

        # Plex
        if "plex" in config:
            plex = config["plex"]
            lines.append(f"[cyan]Plex Server:[/cyan] {plex.get('url', 'Not set')}")
            lines.append(f"[cyan]Token:[/cyan] {'*' * 8}...{plex.get('token', '')[-4:]}\n")

        # LLM
        if "llm" in config:
            llm = config["llm"]
            provider = llm.get('provider', 'Not set')
            lines.append(f"[cyan]LLM Provider:[/cyan] {provider.capitalize()}")
            api_key = llm.get('api_key', '')
            if api_key:
                lines.append(f"[cyan]API Key:[/cyan] {'*' * 8}...{api_key[-4:]}\n")

        # Hosting
        if "hosting" in config:
            hosting = config["hosting"]
            provider = hosting.get('provider', 'Not set')
            lines.append(f"[cyan]Hosting:[/cyan] {provider.capitalize()}")

            provider_config = hosting.get(provider, {})
            for key, value in provider_config.items():
                if "token" in key.lower() or "key" in key.lower():
                    display_value = f"{'*' * 8}...{value[-4:]}" if value else "Not set"
                else:
                    display_value = value or "Not set"
                lines.append(f"  {key}: {display_value}")

        return "\n".join(lines)

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        """Return to hosting screen."""
        self.app.pop_screen()

    @on(Button.Pressed, "#save")
    def save_config(self) -> None:
        """Save configuration to file."""
        app = self.app
        if not isinstance(app, SetupApp):
            return

        year_input = self.query_one("#year", Input)
        output_dir_input = self.query_one("#output-dir", Input)

        try:
            year = int(year_input.value.strip())
        except ValueError:
            self.show_status("Invalid year value", "error")
            return

        output_dir = output_dir_input.value.strip() or "dist"

        # Add year and output_dir to config
        app.config_data["year"] = year
        app.config_data["output_dir"] = output_dir

        # Save to config.yaml
        config_path = Path("config.yaml")

        try:
            with open(config_path, "w") as f:
                yaml.dump(app.config_data, f, default_flow_style=False, sort_keys=False)

            status = self.query_one("#status", Static)
            status.update(
                f"[green]✓ Configuration saved to {config_path}![/green]\n\n"
                "Next steps:\n"
                "1. Run: last-wrapped extract\n"
                "2. Run: last-wrapped process\n"
                "3. Run: last-wrapped build\n"
                "4. Run: last-wrapped deploy\n\n"
                "Or run everything at once: last-wrapped generate"
            )

            # Disable save button after successful save
            save_button = self.query_one("#save", Button)
            save_button.disabled = True

        except Exception as e:
            self.show_status(f"Failed to save config: {str(e)}", "error")

    def show_status(self, message: str, status_type: str) -> None:
        """Update status message."""
        status = self.query_one("#status", Static)
        if status_type == "error":
            status.update(f"[red]{message}[/red]")
        else:
            status.update(f"[green]{message}[/green]")


class SetupApp(App):
    """Main setup wizard application."""

    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        """Initialize setup app."""
        super().__init__()
        self.config_data: Dict[str, Any] = {}

    def on_mount(self) -> None:
        """Show welcome screen on mount."""
        self.push_screen(WelcomeScreen())
