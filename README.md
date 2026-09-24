# Plex Wrapped

> Self-hostable Spotify Wrapped for Plex servers

Generate beautiful, interactive year-end music recaps for everyone on your Plex server.

## Features

- **Rich Stats** - Top artists, albums, tracks, listening time, and more
- **Beautiful UI** - Spotify-style animated slides
- **AI-Powered** - Personalized narratives, roasts, and recommendations
- **Self-Hosted** - Your data stays on your server
- **Shareable** - Each user gets their own link

## Quick Start

```bash
# Clone the repository
git clone https://github.com/detour1999/plex-wrapped.git
cd plex-wrapped

# Install with uv (recommended)
uv venv && source .venv/bin/activate
uv pip install -e .

# Or with pip
# python3 -m venv .venv && source .venv/bin/activate
# pip install -e .

# Run interactive setup wizard
plex-wrapped

# Or generate directly with existing config
plex-wrapped generate
```

## Requirements

- Python 3.11+
- Node.js 18+
- Plex Media Server with music library
- (Optional) Anthropic or OpenAI API key for AI features

## Documentation

See [Getting Started](docs/getting-started.md) for detailed setup instructions.

## Development

This repo uses [pre-commit](https://pre-commit.com) to run lint, format, and test
checks (with a coverage floor) before each commit - see `.pre-commit-config.yaml`.
If `pre-commit` isn't already wired into your `git commit` (it needs to be either
installed via `pre-commit install` or picked up by an existing global hooks setup),
run the checks manually with:

```bash
uv run pre-commit run --all-files
```

Python checks run via `uv run ruff format --check`, `uv run ruff check`, and
`uv run pytest --cov` (fails under 90% coverage - see `[tool.coverage.report]` in
`pyproject.toml`). Frontend checks run `npm run test:coverage` inside `frontend/`
whenever a `frontend/` file changes.

## License

MIT
