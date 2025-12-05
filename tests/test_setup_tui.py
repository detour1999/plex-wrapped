# ABOUTME: Tests for the TUI setup wizard and processing screen.
# ABOUTME: Uses Textual's pilot API for async UI testing.

import pytest

from plex_wrapped.setup_tui import HostingScreen, ProcessingScreen, SetupApp, SummaryScreen


class TestProcessingScreen:
    """Tests for the ProcessingScreen component."""

    async def test_processing_screen_shows_stage_indicators(self):
        """ProcessingScreen displays extract, process, build, deploy stage indicators."""
        app = SetupApp()
        async with app.run_test() as pilot:
            # Push the processing screen and wait for it to mount
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            # Should have stage indicators for each phase
            extract_label = app.screen.query_one("#stage-extract")
            process_label = app.screen.query_one("#stage-process")
            build_label = app.screen.query_one("#stage-build")
            deploy_label = app.screen.query_one("#stage-deploy")

            assert extract_label is not None
            assert process_label is not None
            assert build_label is not None
            assert deploy_label is not None

    async def test_processing_screen_has_start_button(self):
        """ProcessingScreen has a Start button to begin generation."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            start_button = app.screen.query_one("#start-generation")
            assert start_button is not None
            assert not start_button.disabled

    async def test_processing_screen_has_log_output_area(self):
        """ProcessingScreen has a log output area for status messages."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            log_area = app.screen.query_one("#log-output")
            assert log_area is not None


class TestSummaryScreen:
    """Tests for the SummaryScreen component."""

    async def test_summary_screen_has_generate_button(self):
        """SummaryScreen has a Generate button to start the pipeline."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            generate_button = app.screen.query_one("#generate")
            assert generate_button is not None

    async def test_generate_button_disabled_initially(self):
        """Generate button is disabled until config is saved."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            generate_button = app.screen.query_one("#generate")
            assert generate_button.disabled is True

    async def test_generate_button_navigates_to_processing_screen(self):
        """Clicking Generate navigates to ProcessingScreen."""
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            # Enable the button manually for testing navigation
            generate_button = app.screen.query_one("#generate", Button)
            generate_button.disabled = False

            # Press the button directly
            generate_button.press()
            await pilot.pause()

            # Should now be on ProcessingScreen
            assert isinstance(app.screen, ProcessingScreen)

    async def test_generate_button_enabled_after_save(self):
        """Generate button should be enabled after config is saved."""
        from unittest.mock import patch
        from textual.widgets import Button

        app = SetupApp()
        # Pre-populate config data so save works
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "test_token"},
            "llm": {"provider": "anthropic", "api_key": "test_key"},
            "hosting": {"provider": "cloudflare", "cloudflare": {}},
        }

        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            # Generate button should be disabled initially
            generate_button = app.screen.query_one("#generate", Button)
            assert generate_button.disabled is True

            # Mock the file write to avoid actual I/O
            with patch("builtins.open"):
                # Press save button
                save_button = app.screen.query_one("#save", Button)
                save_button.press()
                await pilot.pause()

            # Generate button should now be enabled
            assert generate_button.disabled is False


class TestHostingScreen:
    """Tests for the HostingScreen config pre-fill."""

    async def test_hosting_screen_prefills_cloudflare_from_config(self):
        """HostingScreen pre-fills Cloudflare fields from existing config."""
        from textual.widgets import Input, RadioButton, RadioSet

        app = SetupApp()
        app.config_data = {
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {
                    "account_id": "test_account_id",
                    "project_name": "test_project",
                },
            }
        }

        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            # Check provider is selected
            provider_set = app.screen.query_one("#provider-set", RadioSet)
            cloudflare_button = app.screen.query_one("#cloudflare", RadioButton)
            assert cloudflare_button.value is True

            # Check fields are pre-filled
            account_id = app.screen.query_one("#account-id", Input)
            project_name = app.screen.query_one("#project-name", Input)

            assert account_id.value == "test_account_id"
            assert project_name.value == "test_project"

    async def test_hosting_screen_prefills_vercel_from_config(self):
        """HostingScreen pre-fills Vercel fields from existing config."""
        from textual.widgets import Input, RadioButton

        app = SetupApp()
        app.config_data = {
            "hosting": {
                "provider": "vercel",
                "vercel": {
                    "token": "vercel_token_123",
                    "project_name": "my_vercel_project",
                },
            }
        }

        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            # Check provider is selected
            vercel_button = app.screen.query_one("#vercel", RadioButton)
            assert vercel_button.value is True

            # Check fields are pre-filled
            token = app.screen.query_one("#token", Input)
            project_name = app.screen.query_one("#project-name", Input)

            assert token.value == "vercel_token_123"
            assert project_name.value == "my_vercel_project"
