# ABOUTME: Tests for configuration loading and validation.
# ABOUTME: Verifies YAML parsing and Pydantic model validation.

import pytest
from pathlib import Path
import tempfile
import yaml

from last_wrapped.config import load_config, Config, PlexConfig, LLMConfig, HostingConfig


class TestConfigLoading:
    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Config loads and validates from YAML file."""
        config_data = {
            "plex": {
                "url": "https://plex.example.com",
                "token": "test-token-123",
            },
            "llm": {
                "provider": "anthropic",
                "api_key": "sk-test-key",
            },
            "year": 2024,
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {
                    "account_id": "abc123",
                    "project_name": "my-wrapped",
                },
            },
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)

        assert config.plex.url == "https://plex.example.com"
        assert config.plex.token == "test-token-123"
        assert config.llm.provider == "anthropic"
        assert config.year == 2024
        assert config.hosting.provider == "cloudflare"

    def test_load_missing_file_raises(self) -> None:
        """Loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Loading invalid YAML raises ValueError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_config(config_file)

    def test_load_missing_required_field_raises(self, tmp_path: Path) -> None:
        """Missing required field raises ValidationError."""
        config_data = {
            "plex": {
                "url": "https://plex.example.com",
                # missing token
            },
            "year": 2024,
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValueError, match="token"):
            load_config(config_file)


class TestLLMConfig:
    def test_llm_provider_none_skips_api_key(self, tmp_path: Path) -> None:
        """Provider 'none' doesn't require api_key."""
        config_data = {
            "plex": {"url": "https://plex.example.com", "token": "test"},
            "llm": {"provider": "none"},
            "year": 2024,
            "hosting": {"provider": "cloudflare", "cloudflare": {"account_id": "x", "project_name": "y"}},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)
        assert config.llm.provider == "none"
        assert config.llm.api_key is None

    def test_llm_requires_api_key_for_anthropic(self, tmp_path: Path) -> None:
        """Provider 'anthropic' requires api_key."""
        config_data = {
            "plex": {"url": "https://plex.example.com", "token": "test"},
            "llm": {"provider": "anthropic"},  # Missing api_key!
            "year": 2024,
            "hosting": {"provider": "cloudflare", "cloudflare": {"account_id": "x", "project_name": "y"}},
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValueError, match="api_key"):
            load_config(config_file)


class TestHostingConfig:
    def test_hosting_requires_provider_config(self, tmp_path: Path) -> None:
        """Hosting provider 'cloudflare' requires cloudflare config."""
        config_data = {
            "plex": {"url": "https://plex.example.com", "token": "test"},
            "llm": {"provider": "none"},
            "year": 2024,
            "hosting": {"provider": "cloudflare"},  # Missing cloudflare config!
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValueError, match="cloudflare"):
            load_config(config_file)
