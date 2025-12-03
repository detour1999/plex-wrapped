# Last Wrapped - Design Document

## Overview

A self-hostable "Spotify Wrapped" experience for Plex server administrators. Each user on a Plex server gets their own shareable, interactive year-end music recap.

## Goals

- **Per-user Wrapped reports** - Each Plex user gets their own personalized recap
- **Shareable interactive web experience** - Spotify-style animated slides
- **Year-end only** - Classic Wrapped timing (December, full year coverage)
- **Self-hostable** - Plex admins run for their own servers, deploy to their own hosting
- **Configurable** - Plex server, LLM provider, and hosting all configurable

## Key Features

### Core Metrics
- Top artists, albums, and tracks with play counts and rankings
- Listening time stats (total minutes, peak hours/days, streaks)
- Genre/mood analysis and evolution through the year
- Discovery metrics (new artists found, new vs. familiar ratio)

### Creative/Fun Elements
- **Listening personality** - Whimsical type with tagline and spirit animal
- **Audio aura** - Visual colors/gradients based on mood + vibe description
- **Quirky patterns** - "Your 2am anthem", "Monday motivator", etc.
- **Roasts** - Playful callouts about listening habits
- **Superlatives & awards** - "Most Likely to...", certificates
- **AI narrative** - Personalized story about the year in music
- **Hot takes** - Humorous observations about taste
- **Suggestions** - Recommendations and challenges for next year

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│           LAST WRAPPED (Self-Hosted by Plex Admins)             │
└─────────────────────────────────────────────────────────────────┘

  Admin runs yearly:
   ┌──────────┐      ┌─────────────────┐      ┌──────────────────┐
   │  Plex    │ ───▶ │   Python CLI    │ ───▶ │   JSON + Assets  │
   │  Server  │      │  (configurable) │      │   (per user)     │
   └──────────┘      └─────────────────┘      └──────────────────┘
                              │                        │
                     ┌────────┴────────┐               │
                     ▼                 ▼               ▼
            ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
            │ Claude API   │  │ OpenAI API   │  │ Astro Build │
            │ (optional)   │  │ (optional)   │  │             │
            └──────────────┘  └──────────────┘  └─────────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Admin's Hosting │
                                              │ (CF/Vercel/etc.) │
                                              └──────────────────┘
```

## Configuration

```yaml
# config.yaml
plex:
  url: "https://plex.myserver.com"
  token: "xxxx"

llm:
  provider: "anthropic"  # or "openai" or "none"
  api_key: "sk-..."

year: 2024

hosting:
  provider: "cloudflare"  # or "vercel", "netlify", "github-pages"
  cloudflare:
    account_id: "xxxx"
    project_name: "my-wrapped"
  # OR vercel/netlify/github_pages specific config
```

## URL Structure

User-centric with history:
```
yoursite.com/
├── /                     # Landing: list of users
├── /dylan/               # User landing: all years
│   ├── /dylan/2024/      # Dylan's 2024 Wrapped
│   └── /dylan/2025/      # Dylan's 2025 Wrapped
├── /roommate/
│   └── /roommate/2024/
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| CLI | Python 3.11+, Typer, plexapi, pydantic |
| AI | anthropic/openai SDKs (configurable) |
| Frontend | Astro 4, Svelte 5, TailwindCSS |
| Animations | Svelte transitions + CSS |
| Hosting | Cloudflare Pages / Vercel / Netlify / GH Pages |

## Repository Structure

```
last-wrapped/
├── cli/                    # Python CLI (pip installable)
│   ├── pyproject.toml
│   └── src/last_wrapped/
│       ├── __init__.py
│       ├── main.py              # CLI entry point (Typer)
│       ├── config.py            # Config loading/validation
│       ├── extractors/
│       │   └── plex.py          # Plex API data extraction
│       ├── processors/
│       │   ├── stats.py         # Top tracks, artists, albums
│       │   ├── time_analysis.py # Listening time, patterns, streaks
│       │   ├── genres.py        # Genre/mood analysis
│       │   └── discovery.py     # New vs familiar artists
│       ├── ai/
│       │   ├── provider.py      # Abstract LLM interface
│       │   ├── anthropic.py     # Claude implementation
│       │   ├── openai.py        # OpenAI implementation
│       │   ├── narrative.py     # Year story generation
│       │   ├── personality.py   # Listening personality type
│       │   └── suggestions.py   # Next year recommendations
│       ├── builders/
│       │   └── astro.py         # Triggers Astro build
│       └── deployers/
│           ├── cloudflare.py
│           ├── vercel.py
│           ├── netlify.py
│           └── github_pages.py
├── frontend/               # Astro + Svelte
│   ├── package.json
│   ├── astro.config.mjs
│   └── src/
│       ├── layouts/
│       │   └── WrappedLayout.astro
│       ├── components/
│       │   ├── slides/
│       │   │   ├── Intro.svelte
│       │   │   ├── TotalTime.svelte
│       │   │   ├── TopArtist.svelte
│       │   │   ├── TopTracks.svelte
│       │   │   ├── ListeningClock.svelte
│       │   │   ├── QuirkyStats.svelte
│       │   │   ├── GenreBreakdown.svelte
│       │   │   ├── Discovery.svelte
│       │   │   ├── Personality.svelte
│       │   │   ├── Aura.svelte
│       │   │   ├── Superlatives.svelte
│       │   │   ├── Narrative.svelte
│       │   │   ├── NextYear.svelte
│       │   │   └── Share.svelte
│       │   └── common/
│       │       ├── SlideContainer.svelte
│       │       ├── AnimatedNumber.svelte
│       │       └── ProgressDots.svelte
│       ├── pages/
│       │   ├── index.astro              # Server landing
│       │   ├── [user]/
│       │   │   ├── index.astro          # User's year list
│       │   │   └── [year]/
│       │   │       └── index.astro      # The Wrapped experience
│       └── data/
│           └── *.json                   # Generated user data
├── docs/
│   └── getting-started.md
├── examples/
│   └── config.example.yaml
└── README.md
```

## Data Schema (Per User JSON)

```json
{
  "user": {
    "name": "Dylan",
    "avatar_url": "https://plex.tv/...",
    "year": 2024
  },
  "stats": {
    "total_minutes": 42380,
    "total_tracks": 8420,
    "unique_artists": 312,
    "unique_albums": 589,
    "peak_day": "2024-03-15",
    "peak_day_minutes": 480,
    "longest_streak_days": 47
  },
  "top": {
    "artists": [
      {"name": "Artist Name", "plays": 245, "minutes": 892, "image_url": "..."}
    ],
    "albums": [],
    "tracks": []
  },
  "time_patterns": {
    "by_hour": [],
    "by_day_of_week": [],
    "by_month": [],
    "quirky": {
      "late_night_anthem": {"track": "...", "plays_after_midnight": 23},
      "monday_motivator": {"track": "...", "monday_plays": 18},
      "most_repeated_day": {"track": "...", "date": "2024-06-12", "plays": 14}
    }
  },
  "genres": {
    "top_genres": [{"name": "Indie Rock", "percentage": 34}],
    "monthly_evolution": {}
  },
  "discovery": {
    "new_artists_count": 89,
    "new_vs_familiar_ratio": 0.28,
    "biggest_discovery": {"artist": "...", "first_listen": "2024-02-14", "total_plays": 67}
  },
  "ai_generated": {
    "narrative": "Your 2024 started with a breakup playlist...",
    "personality": {
      "type": "The Chaotic Archivist",
      "tagline": "You have 47 playlists and commitment issues",
      "description": "You don't have a type—you have a rotating cast...",
      "spirit_animal": "A raccoon in a record store at 2am"
    },
    "aura": {
      "colors": ["#4A90D9", "#7B68EE", "#FF6B6B"],
      "vibe": "Main character energy with a hint of existential dread",
      "aesthetic": "Coffee shop that plays vinyl but also has WiFi"
    },
    "roasts": [
      "You listened to 'Running Up That Hill' 84 times. Stranger Things ended in 2022, bestie.",
      "Your most-played hour is 2am. Everything okay at home?"
    ],
    "superlatives": {
      "title": "Most Likely to Cry in the Car",
      "award": "Golden Headphones for Emotional Damage",
      "certificate": "Certified Hood Classic Enthusiast"
    },
    "hot_takes": [
      "Your music taste is 60% impeccable, 40% unhinged",
      "You're one bad day away from a full folk phase"
    ],
    "suggestions": {
      "artists": [],
      "challenge": "In 2025, try listening to ONE album all the way through."
    }
  }
}
```

## CLI Workflow

```bash
# Install
pip install last-wrapped
# or: uvx last-wrapped

# Initialize config (first time)
last-wrapped init

# Generate everything (one command)
last-wrapped generate

# Or step-by-step:
last-wrapped extract   # Pull Plex data
last-wrapped process   # Crunch stats + AI
last-wrapped build     # Generate static site
last-wrapped deploy    # Push to hosting
last-wrapped preview   # Local preview before deploy
```

## Slide Sequence

1. **Intro** - "Your 2024 Wrapped is ready"
2. **TotalTime** - Big animated number reveal
3. **TopArtist** - Artist reveal with album art
4. **TopTracks** - Countdown style (5→1)
5. **ListeningClock** - Radial chart of hours
6. **QuirkyStats** - "Your 2am anthem was..."
7. **GenreBreakdown** - Animated pie/bar
8. **Discovery** - New artists found
9. **Personality** - Type reveal + roasts
10. **Aura** - Gradient background + vibe
11. **Superlatives** - Awards ceremony style
12. **Narrative** - AI story, typewriter effect
13. **NextYear** - Suggestions + challenge
14. **Share** - Share buttons + screenshot

## Interactions

- Tap/click or swipe to advance slides
- Each slide has entrance animation (fade, scale, count-up)
- Progress dots at bottom
- Share button generates screenshot of current slide

## Dependencies

### Python CLI
- `plexapi` - Official Plex Python library
- `typer` - Modern CLI framework
- `pydantic` - Config validation
- `anthropic` / `openai` - LLM clients
- `rich` - Pretty CLI output

### Frontend
- `astro` - Static site framework
- `svelte` - Interactive components
- `tailwindcss` - Styling
