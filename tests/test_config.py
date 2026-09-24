# ABOUTME: Tests for configuration loading and validation.
# ABOUTME: Verifies YAML parsing and Pydantic model validation.

import pytest
from pathlib import Path
import yaml

from plex_wrapped.config import load_config


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

    def test_load_empty_file_raises(self, tmp_path: Path) -> None:
        """An empty (or all-comments) YAML file raises a clear error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("# just a comment, no data\n")

        with pytest.raises(ValueError, match="empty"):
            load_config(config_file)

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
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {"account_id": "x", "project_name": "y"},
            },
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
            "hosting": {
                "provider": "cloudflare",
                "cloudflare": {"account_id": "x", "project_name": "y"},
            },
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


class TestEnvironmentVariableFallbacks:
    """Sensitive credentials omitted from the YAML fall back to environment variables."""

    def _write_config(
        self, tmp_path: Path, hosting: dict, llm: dict, plex_token: str | None = "inline-token"
    ) -> Path:
        config_data = {
            "plex": {
                "url": "https://plex.example.com",
                **({"token": plex_token} if plex_token else {}),
            },
            "llm": llm,
            "year": 2024,
            "hosting": hosting,
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))
        return config_file

    def test_plex_token_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("PLEX_TOKEN", "env-plex-token")
        config_file = self._write_config(
            tmp_path, {"provider": "none"}, {"provider": "none"}, plex_token=None
        )

        config = load_config(config_file)

        assert config.plex.token == "env-plex-token"

    def test_anthropic_api_key_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "env-anthropic-key")
        config_file = self._write_config(tmp_path, {"provider": "none"}, {"provider": "anthropic"})

        config = load_config(config_file)

        assert config.llm.api_key == "env-anthropic-key"

    def test_openai_api_key_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")
        config_file = self._write_config(tmp_path, {"provider": "none"}, {"provider": "openai"})

        config = load_config(config_file)

        assert config.llm.api_key == "env-openai-key"

    def test_cloudflare_api_token_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "env-cf-token")
        hosting = {"provider": "cloudflare", "cloudflare": {"account_id": "x", "project_name": "y"}}
        config_file = self._write_config(tmp_path, hosting, {"provider": "none"})

        config = load_config(config_file)

        assert config.hosting.cloudflare.api_token == "env-cf-token"

    def test_vercel_token_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("VERCEL_TOKEN", "env-vercel-token")
        hosting = {"provider": "vercel", "vercel": {"project_name": "y"}}
        config_file = self._write_config(tmp_path, hosting, {"provider": "none"})

        config = load_config(config_file)

        assert config.hosting.vercel.token == "env-vercel-token"

    def test_netlify_auth_token_falls_back_to_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("NETLIFY_AUTH_TOKEN", "env-netlify-token")
        hosting = {"provider": "netlify", "netlify": {"site_id": "y"}}
        config_file = self._write_config(tmp_path, hosting, {"provider": "none"})

        config = load_config(config_file)

        assert config.hosting.netlify.auth_token == "env-netlify-token"
