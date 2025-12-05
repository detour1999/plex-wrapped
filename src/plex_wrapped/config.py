# ABOUTME: Configuration loading and validation using Pydantic models.
# ABOUTME: Handles YAML parsing and validates all config settings for Plex, LLM, and hosting.

from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator


class PlexConfig(BaseModel):
    """Plex server connection configuration."""

    url: str = Field(..., description="Plex server URL (e.g., https://plex.example.com)")
    token: str = Field(..., description="Plex authentication token")


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["anthropic", "openai", "none"] = Field(
        ..., description="LLM provider to use for generating content"
    )
    api_key: Optional[str] = Field(
        None, description="API key for the LLM provider (not required if provider is 'none')"
    )
    model: Optional[str] = Field(None, description="Specific model to use (optional)")

    @model_validator(mode='after')
    def validate_api_key_required(self) -> 'LLMConfig':
        """Validate that api_key is provided when provider is not 'none'."""
        if self.provider != "none" and not self.api_key:
            raise ValueError(f"api_key is required when provider is '{self.provider}'")
        return self


class CloudflareConfig(BaseModel):
    """Cloudflare Pages deployment configuration."""

    account_id: str = Field(..., description="Cloudflare account ID")
    project_name: str = Field(..., description="Cloudflare Pages project name")
    api_token: Optional[str] = Field(None, description="Cloudflare API token (optional)")


class VercelConfig(BaseModel):
    """Vercel deployment configuration."""

    project_name: str = Field(..., description="Vercel project name")
    token: Optional[str] = Field(None, description="Vercel authentication token (optional)")


class NetlifyConfig(BaseModel):
    """Netlify deployment configuration."""

    site_id: str = Field(..., description="Netlify site ID")
    auth_token: Optional[str] = Field(None, description="Netlify authentication token (optional)")


class GitHubPagesConfig(BaseModel):
    """GitHub Pages deployment configuration."""

    repo: str = Field(..., description="GitHub repository (e.g., username/repo)")
    branch: str = Field(default="gh-pages", description="Branch to deploy to")


class HostingConfig(BaseModel):
    """Hosting provider configuration."""

    provider: Literal["cloudflare", "vercel", "netlify", "github", "none"] = Field(
        ..., description="Hosting provider for deployment"
    )
    cloudflare: Optional[CloudflareConfig] = Field(
        None, description="Cloudflare-specific configuration"
    )
    vercel: Optional[VercelConfig] = Field(None, description="Vercel-specific configuration")
    netlify: Optional[NetlifyConfig] = Field(None, description="Netlify-specific configuration")
    github: Optional[GitHubPagesConfig] = Field(
        None, description="GitHub Pages-specific configuration"
    )

    @model_validator(mode='after')
    def validate_provider_config_exists(self) -> 'HostingConfig':
        """Validate that provider-specific config matches the selected provider."""
        provider_map = {
            'cloudflare': self.cloudflare,
            'vercel': self.vercel,
            'netlify': self.netlify,
            'github': self.github,
        }
        if self.provider in provider_map and provider_map[self.provider] is None:
            raise ValueError(f"Missing config for hosting provider '{self.provider}'")
        return self


class Config(BaseModel):
    """Root configuration model."""

    plex: PlexConfig = Field(..., description="Plex server configuration")
    llm: LLMConfig = Field(..., description="LLM provider configuration")
    year: int = Field(..., description="Year to generate Wrapped for")
    hosting: HostingConfig = Field(..., description="Hosting provider configuration")
    output_dir: Path = Field(
        default=Path("dist"), description="Output directory for generated site"
    )
    project_root: Path = Field(
        default=Path("."), description="Project root directory containing frontend/"
    )


def load_config(config_path: Path) -> Config:
    """
    Load and validate configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Validated Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is invalid or config validation fails
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")

    if config_data is None:
        raise ValueError("Config file is empty")

    try:
        return Config(**config_data)
    except Exception as e:
        raise ValueError(f"Config validation failed: {e}")
