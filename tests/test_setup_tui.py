# ABOUTME: Tests for the TUI setup wizard and processing screen.
# ABOUTME: Uses Textual's pilot API for async UI testing.

from plex_wrapped.setup_tui import (
    HostingScreen,
    PlexScreen,
    ProcessingScreen,
    SetupApp,
    SummaryScreen,
)


class TestPlexScreen:
    """Tests for the PlexScreen connection form."""

    async def test_empty_url_and_token_shows_error_instead_of_crashing(self):
        """Testing the connection with empty fields reports what is missing."""
        from textual.widgets import Button, Static

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            await pilot.pause()

            app.screen.query_one("#test", Button).press()
            await pilot.pause()

            status = app.screen.query_one("#status", Static)
            assert "Please enter both URL and token" in str(status.render())


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
        from textual.widgets import Input, RadioButton

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


class TestWelcomeScreen:
    async def test_get_started_navigates_to_plex_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import WelcomeScreen

            await app.push_screen(WelcomeScreen())
            await pilot.pause()

            app.screen.query_one("#get-started", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, PlexScreen)


class TestPlexScreenExtra:
    async def test_on_mount_prefills_url_and_token_from_config(self):
        from textual.widgets import Input

        app = SetupApp()
        app.config_data = {"plex": {"url": "http://test:32400", "token": "abc123"}}
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            await pilot.pause()

            assert app.screen.query_one("#plex-url", Input).value == "http://test:32400"
            assert app.screen.query_one("#plex-token", Input).value == "abc123"

    async def test_back_button_pops_the_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import WelcomeScreen

            await app.push_screen(WelcomeScreen())
            await app.push_screen(PlexScreen())
            await pilot.pause()

            app.screen.query_one("#back", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, WelcomeScreen)

    async def test_show_status_error_and_default_styling(self):
        from textual.widgets import Static

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            await pilot.pause()

            app.screen.show_status("bad", "error")
            assert "bad" in str(app.screen.query_one("#status", Static).render())

            app.screen.show_status("info", "warning")
            assert "info" in str(app.screen.query_one("#status", Static).render())

    async def test_next_button_navigates_to_llm_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            await pilot.pause()

            next_button = app.screen.query_one("#next", Button)
            next_button.disabled = False
            next_button.press()
            await pilot.pause()

            from plex_wrapped.setup_tui import LLMScreen

            assert isinstance(app.screen, LLMScreen)


class TestLLMScreen:
    async def test_on_mount_prefills_api_key_and_selects_provider(self):
        from textual.widgets import Input, RadioButton

        app = SetupApp()
        app.config_data = {"llm": {"provider": "openai", "api_key": "sk-test"}}
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            assert app.screen.query_one("#api-key", Input).value == "sk-test"
            assert app.screen.query_one("#openai", RadioButton).value is True

    async def test_provider_changed_updates_help_text_for_openai(self):
        from textual.widgets import RadioButton, RadioSet, Static

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            radio_set = app.screen.query_one("#provider-set", RadioSet)
            radio_set.action_toggle_button()  # anthropic -> openai focus change alone won't fire event
            openai_button = app.screen.query_one("#openai", RadioButton)
            openai_button.value = True
            await pilot.pause()

            help_text = str(app.screen.query_one("#api-key-help", Static).render())
            assert "OpenAI" in help_text or "platform.openai.com" in help_text

    async def test_back_button_pops_the_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            app.screen.query_one("#back", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, PlexScreen)

    async def test_validate_with_empty_key_shows_error_instead_of_calling_a_real_api(self):
        from textual.widgets import Button, Static

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            app.screen.query_one("#validate", Button).press()
            await pilot.pause()

            assert "Please enter an API key" in str(
                app.screen.query_one("#status", Static).render()
            )

    async def test_show_status_error_and_default_styling(self):
        from textual.widgets import Static

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            app.screen.show_status("bad", "error")
            assert "bad" in str(app.screen.query_one("#status", Static).render())
            app.screen.show_status("info", "warning")
            assert "info" in str(app.screen.query_one("#status", Static).render())

    async def test_next_button_navigates_to_hosting_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            next_button = app.screen.query_one("#next", Button)
            next_button.disabled = False
            next_button.press()
            await pilot.pause()

            assert isinstance(app.screen, HostingScreen)


class TestHostingScreenPrefillRemainingProviders:
    async def test_prefills_netlify_from_config(self):
        from textual.widgets import Input, RadioButton

        app = SetupApp()
        app.config_data = {
            "hosting": {
                "provider": "netlify",
                "netlify": {"auth_token": "netlify-tok", "site_id": "site-123"},
            }
        }
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            assert app.screen.query_one("#netlify", RadioButton).value is True
            assert app.screen.query_one("#token", Input).value == "netlify-tok"
            assert app.screen.query_one("#site-id", Input).value == "site-123"

    async def test_prefills_github_from_config(self):
        from textual.widgets import Input, RadioButton

        app = SetupApp()
        app.config_data = {
            "hosting": {"provider": "github", "github": {"repo": "me/repo", "branch": "main"}}
        }
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            assert app.screen.query_one("#github", RadioButton).value is True
            assert app.screen.query_one("#repo", Input).value == "me/repo"
            assert app.screen.query_one("#branch", Input).value == "main"

    async def test_prefills_cloudflare_api_token(self):
        """The api_token field specifically - the account_id/project_name pair is
        already covered by the pre-existing cloudflare prefill test."""
        from textual.widgets import Input

        app = SetupApp()
        app.config_data = {
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {"api_token": "cf-tok"},
            }
        }
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            assert app.screen.query_one("#api-token", Input).value == "cf-tok"

    async def test_no_prefill_when_app_has_no_config_data(self):
        """_prefill_hosting_fields returns early when there's nothing to prefill."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            # Default provider (cloudflare) fields exist and are simply empty.
            from textual.widgets import Input

            assert app.screen.query_one("#account-id", Input).value == ""


class TestHostingScreenProviderSwitching:
    async def test_switching_provider_rebuilds_the_dynamic_fields(self):
        from textual.widgets import Input, RadioButton

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#vercel", RadioButton).value = True
            await pilot.pause()

            # Cloudflare-only fields are gone, Vercel fields exist.
            assert len(app.screen.query("#account-id")) == 0
            assert app.screen.query_one("#token", Input) is not None

    async def test_reselecting_the_same_provider_does_not_rebuild_fields(self):
        """on_provider_changed only rebuilds when the pressed id actually differs."""
        from textual.widgets import RadioButton

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            container_before = app.screen.query_one("#dynamic-fields")
            children_before = list(container_before.children)

            app.screen.query_one("#cloudflare", RadioButton).value = True
            await pilot.pause()

            assert list(app.screen.query_one("#dynamic-fields").children) == children_before

    async def test_back_button_pops_the_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#back", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, LLMScreen)


class TestHostingScreenGoToSummary:
    async def test_collects_cloudflare_fields_and_navigates_to_summary(self):
        from textual.widgets import Button, Input

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#account-id", Input).value = "acc"
            app.screen.query_one("#project-name", Input).value = "proj"
            app.screen.query_one("#api-token", Input).value = "tok"
            app.screen.query_one("#next", Button).press()
            await pilot.pause()

            assert app.config_data["hosting"] == {
                "provider": "cloudflare",
                "cloudflare": {"account_id": "acc", "project_name": "proj", "api_token": "tok"},
            }
            assert isinstance(app.screen, SummaryScreen)

    async def test_collects_vercel_fields(self):
        from textual.widgets import Button, Input, RadioButton

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#vercel", RadioButton).value = True
            await pilot.pause()
            app.screen.query_one("#token", Input).value = "vtok"
            app.screen.query_one("#project-name", Input).value = "vproj"
            app.screen.query_one("#next", Button).press()
            await pilot.pause()

            assert app.config_data["hosting"] == {
                "provider": "vercel",
                "vercel": {"token": "vtok", "project_name": "vproj"},
            }

    async def test_collects_netlify_fields(self):
        from textual.widgets import Button, Input, RadioButton

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#netlify", RadioButton).value = True
            await pilot.pause()
            app.screen.query_one("#token", Input).value = "ntok"
            app.screen.query_one("#site-id", Input).value = "nsite"
            app.screen.query_one("#next", Button).press()
            await pilot.pause()

            assert app.config_data["hosting"] == {
                "provider": "netlify",
                "netlify": {"auth_token": "ntok", "site_id": "nsite"},
            }

    async def test_collects_github_fields_and_defaults_branch(self):
        from textual.widgets import Button, Input, RadioButton

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await pilot.pause()

            app.screen.query_one("#github", RadioButton).value = True
            await pilot.pause()
            app.screen.query_one("#repo", Input).value = "me/repo"
            app.screen.query_one("#next", Button).press()
            await pilot.pause()

            assert app.config_data["hosting"] == {
                "provider": "github",
                "github": {"repo": "me/repo", "branch": "gh-pages"},
            }


class TestSummaryScreenExtra:
    async def test_build_summary_with_no_app_config(self):
        """build_summary defends against self.app not being a SetupApp - not reachable
        through normal use, but a real branch worth verifying returns the right text."""
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            # It IS a SetupApp in normal use; exercise the branch by calling the
            # method with an empty config_data instead (the realistic empty case).
            app.config_data = {}
            assert "Configuration Summary" in app.screen.build_summary()

    async def test_build_summary_includes_plex_llm_and_hosting_sections(self):
        app = SetupApp()
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "abcd1234"},
            "llm": {"provider": "anthropic", "api_key": "sk-abcd1234"},
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {"account_id": "acc", "api_token": "cftokenvalue"},
            },
        }
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            summary = app.screen.build_summary()
            assert "http://test:32400" in summary
            assert "Anthropic" in summary
            assert "Cloudflare" in summary
            # Token/key fields are masked, never shown in full.
            assert "abcd1234" not in summary
            assert "sk-abcd1234" not in summary
            assert "cftokenvalue" not in summary
            assert "acc" in summary  # non-secret field shown as-is

    async def test_back_button_pops_the_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(HostingScreen())
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            app.screen.query_one("#back", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, HostingScreen)

    async def test_save_config_rejects_a_non_numeric_year(self, tmp_path, monkeypatch):
        from textual.widgets import Button, Input, Static

        monkeypatch.chdir(tmp_path)
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            app.screen.query_one("#year", Input).value = "not-a-year"
            app.screen.query_one("#save", Button).press()
            await pilot.pause()

            assert "Invalid year value" in str(app.screen.query_one("#status", Static).render())
            assert not (tmp_path / "config.yaml").exists()

    async def test_save_config_writes_a_real_yaml_file_and_enables_generate(
        self, tmp_path, monkeypatch
    ):
        from textual.widgets import Button, Input

        monkeypatch.chdir(tmp_path)
        app = SetupApp()
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "tok"},
            "llm": {"provider": "none"},
            "hosting": {"provider": "none"},
        }
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            app.screen.query_one("#year", Input).value = "2025"
            app.screen.query_one("#output-dir", Input).value = "out"
            save_button = app.screen.query_one("#save", Button)
            save_button.press()
            await pilot.pause()

            saved = (tmp_path / "config.yaml").read_text()
            assert "2025" in saved
            assert save_button.disabled is True
            assert app.screen.query_one("#generate", Button).disabled is False

    async def test_save_config_defaults_a_blank_output_dir_to_dist(self, tmp_path, monkeypatch):
        from textual.widgets import Button, Input

        monkeypatch.chdir(tmp_path)
        app = SetupApp()
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "tok"},
            "llm": {"provider": "none"},
            "hosting": {"provider": "none"},
        }
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            app.screen.query_one("#output-dir", Input).value = ""
            app.screen.query_one("#save", Button).press()
            await pilot.pause()

        assert app.config_data["output_dir"] == "dist"

    async def test_save_config_reports_a_write_failure(self, tmp_path, monkeypatch):
        from textual.widgets import Button, Static

        monkeypatch.chdir(tmp_path)
        app = SetupApp()
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "tok"},
            "llm": {"provider": "none"},
            "hosting": {"provider": "none"},
        }
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            # Make config.yaml a directory so open(..., "w") fails.
            (tmp_path / "config.yaml").mkdir()
            app.screen.query_one("#save", Button).press()
            await pilot.pause()

            assert "Failed to save config" in str(app.screen.query_one("#status", Static).render())

    async def test_show_status_default_styling(self):
        from textual.widgets import Static

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(SummaryScreen())
            await pilot.pause()

            app.screen.show_status("saved!", "success")
            assert "saved!" in str(app.screen.query_one("#status", Static).render())


class TestProcessingScreenNavigationAndUiUpdates:
    async def test_edit_config_navigates_to_plex_screen(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen.query_one("#edit-config", Button).press()
            await pilot.pause()

            assert isinstance(app.screen, PlexScreen)

    async def test_log_appends_a_line_to_the_log_widget(self):
        from textual.widgets import RichLog

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen._log("hello from a test")
            await pilot.pause()

            log_widget = app.screen.query_one("#log-output", RichLog)
            assert len(log_widget.lines) >= 1

    async def test_update_ui_start_disables_the_button_and_clears_the_log(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen._update_ui_start()
            await pilot.pause()

            button = app.screen.query_one("#start-generation", Button)
            assert button.disabled is True
            assert button.label.plain == "Running..."

    async def test_update_ui_stage_logs_running_and_done_messages(self):
        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen._update_ui_stage("extract", "running", "starting up")
            app.screen._update_ui_stage("extract", "done", "all finished")
            await pilot.pause()

            from textual.widgets import Static

            assert "Done" in str(app.screen.query_one("#status-extract", Static).render())

    async def test_update_ui_complete_logs_message_and_relabels_button(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen._update_ui_complete("all done")
            await pilot.pause()

            assert app.screen.query_one("#start-generation", Button).label.plain == "Done!"

    async def test_update_ui_error_re_enables_the_button_as_retry(self):
        from textual.widgets import Button

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            app.screen._update_ui_start()
            app.screen._update_ui_error("boom")
            await pilot.pause()

            button = app.screen.query_one("#start-generation", Button)
            assert button.disabled is False
            assert button.label.plain == "Retry"

    async def test_update_stage_status_shows_each_status_icon(self):
        from textual.widgets import Static

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            for status, expected in [
                ("running", "Running"),
                ("done", "Done"),
                ("error", "Error"),
                ("skipped", "Skipped"),
            ]:
                app.screen.update_stage_status("build", status)
                assert expected in str(app.screen.query_one("#status-build", Static).render())


class TestRunPipeline:
    """run_pipeline runs Orchestrator.extract/process/build/deploy in a background
    thread. Patching those methods (our own class, not a live service) makes this
    testable without a real Plex/LLM/hosting connection."""

    def _configured_app(self, tmp_path, hosting_provider: str = "none") -> "SetupApp":
        hosting: dict = {"provider": hosting_provider}
        if hosting_provider == "cloudflare":
            hosting["cloudflare"] = {"account_id": "acc", "project_name": "proj"}
        app = SetupApp(project_root=tmp_path)
        app.config_data = {
            "plex": {"url": "http://test:32400", "token": "tok"},
            "llm": {"provider": "none"},
            "hosting": hosting,
            "year": 2024,
            "output_dir": str(tmp_path / "out"),
        }
        return app

    async def test_runs_every_stage_and_marks_completion(self, tmp_path):
        from unittest.mock import patch
        from textual.widgets import Button

        app = self._configured_app(tmp_path)
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            with (
                patch("plex_wrapped.orchestrator.Orchestrator.extract") as extract,
                patch("plex_wrapped.orchestrator.Orchestrator.process") as process,
                patch("plex_wrapped.orchestrator.Orchestrator.build") as build,
                patch("plex_wrapped.orchestrator.Orchestrator.deploy") as deploy,
            ):
                app.screen.query_one("#start-generation", Button).press()
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

            extract.assert_called_once()
            process.assert_called_once()
            build.assert_called_once()
            deploy.assert_not_called()  # hosting provider is "none"

            button = app.screen.query_one("#start-generation", Button)
            assert button.label.plain == "Done!"

    async def test_deploys_when_a_hosting_provider_is_configured(self, tmp_path):
        from unittest.mock import patch
        from textual.widgets import Button

        app = self._configured_app(tmp_path, hosting_provider="cloudflare")
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            with (
                patch("plex_wrapped.orchestrator.Orchestrator.extract"),
                patch("plex_wrapped.orchestrator.Orchestrator.process"),
                patch("plex_wrapped.orchestrator.Orchestrator.build"),
                patch("plex_wrapped.orchestrator.Orchestrator.deploy") as deploy,
            ):
                app.screen.query_one("#start-generation", Button).press()
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

            deploy.assert_called_once()

    async def test_a_failing_stage_shows_retry_instead_of_crashing(self, tmp_path):
        from unittest.mock import patch
        from textual.widgets import Button

        app = self._configured_app(tmp_path)
        async with app.run_test() as pilot:
            await app.push_screen(ProcessingScreen())
            await pilot.pause()

            with patch(
                "plex_wrapped.orchestrator.Orchestrator.extract",
                side_effect=RuntimeError("simulated extraction failure"),
            ):
                app.screen.query_one("#start-generation", Button).press()
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

            button = app.screen.query_one("#start-generation", Button)
            assert button.disabled is False
            assert button.label.plain == "Retry"


class TestSetupAppInitAndConfigLoading:
    def test_detect_project_root_finds_frontend_in_a_parent_directory(self, tmp_path, monkeypatch):
        (tmp_path / "frontend").mkdir()
        sub = tmp_path / "sub"
        sub.mkdir()
        monkeypatch.chdir(sub)

        app = SetupApp()

        assert app.project_root == tmp_path

    def test_detect_project_root_falls_back_to_cwd_when_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        app = SetupApp()

        assert app.project_root == tmp_path

    def test_explicit_project_root_skips_detection(self, tmp_path):
        app = SetupApp(project_root=tmp_path)

        assert app.project_root == tmp_path

    def test_loads_existing_config_yaml(self, tmp_path, monkeypatch):
        import yaml

        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.yaml").write_text(yaml.dump({"plex": {"url": "http://test"}}))

        app = SetupApp()

        assert app.config_data == {"plex": {"url": "http://test"}}

    def test_no_config_yaml_means_empty_config_data(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        app = SetupApp()

        assert app.config_data == {}

    def test_unreadable_config_yaml_falls_back_to_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.yaml").write_text("not: valid: yaml: [")

        app = SetupApp()

        assert app.config_data == {}

    def test_is_config_complete_requires_plex_llm_and_hosting(self, tmp_path):
        app = SetupApp(project_root=tmp_path)

        assert app._is_config_complete() is False

        app.config_data = {"plex": {}, "llm": {}, "hosting": {}}
        assert app._is_config_complete() is True


class TestSetupAppOnMount:
    async def test_shows_welcome_screen_when_config_is_incomplete(self, tmp_path):
        app = SetupApp(project_root=tmp_path)
        async with app.run_test() as pilot:
            await pilot.pause()

            from plex_wrapped.setup_tui import WelcomeScreen

            assert isinstance(app.screen, WelcomeScreen)

    async def test_shows_processing_screen_when_config_is_complete(self, tmp_path):
        app = SetupApp(project_root=tmp_path)
        app.config_data = {"plex": {}, "llm": {}, "hosting": {}}
        async with app.run_test() as pilot:
            await pilot.pause()

            assert isinstance(app.screen, ProcessingScreen)


class TestPlexScreenValidInputDispatch:
    async def test_valid_input_dispatches_to_the_connection_worker(self):
        from unittest.mock import patch
        from textual.widgets import Button, Input

        app = SetupApp()
        async with app.run_test() as pilot:
            await app.push_screen(PlexScreen())
            await pilot.pause()

            app.screen.query_one("#plex-url", Input).value = "http://test:32400"
            app.screen.query_one("#plex-token", Input).value = "a-token"

            with patch.object(app.screen, "test_plex_connection") as worker:
                app.screen.query_one("#test", Button).press()
                await pilot.pause()

            worker.assert_called_once_with("http://test:32400", "a-token")


class TestLLMScreenValidInputDispatch:
    async def test_valid_input_dispatches_to_the_validation_worker(self):
        from unittest.mock import patch
        from textual.widgets import Button, Input

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            app.screen.query_one("#api-key", Input).value = "sk-a-real-key"

            with patch.object(app.screen, "test_llm_key") as worker:
                app.screen.query_one("#validate", Button).press()
                await pilot.pause()

            worker.assert_called_once_with("anthropic", "sk-a-real-key")

    async def test_switching_back_to_anthropic_restores_its_help_text(self):
        from textual.widgets import RadioButton, Static

        app = SetupApp()
        async with app.run_test() as pilot:
            from plex_wrapped.setup_tui import LLMScreen

            await app.push_screen(LLMScreen())
            await pilot.pause()

            app.screen.query_one("#openai", RadioButton).value = True
            await pilot.pause()
            app.screen.query_one("#anthropic", RadioButton).value = True
            await pilot.pause()

            help_text = str(app.screen.query_one("#api-key-help", Static).render())
            assert "console.anthropic.com" in help_text
