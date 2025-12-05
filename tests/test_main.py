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
        mock_run.assert_called_once_with(
            ["npm", "run", "preview"], cwd=frontend_dir, check=True
        )

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
