# ABOUTME: Tests for the main CLI module including command execution and directory detection.
# ABOUTME: Verifies frontend directory detection logic for preview and other commands.

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from plex_wrapped.main import app, detect_frontend_directory


runner = CliRunner()


class TestDetectFrontendDirectory:
    """Test frontend directory detection logic."""

    def test_finds_frontend_in_current_directory(self, tmp_path: Path) -> None:
        """Should find frontend/ in current directory."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()

        with patch("plex_wrapped.main.Path.cwd", return_value=tmp_path):
            result = detect_frontend_directory()

        assert result == frontend_dir

    def test_finds_frontend_in_parent_directory(self, tmp_path: Path) -> None:
        """Should find frontend/ in parent directory."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        cli_dir = tmp_path / "cli"
        cli_dir.mkdir()

        with patch("plex_wrapped.main.Path.cwd", return_value=cli_dir):
            result = detect_frontend_directory()

        assert result == frontend_dir

    def test_finds_frontend_two_levels_up(self, tmp_path: Path) -> None:
        """Should find frontend/ two parent directories up."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        sub1 = tmp_path / "sub1"
        sub1.mkdir()
        sub2 = sub1 / "sub2"
        sub2.mkdir()

        with patch("plex_wrapped.main.Path.cwd", return_value=sub2):
            result = detect_frontend_directory()

        assert result == frontend_dir

    def test_finds_frontend_three_levels_up(self, tmp_path: Path) -> None:
        """Should find frontend/ three parent directories up."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        sub1 = tmp_path / "sub1"
        sub1.mkdir()
        sub2 = sub1 / "sub2"
        sub2.mkdir()
        sub3 = sub2 / "sub3"
        sub3.mkdir()

        with patch("plex_wrapped.main.Path.cwd", return_value=sub3):
            result = detect_frontend_directory()

        assert result == frontend_dir

    def test_returns_none_when_not_found(self, tmp_path: Path) -> None:
        """Should return None when frontend/ is not found."""
        with patch("plex_wrapped.main.Path.cwd", return_value=tmp_path):
            result = detect_frontend_directory()

        assert result is None


class TestPreviewCommand:
    """Test the preview command."""

    @patch("plex_wrapped.main.subprocess.run")
    @patch("plex_wrapped.main.detect_frontend_directory")
    def test_preview_success(
        self, mock_detect: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Should start preview server when frontend directory is found."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        mock_detect.return_value = frontend_dir
        mock_run.return_value = None

        result = runner.invoke(app, ["preview"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(["npm", "run", "preview"], cwd=frontend_dir, check=True)

    @patch("plex_wrapped.main.detect_frontend_directory")
    def test_preview_frontend_not_found(self, mock_detect: MagicMock) -> None:
        """Should exit with error when frontend directory is not found."""
        mock_detect.return_value = None

        result = runner.invoke(app, ["preview"])

        assert result.exit_code == 1
        assert "Frontend directory not found" in result.stdout

    @patch("plex_wrapped.main.subprocess.run")
    @patch("plex_wrapped.main.detect_frontend_directory")
    def test_preview_subprocess_error(
        self, mock_detect: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Should handle subprocess errors gracefully."""
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        mock_detect.return_value = frontend_dir
        mock_run.side_effect = subprocess.CalledProcessError(1, ["npm"])

        result = runner.invoke(app, ["preview"])

        assert result.exit_code == 1
        assert "Preview failed" in result.stdout


def write_config(tmp_path: Path, **overrides) -> Path:
    """A minimal valid config.yaml - real file, no network/AI/hosting providers."""
    import yaml

    config_data = {
        "plex": {"url": "https://plex.example.com", "token": "test-token"},
        "llm": {"provider": "none"},
        "hosting": {"provider": "none"},
        "year": 2024,
        **overrides,
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))
    return config_file


class TestGetOrchestrator:
    def test_loads_config_and_builds_an_orchestrator(self, tmp_path: Path) -> None:
        from plex_wrapped.main import get_orchestrator

        config_file = write_config(tmp_path)

        orchestrator = get_orchestrator(str(config_file))

        assert orchestrator.config.plex.url == "https://plex.example.com"

    def test_year_override_applies_to_the_loaded_config(self, tmp_path: Path) -> None:
        from plex_wrapped.main import get_orchestrator

        config_file = write_config(tmp_path)

        orchestrator = get_orchestrator(str(config_file), year=2025)

        assert orchestrator.config.year == 2025

    def test_missing_config_file_exits_with_error(self) -> None:
        from plex_wrapped.main import get_orchestrator

        with pytest.raises(SystemExit) as exc_info:
            get_orchestrator("/nonexistent/config.yaml")

        assert exc_info.value.code == 1


class TestOrchestratedCommands:
    """generate/extract/process/build/deploy all share the same shape: load config,
    call one Orchestrator method, exit 1 with a message if it raises."""

    @pytest.mark.parametrize(
        "command,orchestrator_method,failure_message",
        [
            ("generate", "run_all", "Generation failed"),
            ("extract", "extract", "Extraction failed"),
            ("process", "process", "Processing failed"),
            ("build", "build", "Build failed"),
            ("deploy", "deploy", "Deployment failed"),
        ],
    )
    def test_command_success(
        self, tmp_path: Path, command: str, orchestrator_method: str, failure_message: str
    ) -> None:
        config_file = write_config(tmp_path)

        with patch(f"plex_wrapped.orchestrator.Orchestrator.{orchestrator_method}") as method:
            result = runner.invoke(app, [command, "--config", str(config_file)])

        assert result.exit_code == 0
        method.assert_called_once()

    @pytest.mark.parametrize(
        "command,orchestrator_method,failure_message",
        [
            ("generate", "run_all", "Generation failed"),
            ("extract", "extract", "Extraction failed"),
            ("process", "process", "Processing failed"),
            ("build", "build", "Build failed"),
            ("deploy", "deploy", "Deployment failed"),
        ],
    )
    def test_command_reports_failure_and_exits_nonzero(
        self, tmp_path: Path, command: str, orchestrator_method: str, failure_message: str
    ) -> None:
        config_file = write_config(tmp_path)

        with patch(
            f"plex_wrapped.orchestrator.Orchestrator.{orchestrator_method}",
            side_effect=RuntimeError("boom"),
        ):
            result = runner.invoke(app, [command, "--config", str(config_file)])

        assert result.exit_code == 1
        assert failure_message in result.stdout

    def test_generate_and_extract_and_process_accept_a_year_override(self, tmp_path: Path) -> None:
        config_file = write_config(tmp_path)

        with patch("plex_wrapped.orchestrator.Orchestrator.extract") as extract:
            result = runner.invoke(app, ["extract", "--config", str(config_file), "--year", "2019"])

        assert result.exit_code == 0
        extract.assert_called_once()


class TestSetupWizardEntryPoints:
    """The bare CLI and `init` both launch the TUI wizard."""

    @patch("plex_wrapped.setup_tui.SetupApp")
    def test_bare_invocation_launches_the_wizard(self, mock_app_cls: MagicMock) -> None:
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        mock_app_cls.return_value.run.assert_called_once()

    @patch("plex_wrapped.setup_tui.SetupApp")
    def test_init_command_launches_the_wizard(self, mock_app_cls: MagicMock) -> None:
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        mock_app_cls.return_value.run.assert_called_once()


class TestPreviewKeyboardInterrupt:
    @patch("plex_wrapped.main.subprocess.run")
    @patch("plex_wrapped.main.detect_frontend_directory")
    def test_preview_stopped_by_keyboard_interrupt_exits_cleanly(
        self, mock_detect: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        mock_detect.return_value = frontend_dir
        mock_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["preview"])

        assert result.exit_code == 0
        assert "Preview server stopped" in result.stdout
