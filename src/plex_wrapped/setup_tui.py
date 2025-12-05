# ABOUTME: Interactive TUI setup wizard for Plex Wrapped configuration using Textual.
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
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet, RichLog, Static

from plex_wrapped.extractors.plex import PlexExtractor


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
            Static("Plex Wrapped", id="title"),
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
            Static(
                "[dim]Your Plex server URL is the address you use to access Plex.\n"
                "Usually: http://YOUR-SERVER-IP:32400 or https://your-domain.com:32400[/]",
                classes="help-text",
            ),
            Label("Plex Server URL", classes="field-label"),
            Input(
                placeholder="http://192.168.1.100:32400",
                id="plex-url",
                classes="input-field",
            ),
            Static(
                "[dim]To get your Plex token:\n"
                "1. Go to app.plex.tv and sign in\n"
                "2. Open browser DevTools (F12) → Network tab\n"
                "3. Click any request, find 'X-Plex-Token' in the URL[/]",
                classes="help-text",
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

    def on_mount(self) -> None:
        """Pre-fill values from existing config."""
        app = self.app
        if isinstance(app, SetupApp) and "plex" in app.config_data:
            plex = app.config_data["plex"]
            if "url" in plex:
                self.query_one("#plex-url", Input).value = plex["url"]
            if "token" in plex:
                self.query_one("#plex-token", Input).value = plex["token"]

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
            Static(
                "[dim]AI generates personalized insights, roasts, and narratives.\n"
                "Choose your preferred LLM provider below.[/]",
                classes="help-text",
            ),
            Label("Choose Provider", classes="field-label"),
            RadioSet(
                RadioButton("Anthropic (Claude)", id="anthropic", value=True),
                RadioButton("OpenAI (GPT)", id="openai"),
                id="provider-set",
            ),
            Static(
                "[dim]To get your Anthropic API key:\n"
                "1. Go to console.anthropic.com/settings/keys\n"
                "2. Create an account if needed\n"
                "3. Click 'Create Key' and copy it[/]",
                id="api-key-help",
                classes="help-text",
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

    def on_mount(self) -> None:
        """Pre-fill values from existing config."""
        app = self.app
        if isinstance(app, SetupApp) and "llm" in app.config_data:
            llm = app.config_data["llm"]
            if "api_key" in llm:
                self.query_one("#api-key", Input).value = llm["api_key"]
            if "provider" in llm:
                provider = llm["provider"]
                provider_set = self.query_one("#provider-set", RadioSet)
                for button in provider_set.query(RadioButton):
                    if button.id == provider:
                        button.value = True
                        break

    @on(RadioSet.Changed, "#provider-set")
    def on_provider_changed(self, event: RadioSet.Changed) -> None:
        """Update help text when provider changes."""
        help_widget = self.query_one("#api-key-help", Static)
        if event.pressed.id == "anthropic":
            help_widget.update(
                "[dim]To get your Anthropic API key:\n"
                "1. Go to console.anthropic.com/settings/keys\n"
                "2. Create an account if needed\n"
                "3. Click 'Create Key' and copy it[/]"
            )
        else:
            help_widget.update(
                "[dim]To get your OpenAI API key:\n"
                "1. Go to platform.openai.com/api-keys\n"
                "2. Create an account if needed\n"
                "3. Click 'Create new secret key' and copy it[/]"
            )

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

    _current_provider: str = "cloudflare"

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
            Static(
                "[dim]Choose where to deploy your wrapped experience.\n"
                "All providers offer free tiers suitable for static sites.[/]",
                classes="help-text",
            ),
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

    def on_mount(self) -> None:
        """Initialize provider fields and pre-fill from config."""
        app = self.app
        provider = "cloudflare"

        if isinstance(app, SetupApp) and "hosting" in app.config_data:
            hosting = app.config_data["hosting"]
            provider = hosting.get("provider", "cloudflare")

        # Track current provider and create fields
        self._current_provider = provider
        self.update_fields(provider)

        # Select the correct provider radio button (after fields exist)
        if provider != "cloudflare":
            provider_set = self.query_one("#provider-set", RadioSet)
            for button in provider_set.query(RadioButton):
                if button.id == provider:
                    button.value = True
                    break

        # Pre-fill provider-specific fields from config
        self._prefill_hosting_fields(provider)

    def _prefill_hosting_fields(self, provider: str) -> None:
        """Pre-fill hosting fields from config data."""
        app = self.app
        if not isinstance(app, SetupApp) or "hosting" not in app.config_data:
            return

        hosting = app.config_data["hosting"]
        provider_config = hosting.get(provider, {})

        if provider == "cloudflare":
            if "account_id" in provider_config:
                self.query_one("#account-id", Input).value = provider_config["account_id"]
            if "project_name" in provider_config:
                self.query_one("#project-name", Input).value = provider_config["project_name"]
            if "api_token" in provider_config:
                self.query_one("#api-token", Input).value = provider_config["api_token"]
        elif provider == "vercel":
            if "token" in provider_config:
                self.query_one("#token", Input).value = provider_config["token"]
            if "project_name" in provider_config:
                self.query_one("#project-name", Input).value = provider_config["project_name"]
        elif provider == "netlify":
            if "auth_token" in provider_config:
                self.query_one("#token", Input).value = provider_config["auth_token"]
            if "site_id" in provider_config:
                self.query_one("#site-id", Input).value = provider_config["site_id"]
        elif provider == "github":
            if "repo" in provider_config:
                self.query_one("#repo", Input).value = provider_config["repo"]
            if "branch" in provider_config:
                self.query_one("#branch", Input).value = provider_config["branch"]

    @on(RadioSet.Changed, "#provider-set")
    def on_provider_changed(self, event: RadioSet.Changed) -> None:
        """Update fields when provider changes."""
        if event.pressed.id and event.pressed.id != self._current_provider:
            self._current_provider = event.pressed.id
            self.update_fields(event.pressed.id)

    def update_fields(self, provider: str) -> None:
        """Update dynamic fields based on selected provider."""
        container = self.query_one("#dynamic-fields", Container)
        container.remove_children()

        if provider == "cloudflare":
            container.mount(
                Static(
                    "[dim]Find your Account ID at:\n"
                    "dash.cloudflare.com → Right sidebar → Account ID\n\n"
                    "Create an API Token at:\n"
                    "dash.cloudflare.com/profile/api-tokens → Create Token\n"
                    "Use template: Edit Cloudflare Pages[/]",
                    classes="help-text",
                ),
                Label("Account ID", classes="field-label"),
                Input(placeholder="Your Cloudflare account ID", id="account-id", classes="input-field"),
                Label("Project Name", classes="field-label"),
                Input(placeholder="Your project name", id="project-name", classes="input-field"),
                Label("API Token", classes="field-label"),
                Input(placeholder="Your Cloudflare API token", password=True, id="api-token", classes="input-field"),
            )
        elif provider == "vercel":
            container.mount(
                Static(
                    "[dim]Create a token at:\n"
                    "vercel.com/account/tokens → Create Token[/]",
                    classes="help-text",
                ),
                Label("Token", classes="field-label"),
                Input(placeholder="Your Vercel token", password=True, id="token", classes="input-field"),
                Label("Project Name", classes="field-label"),
                Input(placeholder="Your project name", id="project-name", classes="input-field"),
            )
        elif provider == "netlify":
            container.mount(
                Static(
                    "[dim]Get credentials at:\n"
                    "• Token: app.netlify.com/user/applications (Personal access tokens)\n"
                    "• Site ID: Site settings → General → Site details[/]",
                    classes="help-text",
                ),
                Label("Token", classes="field-label"),
                Input(placeholder="Your Netlify token", password=True, id="token", classes="input-field"),
                Label("Site ID", classes="field-label"),
                Input(placeholder="Your site ID", id="site-id", classes="input-field"),
            )
        elif provider == "github":
            container.mount(
                Static(
                    "[dim]GitHub Pages deploys from a repository branch.\n"
                    "Enter your repo in 'username/repo' format.\n"
                    "The gh-pages branch is commonly used for static sites.[/]",
                    classes="help-text",
                ),
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
            api_token = self.query_one("#api-token", Input).value.strip()
            config = {
                "account_id": account_id,
                "project_name": project_name,
                "api_token": api_token,
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
                Button("Save Config", variant="primary", id="save"),
                Button("Generate", variant="success", id="generate", disabled=True),
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
                "Click 'Generate' to run the full pipeline,\n"
                "or use CLI commands:\n"
                "  plex-wrapped extract && plex-wrapped process && plex-wrapped build"
            )

            # Disable save button and enable generate button after successful save
            save_button = self.query_one("#save", Button)
            save_button.disabled = True

            generate_button = self.query_one("#generate", Button)
            generate_button.disabled = False

        except Exception as e:
            self.show_status(f"Failed to save config: {str(e)}", "error")

    def show_status(self, message: str, status_type: str) -> None:
        """Update status message."""
        status = self.query_one("#status", Static)
        if status_type == "error":
            status.update(f"[red]{message}[/red]")
        else:
            status.update(f"[green]{message}[/green]")

    @on(Button.Pressed, "#generate")
    def go_to_processing(self) -> None:
        """Navigate to processing screen to run the pipeline."""
        self.app.push_screen(ProcessingScreen())


class ProcessingScreen(Screen):
    """Processing screen that runs extract, process, and build stages."""

    CSS = """
    ProcessingScreen {
        align: center middle;
    }

    #processing-container {
        width: 90;
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

    .stage-row {
        margin: 1 0;
        height: 3;
    }

    .stage-indicator {
        width: 20;
    }

    .stage-status {
        width: 10;
    }

    #log-output {
        margin: 1 0;
        padding: 1;
        background: $panel;
        border: solid $primary;
        height: 15;
        overflow-y: auto;
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
        """Create processing screen layout."""
        yield Header()
        yield Container(
            Static("Generate Wrapped", classes="screen-title"),
            Static(
                "[dim]Run the full generation pipeline:\n"
                "Extract → Process → Build → Deploy[/]",
                classes="help-text",
            ),
            Horizontal(
                Static("Extract Data", id="stage-extract", classes="stage-indicator"),
                Static("[dim]Pending[/dim]", id="status-extract", classes="stage-status"),
                classes="stage-row",
            ),
            Horizontal(
                Static("Process Stats", id="stage-process", classes="stage-indicator"),
                Static("[dim]Pending[/dim]", id="status-process", classes="stage-status"),
                classes="stage-row",
            ),
            Horizontal(
                Static("Build Site", id="stage-build", classes="stage-indicator"),
                Static("[dim]Pending[/dim]", id="status-build", classes="stage-status"),
                classes="stage-row",
            ),
            Horizontal(
                Static("Deploy", id="stage-deploy", classes="stage-indicator"),
                Static("[dim]Pending[/dim]", id="status-deploy", classes="stage-status"),
                classes="stage-row",
            ),
            RichLog(id="log-output", wrap=True, markup=True),
            Horizontal(
                Button("Edit Config", variant="default", id="edit-config"),
                Button("Start Generation", variant="success", id="start-generation"),
                classes="button-row",
            ),
            id="processing-container",
        )
        yield Footer()

    @on(Button.Pressed, "#edit-config")
    def go_to_setup(self) -> None:
        """Navigate to setup wizard to edit config."""
        self.app.push_screen(PlexScreen())

    @on(Button.Pressed, "#start-generation")
    def start_generation(self) -> None:
        """Start the generation pipeline."""
        self.run_pipeline()

    def _thread_log(self, message: str) -> None:
        """Log a message from a worker thread."""
        self.app.call_from_thread(self._log, message)

    @work(exclusive=True, thread=True)
    def run_pipeline(self) -> None:
        """Run the full generation pipeline in background thread."""
        import time

        self.app.call_from_thread(self._update_ui_start)

        app = self.app
        if not isinstance(app, SetupApp):
            return

        config_data = app.config_data

        try:
            from plex_wrapped.config import Config
            from plex_wrapped.orchestrator import Orchestrator

            self._thread_log("[dim]Initializing configuration...[/dim]")
            config = Config(
                plex=config_data.get("plex", {}),
                llm=config_data.get("llm", {}),
                hosting=config_data.get("hosting", {}),
                year=config_data.get("year", 2024),
                output_dir=config_data.get("output_dir", "dist"),
                project_root=app.project_root,
            )
            self._thread_log(f"[dim]Project root: {app.project_root}[/dim]")
            self._thread_log(f"[dim]Output directory: {config.output_dir}[/dim]")
            orchestrator = Orchestrator(config)

            # Extract
            self.app.call_from_thread(self._update_ui_stage, "extract", "running", "")
            self._thread_log("[yellow]Extracting data from Plex...[/yellow]")
            self._thread_log(f"  Connecting to {config.plex.url}")
            start_time = time.time()
            orchestrator.extract(on_progress=self._thread_log)
            elapsed = time.time() - start_time
            self._thread_log(f"[green]✓ Extraction complete ({elapsed:.1f}s)[/green]")
            self.app.call_from_thread(self._update_ui_stage, "extract", "done", "")

            # Process
            self.app.call_from_thread(self._update_ui_stage, "process", "running", "")
            self._thread_log("[yellow]Processing stats and generating insights...[/yellow]")
            start_time = time.time()
            orchestrator.process(on_progress=self._thread_log)
            elapsed = time.time() - start_time
            self._thread_log(f"[green]✓ Processing complete ({elapsed:.1f}s)[/green]")
            self.app.call_from_thread(self._update_ui_stage, "process", "done", "")

            # Build
            self.app.call_from_thread(self._update_ui_stage, "build", "running", "")
            self._thread_log("[yellow]Building frontend...[/yellow]")
            self._thread_log(f"  Building in {app.project_root / 'frontend'}")
            start_time = time.time()
            orchestrator.build()
            elapsed = time.time() - start_time
            self._thread_log(f"[green]✓ Build complete ({elapsed:.1f}s)[/green]")
            self.app.call_from_thread(self._update_ui_stage, "build", "done", "")

            # Deploy
            provider = config.hosting.provider
            if provider != "none":
                self.app.call_from_thread(self._update_ui_stage, "deploy", "running", "")
                self._thread_log(f"[yellow]Deploying to {provider}...[/yellow]")
                start_time = time.time()
                orchestrator.deploy()
                elapsed = time.time() - start_time
                self._thread_log(f"[green]✓ Deployment complete ({elapsed:.1f}s)[/green]")
                self.app.call_from_thread(self._update_ui_stage, "deploy", "done", "")
            else:
                self._thread_log("[dim]Skipping deployment (no hosting provider configured)[/dim]")
                self.app.call_from_thread(self._update_ui_stage, "deploy", "skipped", "")

            self._thread_log("")
            self._thread_log("[bold green]All done![/bold green]")
            self._thread_log("")
            if provider != "none":
                self._thread_log("Your wrapped experience has been deployed!")
            else:
                self._thread_log("Your wrapped experience is ready!")
                self._thread_log("Run [cyan]plex-wrapped preview[/cyan] to view locally.")
            self.app.call_from_thread(self._update_ui_complete, "")

        except Exception as e:
            self._thread_log(f"[red]Error: {e}[/red]")
            self.app.call_from_thread(self._update_ui_error, str(e))

    def _log(self, message: str) -> None:
        """Append a message to the log output."""
        log_output = self.query_one("#log-output", RichLog)
        log_output.write(message)

    def _update_ui_start(self) -> None:
        """Update UI when pipeline starts."""
        start_button = self.query_one("#start-generation", Button)
        start_button.disabled = True
        start_button.label = "Running..."
        log_output = self.query_one("#log-output", RichLog)
        log_output.clear()
        self._log("[yellow]Starting generation pipeline...[/yellow]")

    def _update_ui_stage(self, stage: str, status: str, message: str) -> None:
        """Update UI for a pipeline stage."""
        self.update_stage_status(stage, status)
        if message:
            if status == "running":
                self._log(f"[yellow]{message}[/yellow]")
            else:
                self._log(f"[green]{message}[/green]")

    def _update_ui_complete(self, message: str) -> None:
        """Update UI when pipeline completes."""
        if message:
            self._log(message)
        start_button = self.query_one("#start-generation", Button)
        start_button.label = "Done!"

    def _update_ui_error(self, error: str) -> None:
        """Update UI when pipeline fails."""
        start_button = self.query_one("#start-generation", Button)
        start_button.disabled = False
        start_button.label = "Retry"

    def update_stage_status(self, stage: str, status: str) -> None:
        """Update the status indicator for a stage."""
        status_widget = self.query_one(f"#status-{stage}", Static)
        if status == "running":
            status_widget.update("[yellow]Running...[/yellow]")
        elif status == "done":
            status_widget.update("[green]✓ Done[/green]")
        elif status == "error":
            status_widget.update("[red]✗ Error[/red]")
        elif status == "skipped":
            status_widget.update("[dim]⊘ Skipped[/dim]")


class SetupApp(App):
    """Main setup wizard application."""

    CSS = """
    Screen {
        background: $background;
    }

    .help-text {
        margin: 1 0;
        padding: 0 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize setup app.

        Args:
            project_root: Root directory of the project containing frontend/.
                          Defaults to auto-detected from current working directory.
        """
        super().__init__()
        self.project_root = project_root or self._detect_project_root()
        self.config_data: Dict[str, Any] = {}
        self._load_existing_config()

    def _detect_project_root(self) -> Path:
        """Detect project root by looking for frontend/ directory.

        Searches current directory and up to 3 parent directories.
        """
        cwd = Path.cwd()
        candidates = [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]

        for candidate in candidates:
            if (candidate / "frontend").is_dir():
                return candidate

        # Fall back to current directory
        return cwd

    def _load_existing_config(self) -> None:
        """Load existing config.yaml if present."""
        config_path = Path("config.yaml")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    self.config_data = yaml.safe_load(f) or {}
            except Exception:
                self.config_data = {}

    def _is_config_complete(self) -> bool:
        """Check if config has all required sections."""
        required = ["plex", "llm", "hosting"]
        return all(key in self.config_data for key in required)

    def on_mount(self) -> None:
        """Show appropriate screen based on config state."""
        if self._is_config_complete():
            self.push_screen(ProcessingScreen())
        else:
            self.push_screen(WelcomeScreen())
