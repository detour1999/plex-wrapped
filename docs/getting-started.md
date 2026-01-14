# Getting Started with Plex Wrapped

Complete guide to setting up and generating your Plex Wrapped experience.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.11 or higher** - Check with `python --version`
- **Node.js 18 or higher** - Check with `node --version`
- **Plex Media Server** - With a music library and listening history
- **Plex Token** - Follow [this guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) to find your token
- **(Optional) AI API Key** - Anthropic or OpenAI API key for AI-generated content

## Installation

### Install Plex Wrapped CLI

```bash
pip install git+https://github.com/detour1999/plex-wrapped.git
```

Verify installation:

```bash
plex-wrapped --help
```

### Install Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Configuration

### 1. Initialize Configuration

Create a new configuration file:

```bash
plex-wrapped init
```

This creates a `config.yaml` file in your current directory.

### 2. Configure Plex Connection

Edit `config.yaml` and add your Plex server details:

```yaml
plex:
  url: "https://plex.example.com"  # Your Plex server URL
  token: "your-plex-token-here"    # Your Plex authentication token
```

To find your Plex token:
1. Open Plex Web App
2. Play any media item
3. Click the three dots menu > "Get Info"
4. Click "View XML"
5. Look for `X-Plex-Token` in the URL

### 3. Configure AI Provider (Optional)

For AI-generated narratives, roasts, and recommendations:

```yaml
llm:
  provider: "anthropic"  # Options: anthropic, openai, none
  api_key: "sk-ant-xxx"  # Your API key
  model: "claude-sonnet-4-5-20250929"  # Optional: specific model
```

If you skip this, Plex Wrapped will still generate stats but without AI-enhanced content.

### 4. Set Target Year (Optional)

```yaml
year: 2024  # Year to generate Wrapped for (defaults to current year if not specified)
```

The year field is optional and defaults to the current year. You can also override the year at runtime with the `--year` flag (see below).

### 5. Configure Hosting (Optional)

Choose a hosting provider for deployment:

#### Cloudflare Pages

```yaml
hosting:
  provider: "cloudflare"
  cloudflare:
    account_id: "your-account-id"
    project_name: "my-wrapped"
    api_token: "your-api-token"
```

#### Vercel

```yaml
hosting:
  provider: "vercel"
  vercel:
    project_name: "my-wrapped"
    token: "your-vercel-token"
```

#### Netlify

```yaml
hosting:
  provider: "netlify"
  netlify:
    site_id: "your-site-id"
    auth_token: "your-netlify-token"
```

#### GitHub Pages

```yaml
hosting:
  provider: "github"
  github:
    repo: "username/repo"
    branch: "gh-pages"
```

#### Local Only

```yaml
hosting:
  provider: "none"
```

## Generate Workflow

### Option 1: All-in-One (Recommended)

Generate the complete Wrapped experience with a single command:

```bash
plex-wrapped generate
```

This will:
1. Extract listening history from Plex
2. Process data and generate insights
3. Generate AI content (if configured)
4. Build the frontend application
5. Deploy to hosting (if configured)

### Option 2: Step-by-Step

For more control, run each step individually:

```bash
# 1. Extract listening history from Plex
plex-wrapped extract

# 2. Process data and generate insights
plex-wrapped process

# 3. Build the frontend
plex-wrapped build

# 4. Deploy to hosting (optional)
plex-wrapped deploy
```

### Generating for Specific Years

You can generate Wrapped for any year using the `--year` flag, which overrides the year in your config file:

```bash
# Generate for 2023
plex-wrapped generate --year 2023

# Or use the short form
plex-wrapped generate -y 2023

# Works with individual commands too
plex-wrapped extract --year 2022
plex-wrapped process --year 2022
```

This is useful for:
- Generating historical Wrapped experiences without editing your config
- Running multiple years in sequence (2022, 2023, 2024, etc.)

## Local Preview

Preview the generated Wrapped site locally:

```bash
plex-wrapped preview
```

This starts a local server at `http://localhost:4321` where you can view the Wrapped experience before deploying.

## Hosting Options

### Cloudflare Pages

1. Create a Cloudflare Pages project
2. Get your Account ID from the Cloudflare dashboard
3. Create an API token with Pages permissions
4. Configure in `config.yaml` as shown above
5. Run `plex-wrapped deploy`

### Vercel

1. Install Vercel CLI: `npm install -g vercel`
2. Run `vercel login` to authenticate
3. Configure in `config.yaml`
4. Run `plex-wrapped deploy`

### Netlify

1. Install Netlify CLI: `npm install -g netlify-cli`
2. Run `netlify login` to authenticate
3. Get your Site ID from Site Settings > General > Site details
4. Configure in `config.yaml`
5. Run `plex-wrapped deploy`

### GitHub Pages

1. Create a repository on GitHub
2. Enable GitHub Pages in repository settings
3. Configure in `config.yaml`
4. Run `plex-wrapped deploy`

### Manual Deployment

Build the site and upload the `dist/` directory to any static hosting provider:

```bash
plex-wrapped build
# Upload contents of dist/ directory to your hosting
```

## Troubleshooting

### "Failed to connect to Plex server"

- Verify your Plex server URL is correct and accessible
- Check that your Plex token is valid
- Ensure your Plex server is running

### "No listening history found"

- Verify your Plex server has a music library
- Check that there is listening history for the configured year
- Ensure the Plex token has access to the music library

### "AI generation failed"

- Verify your API key is correct
- Check that you have sufficient API credits
- Ensure the model name is valid for your provider

### "Build failed"

- Make sure Node.js dependencies are installed: `cd frontend && npm install`
- Check that the frontend directory exists
- Verify Node.js version is 18 or higher

### "Deployment failed"

- Verify your hosting provider credentials are correct
- Check that the project name matches your hosting configuration
- Ensure you have permissions to deploy to the target

## Advanced Configuration

### Custom Output Directory

```yaml
output_dir: "custom-dist"
```

### Using Environment Variables

Instead of storing API keys in `config.yaml`, use environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-xxx"
export CLOUDFLARE_API_TOKEN="your-token"
```

Then in `config.yaml`, omit the keys - Plex Wrapped will use the environment variables.

### Custom Config File Location

```bash
plex-wrapped generate --config /path/to/custom-config.yaml
```

## Next Steps

- Customize the frontend design in `frontend/src/`
- Add custom slides or animations
- Set up automated yearly generation with cron jobs
- Share your Wrapped links with Plex server users

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the example configuration at `examples/config.example.yaml`
3. Open an issue on GitHub with details about your setup and error messages

## Example Configuration

See `examples/config.example.yaml` for a complete configuration template with all available options.
