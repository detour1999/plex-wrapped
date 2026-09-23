# ABOUTME: Tests for CLI orchestration.
# ABOUTME: Verifies end-to-end workflow from extract to deploy.

import json

import pytest
from pathlib import Path

from plex_wrapped.orchestrator import Orchestrator
from plex_wrapped.config import Config, PlexConfig, LLMConfig, HostingConfig, CloudflareConfig


class TestOrchestrator:
    def test_orchestrator_initializes_with_config(self, tmp_path: Path) -> None:
        """Orchestrator accepts config and output directory."""
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(
                provider="cloudflare",
                cloudflare=CloudflareConfig(account_id="x", project_name="y"),
            ),
            output_dir=tmp_path,
        )

        orchestrator = Orchestrator(config)

        assert orchestrator.config == config
        assert orchestrator.output_dir == tmp_path


def make_orchestrator(project_root: Path, output_dir: Path) -> Orchestrator:
    config = Config(
        plex=PlexConfig(url="https://test.com", token="test"),
        llm=LLMConfig(provider="none"),
        year=2024,
        hosting=HostingConfig(provider="none"),
        output_dir=output_dir,
        project_root=project_root,
    )
    return Orchestrator(config)


def make_frontend(project_root: Path) -> Path:
    """Create a minimal real npm project whose only dependency is a local folder.

    Installing it needs no network but still creates a real node_modules directory.
    The preinstall script leaves a marker so tests can tell whether npm install ran.
    """
    frontend = project_root / "frontend"
    local_dep = frontend / "local-dep"
    local_dep.mkdir(parents=True)
    (local_dep / "package.json").write_text('{"name": "local-dep", "version": "1.0.0"}')
    (frontend / "package.json").write_text(
        json.dumps(
            {
                "name": "fake-frontend",
                "version": "1.0.0",
                "private": True,
                "dependencies": {"local-dep": "file:./local-dep"},
                "scripts": {
                    "preinstall": "touch npm-install-ran",
                    "build": "mkdir -p dist && touch dist/built",
                },
            }
        )
    )
    return frontend


class TestProcessYearConsistency:
    def test_process_stats_year_matches_the_raw_filename_year(self, tmp_path: Path) -> None:
        """The processed file's stats["year"] always matches the year in its own filename.

        Raw files are named "{user}_{year}_raw.json", and process() globs every raw
        file in the data directory rather than just the one for the currently
        configured year. A stale raw file left over from an earlier run (e.g. the
        orchestrator is re-run later with a different config year, without clearing
        old data) must not be stamped with the *current* config year - the year
        embedded in the raw filename is the actual source of truth for what
        listening period that file's data covers, and the frontend derives the
        displayed year from that same filename.
        """
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)

        # Raw data left over from a 2022 run, while the orchestrator is now
        # configured for 2025.
        history = {"user": "alice", "year": 2022, "tracks": []}
        (data_dir / "alice_2022_raw.json").write_text(json.dumps(history))

        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2025,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        Orchestrator(config).process()

        processed_file = data_dir / "alice_2022_processed.json"
        assert processed_file.exists()

        stats = json.loads(processed_file.read_text())
        assert stats["year"] == 2022


class TestBuild:
    def test_build_installs_dependencies_when_node_modules_missing(self, tmp_path: Path) -> None:
        """build() runs npm install first if frontend/node_modules does not exist."""
        frontend = make_frontend(tmp_path)

        make_orchestrator(tmp_path, tmp_path / "out").build()

        assert (frontend / "node_modules" / "local-dep").exists()
        assert (frontend / "dist" / "built").exists()

    def test_build_skips_install_when_node_modules_present(self, tmp_path: Path) -> None:
        """build() leaves an existing node_modules alone."""
        frontend = make_frontend(tmp_path)
        (frontend / "node_modules").mkdir()

        make_orchestrator(tmp_path, tmp_path / "out").build()

        assert not (frontend / "npm-install-ran").exists()
        assert (frontend / "dist" / "built").exists()

    def test_build_reports_failed_install(self, tmp_path: Path) -> None:
        """A failing npm install raises a RuntimeError that says so."""
        frontend = make_frontend(tmp_path)
        (frontend / "package.json").write_text("{ this is not valid json")

        with pytest.raises(RuntimeError, match="npm install failed"):
            make_orchestrator(tmp_path, tmp_path / "out").build()

        assert not (frontend / "dist").exists()

    def test_build_explains_missing_npm(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without npm on PATH, build() says to install Node.js instead of crashing."""
        make_frontend(tmp_path)
        empty_bin = tmp_path / "empty-bin"
        empty_bin.mkdir()
        monkeypatch.setenv("PATH", str(empty_bin))

        with pytest.raises(RuntimeError, match="npm.*Node.js"):
            make_orchestrator(tmp_path, tmp_path / "out").build()
