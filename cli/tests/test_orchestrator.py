# ABOUTME: Tests for CLI orchestration.
# ABOUTME: Verifies end-to-end workflow from extract to deploy.

import pytest
from pathlib import Path

from last_wrapped.orchestrator import Orchestrator
from last_wrapped.config import Config, PlexConfig, LLMConfig, HostingConfig, CloudflareConfig


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
