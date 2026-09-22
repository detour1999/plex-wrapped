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

## License

MIT
