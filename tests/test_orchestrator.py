# ABOUTME: Tests for CLI orchestration.
# ABOUTME: Verifies end-to-end workflow from extract to deploy.

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pathlib import Path

from plex_wrapped.orchestrator import Orchestrator
from plex_wrapped.config import (
    Config,
    PlexConfig,
    LLMConfig,
    HostingConfig,
    CloudflareConfig,
    VercelConfig,
    NetlifyConfig,
    GitHubPagesConfig,
)


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


class TestBuildImageMapping:
    def test_returns_empty_dict_when_no_images_directory(self, tmp_path: Path) -> None:
        orchestrator = make_orchestrator(tmp_path, tmp_path / "out")

        assert orchestrator._build_image_mapping("alice") == {}

    def test_maps_artist_album_and_track_images_by_slug(self, tmp_path: Path) -> None:
        images_dir = tmp_path / "out" / "images" / "alice"
        images_dir.mkdir(parents=True)
        (images_dir / "artist-radiohead-a1b2c3d4.jpg").write_bytes(b"x")
        (images_dir / "album-radiohead-ok-computer-e5f6a7b8.jpg").write_bytes(b"x")
        (images_dir / "track-radiohead-karma-police-11223344.jpg").write_bytes(b"x")

        mapping = make_orchestrator(tmp_path, tmp_path / "out")._build_image_mapping("alice")

        assert mapping["artist:radiohead"] == "/images/alice/artist-radiohead-a1b2c3d4.jpg"
        assert mapping["album:radiohead-ok-computer"] == (
            "/images/alice/album-radiohead-ok-computer-e5f6a7b8.jpg"
        )
        assert mapping["track:radiohead-karma-police"] == (
            "/images/alice/track-radiohead-karma-police-11223344.jpg"
        )

    def test_skips_files_it_cannot_parse(self, tmp_path: Path) -> None:
        """A subdirectory or a filename with no hash suffix is skipped, not an error."""
        images_dir = tmp_path / "out" / "images" / "alice"
        images_dir.mkdir(parents=True)
        (images_dir / "subdir").mkdir()
        (images_dir / "noext").write_bytes(b"x")

        mapping = make_orchestrator(tmp_path, tmp_path / "out")._build_image_mapping("alice")

        assert mapping == {}


def write_raw_history(data_dir: Path, user: str, year: int, tracks: list[dict]) -> Path:
    history = {"user": user, "year": year, "tracks": tracks}
    path = data_dir / f"{user}_{year}_raw.json"
    path.write_text(json.dumps(history, default=str))
    return path


def a_track(title: str, artist: str, album: str, played_at: str, plays_hint: int = 1) -> dict:
    return {
        "title": title,
        "artist": artist,
        "album": album,
        "duration_ms": 200_000,
        "played_at": played_at,
        "user": "alice",
    }


class TestProcessStatsAndImages:
    def test_uses_local_images_when_available_and_falls_back_otherwise(
        self, tmp_path: Path
    ) -> None:
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        tracks = [a_track("Karma Police", "Radiohead", "OK Computer", "2024-03-01T12:00:00")]
        write_raw_history(data_dir, "alice", 2024, tracks)

        images_dir = output_dir / "images" / "alice"
        images_dir.mkdir(parents=True)
        (images_dir / "artist-radiohead-aaaaaaaa.jpg").write_bytes(b"x")

        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        Orchestrator(config).process()

        stats = json.loads((data_dir / "alice_2024_processed.json").read_text())
        assert stats["top_artists"][0]["image_url"] == "/images/alice/artist-radiohead-aaaaaaaa.jpg"
        # No local album art was ever placed, so it falls back to whatever
        # StatsProcessor supplies (None here, since the raw track carries no thumb_url).
        assert stats["top_albums"][0]["image_url"] is None

    def test_raises_when_data_directory_is_missing(self, tmp_path: Path) -> None:
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=tmp_path / "out",
        )

        with pytest.raises(RuntimeError, match="Data directory not found"):
            Orchestrator(config).process()

    def test_raises_when_no_raw_files_present(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "out"
        (output_dir / "data").mkdir(parents=True)
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )

        with pytest.raises(RuntimeError, match="No raw data files found"):
            Orchestrator(config).process()

    def test_processes_every_raw_file_in_the_data_directory(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        write_raw_history(
            data_dir, "alice", 2024, [a_track("A", "Artist A", "Album A", "2024-01-01T00:00:00")]
        )
        write_raw_history(
            data_dir, "bob", 2024, [a_track("B", "Artist B", "Album B", "2024-01-01T00:00:00")]
        )

        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        Orchestrator(config).process()

        assert (data_dir / "alice_2024_processed.json").exists()
        assert (data_dir / "bob_2024_processed.json").exists()

    def test_old_format_filename_without_a_year_falls_back_to_config_year(
        self, tmp_path: Path
    ) -> None:
        """A raw filename with no trailing _{year} (pre-existing legacy data) uses the
        currently configured year rather than crashing on int(file_year)."""
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        history = {
            "user": "alice",
            "year": 2024,
            "tracks": [a_track("A", "Art", "Alb", "2024-01-01T00:00:00")],
        }
        (data_dir / "alice_raw.json").write_text(json.dumps(history))

        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        Orchestrator(config).process()

        assert (data_dir / "alice_2024_processed.json").exists()


class RecordingLLMProvider:
    """A local LLMProvider double - our own interface, not a third-party API - so
    process()'s AI-generation orchestration is testable without a live LLM call."""

    def __init__(self, response: str = "{}", fail_on: set[str] | None = None) -> None:
        self.response = response
        self.fail_on = fail_on or set()
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        for name in self.fail_on:
            if name in prompt.lower():
                raise RuntimeError(f"simulated failure for {name}")
        return self.response

    def generate_creative_pick(self, prompt: str) -> str:
        return "a testable creative choice"


class TestProcessAIGeneration:
    def _process_with_provider(self, tmp_path: Path, provider) -> dict:
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        write_raw_history(
            data_dir, "alice", 2024, [a_track("A", "Artist", "Album", "2024-01-01T00:00:00")]
        )
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="anthropic", api_key="unused"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        with patch("plex_wrapped.orchestrator.get_provider", return_value=provider):
            Orchestrator(config).process()
        return json.loads((data_dir / "alice_2024_processed.json").read_text())

    def test_ai_content_is_generated_for_every_generator(self, tmp_path: Path) -> None:
        provider = RecordingLLMProvider('{"narrative": "a story"}')

        stats = self._process_with_provider(tmp_path, provider)

        expected = {
            "narrative",
            "personality",
            "roast",
            "aura",
            "superlatives",
            "hot_takes",
            "suggestions",
            "theme",
        }
        assert set(stats["ai_content"].keys()) == expected

    def test_a_failing_generator_does_not_stop_the_others(self, tmp_path: Path) -> None:
        provider = RecordingLLMProvider('{"ok": true}', fail_on={"roast"})

        stats = self._process_with_provider(tmp_path, provider)

        assert stats["ai_content"]["roast"] == {}
        assert stats["ai_content"]["narrative"] == {"ok": True}

    def test_no_ai_content_key_when_provider_is_none(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        write_raw_history(
            data_dir, "alice", 2024, [a_track("A", "Artist", "Album", "2024-01-01T00:00:00")]
        )
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )

        Orchestrator(config).process()

        stats = json.loads((data_dir / "alice_2024_processed.json").read_text())
        assert "ai_content" not in stats

    def test_on_progress_callback_receives_messages_including_a_failure_warning(
        self, tmp_path: Path
    ) -> None:
        provider = RecordingLLMProvider('{"ok": true}', fail_on={"roast"})
        output_dir = tmp_path / "out"
        data_dir = output_dir / "data"
        data_dir.mkdir(parents=True)
        write_raw_history(
            data_dir, "alice", 2024, [a_track("A", "Artist", "Album", "2024-01-01T00:00:00")]
        )
        config = Config(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="anthropic", api_key="unused"),
            year=2024,
            hosting=HostingConfig(provider="none"),
            output_dir=output_dir,
        )
        messages: list[str] = []

        with patch("plex_wrapped.orchestrator.get_provider", return_value=provider):
            Orchestrator(config).process(on_progress=messages.append)

        assert any("Processing user" in m for m in messages)
        assert any("Generating AI insights" in m for m in messages)
        assert any("Generating narrative" in m for m in messages)
        assert any("Warning: Failed to generate roast" in m for m in messages)


class TestBuildEdgeCases:
    def test_raises_when_frontend_directory_is_missing(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="Frontend directory not found"):
            make_orchestrator(tmp_path, tmp_path / "out").build()

    def test_reports_a_failing_npm_build(self, tmp_path: Path) -> None:
        frontend = make_frontend(tmp_path)
        (frontend / "node_modules").mkdir()  # skip install
        package = json.loads((frontend / "package.json").read_text())
        package["scripts"]["build"] = "exit 1"
        (frontend / "package.json").write_text(json.dumps(package))

        with pytest.raises(RuntimeError, match="Frontend build failed"):
            make_orchestrator(tmp_path, tmp_path / "out").build()

    def test_copies_images_from_output_dir_into_frontend_dist(self, tmp_path: Path) -> None:
        frontend = make_frontend(tmp_path)
        (frontend / "node_modules").mkdir()
        output_dir = tmp_path / "out"
        images_dir = output_dir / "images" / "alice"
        images_dir.mkdir(parents=True)
        (images_dir / "artist-x.jpg").write_bytes(b"x")

        make_orchestrator(tmp_path, output_dir).build()

        copied = frontend / "dist" / "images" / "alice" / "artist-x.jpg"
        assert copied.read_bytes() == b"x"

    def test_replaces_a_stale_dist_images_directory(self, tmp_path: Path) -> None:
        """A previous build's leftover dist/images is removed, not merged with the new one."""
        frontend = make_frontend(tmp_path)
        (frontend / "node_modules").mkdir()
        (frontend / "dist").mkdir()
        stale = frontend / "dist" / "images" / "old-user"
        stale.mkdir(parents=True)
        (stale / "stale.jpg").write_bytes(b"old")

        output_dir = tmp_path / "out"
        images_dir = output_dir / "images" / "alice"
        images_dir.mkdir(parents=True)
        (images_dir / "artist-x.jpg").write_bytes(b"new")

        make_orchestrator(tmp_path, output_dir).build()

        assert not (frontend / "dist" / "images" / "old-user").exists()
        assert (frontend / "dist" / "images" / "alice" / "artist-x.jpg").read_bytes() == b"new"

    def test_no_error_when_there_are_no_images_to_copy(self, tmp_path: Path) -> None:
        make_frontend(tmp_path)
        make_orchestrator(tmp_path, tmp_path / "out").build()  # should simply not copy anything


def make_orchestrator_with_hosting(project_root: Path, hosting: HostingConfig) -> Orchestrator:
    config = Config(
        plex=PlexConfig(url="https://test.com", token="test"),
        llm=LLMConfig(provider="none"),
        year=2024,
        hosting=hosting,
        output_dir=project_root / "out",
        project_root=project_root,
    )
    return Orchestrator(config)


class TestDeployDispatch:
    def test_skips_deployment_when_provider_is_none(self, tmp_path: Path) -> None:
        orchestrator = make_orchestrator_with_hosting(tmp_path, HostingConfig(provider="none"))

        orchestrator.deploy()  # must not raise, must not try to find a dist/ dir

    def test_raises_when_dist_directory_is_missing(self, tmp_path: Path) -> None:
        hosting = HostingConfig(
            provider="cloudflare",
            cloudflare=CloudflareConfig(account_id="x", project_name="y"),
        )
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with pytest.raises(RuntimeError, match="Build directory not found"):
            orchestrator.deploy()

    @pytest.mark.parametrize(
        "provider,hosting_field,method",
        [
            (
                "cloudflare",
                CloudflareConfig(account_id="x", project_name="y"),
                "_deploy_cloudflare",
            ),
            ("vercel", VercelConfig(project_name="y"), "_deploy_vercel"),
            ("netlify", NetlifyConfig(site_id="y"), "_deploy_netlify"),
            ("github", GitHubPagesConfig(repo="a/b"), "_deploy_github"),
        ],
    )
    def test_dispatches_to_the_right_deploy_method(
        self, tmp_path: Path, provider: str, hosting_field, method: str
    ) -> None:
        (tmp_path / "frontend" / "dist").mkdir(parents=True)
        hosting = HostingConfig(provider=provider, **{provider: hosting_field})
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with patch.object(orchestrator, method) as deploy_method:
            orchestrator.deploy()

        deploy_method.assert_called_once()


class TestDeployDispatchUnsupportedProvider:
    def test_unsupported_provider_raises(self, tmp_path: Path) -> None:
        """Pydantic's Literal type already blocks this through normal construction;
        model_construct bypasses validation to exercise the defensive fallback branch."""
        (tmp_path / "frontend" / "dist").mkdir(parents=True)
        hosting = HostingConfig.model_construct(provider="carrier-pigeon")
        config = Config.model_construct(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=hosting,
            output_dir=tmp_path / "out",
            project_root=tmp_path,
        )

        with pytest.raises(ValueError, match="Unsupported hosting provider"):
            Orchestrator(config).deploy()


class TestDeployProviders:
    def test_cloudflare_missing_config_raises(self, tmp_path: Path) -> None:
        hosting = HostingConfig.model_construct(provider="cloudflare")
        # Config re-validates hosting on construction too, so bypass at this level
        # as well - this test is purely for Orchestrator's own defensive check.
        config = Config.model_construct(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=hosting,
            output_dir=tmp_path / "out",
            project_root=tmp_path,
        )
        orchestrator = Orchestrator(config)

        with pytest.raises(RuntimeError, match="Cloudflare config is missing"):
            orchestrator._deploy_cloudflare(tmp_path)

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_cloudflare_deploy_invokes_wrangler_with_the_project_name(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        hosting = HostingConfig(
            provider="cloudflare",
            cloudflare=CloudflareConfig(account_id="x", project_name="my-wrapped", api_token="tok"),
        )
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        orchestrator._deploy_cloudflare(tmp_path / "dist")

        args, kwargs = mock_run.call_args
        assert args[0] == [
            "npx",
            "wrangler",
            "pages",
            "deploy",
            str(tmp_path / "dist"),
            "--project-name",
            "my-wrapped",
        ]
        assert kwargs["env"]["CLOUDFLARE_API_TOKEN"] == "tok"

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_cloudflare_deploy_failure_raises_runtime_error(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["npx"])
        hosting = HostingConfig(
            provider="cloudflare",
            cloudflare=CloudflareConfig(account_id="x", project_name="y"),
        )
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with pytest.raises(RuntimeError, match="Cloudflare deployment failed"):
            orchestrator._deploy_cloudflare(tmp_path / "dist")

    def test_vercel_missing_config_raises(self, tmp_path: Path) -> None:
        hosting = HostingConfig.model_construct(provider="vercel")
        # Config re-validates hosting on construction too, so bypass at this level
        # as well - this test is purely for Orchestrator's own defensive check.
        config = Config.model_construct(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=hosting,
            output_dir=tmp_path / "out",
            project_root=tmp_path,
        )
        orchestrator = Orchestrator(config)

        with pytest.raises(RuntimeError, match="Vercel config is missing"):
            orchestrator._deploy_vercel(tmp_path)

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_vercel_deploy_invokes_vercel_cli(self, mock_run: MagicMock, tmp_path: Path) -> None:
        hosting = HostingConfig(
            provider="vercel", vercel=VercelConfig(project_name="y", token="tok")
        )
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        orchestrator._deploy_vercel(tmp_path / "dist")

        args, kwargs = mock_run.call_args
        assert args[0] == ["npx", "vercel", "deploy", str(tmp_path / "dist"), "--prod"]
        assert kwargs["env"]["VERCEL_TOKEN"] == "tok"

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_vercel_deploy_failure_raises_runtime_error(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["npx"])
        hosting = HostingConfig(provider="vercel", vercel=VercelConfig(project_name="y"))
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with pytest.raises(RuntimeError, match="Vercel deployment failed"):
            orchestrator._deploy_vercel(tmp_path / "dist")

    def test_netlify_missing_config_raises(self, tmp_path: Path) -> None:
        hosting = HostingConfig.model_construct(provider="netlify")
        # Config re-validates hosting on construction too, so bypass at this level
        # as well - this test is purely for Orchestrator's own defensive check.
        config = Config.model_construct(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=hosting,
            output_dir=tmp_path / "out",
            project_root=tmp_path,
        )
        orchestrator = Orchestrator(config)

        with pytest.raises(RuntimeError, match="Netlify config is missing"):
            orchestrator._deploy_netlify(tmp_path)

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_netlify_deploy_invokes_netlify_cli(self, mock_run: MagicMock, tmp_path: Path) -> None:
        hosting = HostingConfig(
            provider="netlify", netlify=NetlifyConfig(site_id="site-1", auth_token="tok")
        )
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        orchestrator._deploy_netlify(tmp_path / "dist")

        args, kwargs = mock_run.call_args
        assert args[0] == [
            "npx",
            "netlify",
            "deploy",
            "--prod",
            "--dir",
            str(tmp_path / "dist"),
            "--site",
            "site-1",
        ]
        assert kwargs["env"]["NETLIFY_AUTH_TOKEN"] == "tok"

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_netlify_deploy_failure_raises_runtime_error(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["npx"])
        hosting = HostingConfig(provider="netlify", netlify=NetlifyConfig(site_id="site-1"))
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with pytest.raises(RuntimeError, match="Netlify deployment failed"):
            orchestrator._deploy_netlify(tmp_path / "dist")

    def test_github_missing_config_raises(self, tmp_path: Path) -> None:
        hosting = HostingConfig.model_construct(provider="github")
        # Config re-validates hosting on construction too, so bypass at this level
        # as well - this test is purely for Orchestrator's own defensive check.
        config = Config.model_construct(
            plex=PlexConfig(url="https://test.com", token="test"),
            llm=LLMConfig(provider="none"),
            year=2024,
            hosting=hosting,
            output_dir=tmp_path / "out",
            project_root=tmp_path,
        )
        orchestrator = Orchestrator(config)

        with pytest.raises(RuntimeError, match="GitHub Pages config is missing"):
            orchestrator._deploy_github(tmp_path)

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_github_deploy_invokes_gh_pages_cli(self, mock_run: MagicMock, tmp_path: Path) -> None:
        hosting = HostingConfig(provider="github", github=GitHubPagesConfig(repo="me/repo"))
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        orchestrator._deploy_github(tmp_path / "dist")

        args, _ = mock_run.call_args
        assert args[0] == [
            "npx",
            "gh-pages",
            "--dist",
            str(tmp_path / "dist"),
            "--repo",
            "https://github.com/me/repo.git",
            "--branch",
            "gh-pages",
        ]

    @patch("plex_wrapped.orchestrator.subprocess.run")
    def test_github_deploy_failure_raises_runtime_error(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["npx"])
        hosting = HostingConfig(provider="github", github=GitHubPagesConfig(repo="me/repo"))
        orchestrator = make_orchestrator_with_hosting(tmp_path, hosting)

        with pytest.raises(RuntimeError, match="GitHub Pages deployment failed"):
            orchestrator._deploy_github(tmp_path / "dist")


class TestRunAll:
    def test_calls_every_stage_in_order_and_prints_success(self, tmp_path: Path) -> None:
        orchestrator = make_orchestrator(tmp_path, tmp_path / "out")
        calls: list[str] = []
        for stage in ("extract", "process", "build", "deploy"):
            setattr(orchestrator, stage, lambda stage=stage: calls.append(stage))

        orchestrator.run_all()

        assert calls == ["extract", "process", "build", "deploy"]

    def test_reraises_and_still_lets_the_failure_propagate(self, tmp_path: Path) -> None:
        orchestrator = make_orchestrator(tmp_path, tmp_path / "out")
        orchestrator.extract = lambda: (_ for _ in ()).throw(RuntimeError("boom"))

        with pytest.raises(RuntimeError, match="boom"):
            orchestrator.run_all()
