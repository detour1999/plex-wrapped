# Dynamic Theming System Design

## Overview

LLM-driven visual theming with ambient animated backgrounds that vary per slide based on user's listening personality.

## Data Structure

The LLM outputs a `theme` object in processed data:

```json
{
  "theme": {
    "palette": {
      "primary": "#F39C12",
      "secondary": "#8E44AD",
      "accent": "#E74C3C",
      "background": "#1a1a2e",
      "text": "#ffffff"
    },
    "slides": {
      "intro": { "visualization": "aurora", "mood": "dramatic", "intensity": 0.8 },
      "totalTime": { "visualization": "particles", "mood": "celebratory", "intensity": 0.6 },
      "topArtist": { "visualization": "gradient_blob", "mood": "warm", "intensity": 0.7 },
      "topTracks": { "visualization": "gradient_mesh", "mood": "energetic", "intensity": 0.5 },
      "listeningClock": { "visualization": "radial_burst", "mood": "analytical", "intensity": 0.4 },
      "quirkyStats": { "visualization": "falling_blocks", "mood": "playful", "intensity": 0.6 },
      "personality": { "visualization": "gradient_blob", "mood": "introspective", "intensity": 0.7 },
      "aura": { "visualization": "aurora", "mood": "mystical", "intensity": 0.9 },
      "roasts": { "visualization": "gradient_mesh", "mood": "chaotic", "intensity": 0.8 },
      "narrative": { "visualization": "particles", "mood": "reflective", "intensity": 0.3 },
      "share": { "visualization": "gradient_blob", "mood": "triumphant", "intensity": 0.7 }
    }
  }
}
```

## Frontend Architecture

### Component Hierarchy

```
WrappedExperience.svelte
├── VisualizationBackground.svelte (fixed, z-index: 0, full viewport)
│   └── <canvas> WebGL context
└── Current Slide (z-index: 1, content on top)
```

### Visualization Registry

Each renderer implements a common interface:

```typescript
interface VisualizationRenderer {
  init(gl: WebGLRenderingContext, palette: Palette): void;
  update(deltaTime: number, mood: string, intensity: number): void;
  transition(fromConfig: SlideConfig, toConfig: SlideConfig, progress: number): void;
  destroy(): void;
}
```

### Available Visualizations

| ID | Name | Description | Best For |
|----|------|-------------|----------|
| `gradient_blob` | Gradient Blob | Soft circles with gaussian blur, slowly drifting | warm, introspective |
| `gradient_mesh` | Gradient Mesh | Voronoi-like color cells with smooth interpolation | energetic, structured |
| `aurora` | Aurora | Horizontal noise bands with wave displacement | dramatic, mystical |
| `particles` | Particles | Floating dots with drift and twinkle | celebratory, reflective |
| `radial_burst` | Radial Burst | Rays from center with pulsing intensity | analytical, reveals |
| `waves` | Waves | Stacked sine waves like sound visualizer | musical, rhythmic |
| `falling_blocks` | Falling Blocks | Geometric shapes cascading and stacking | playful, nostalgic |

### Mood to Color Mapping

- `dramatic/mystical` - darker, more contrast
- `warm/introspective` - primary + secondary blend
- `energetic/chaotic` - all colors, higher saturation
- `celebratory/triumphant` - accent-heavy, bright
- `reflective/analytical` - muted, subtle

## File Structure

```
frontend/src/lib/visualizations/
├── index.ts              # Registry + types
├── base.ts               # Shared WebGL utilities
├── gradient_blob.ts
├── gradient_mesh.ts
├── aurora.ts
├── particles.ts
├── radial_burst.ts
├── waves.ts
└── falling_blocks.ts
```

## Self-Documenting Visualizations

Each renderer exports metadata for LLM prompt generation:

```typescript
export const metadata: VisualizationMetadata = {
  id: 'falling_blocks',
  name: 'Falling Blocks',
  description: 'Geometric shapes cascading and stacking like a puzzle game',
  bestFor: ['playful', 'nostalgic', 'quirky'],
};
```

At frontend build time, a `manifest.json` is generated:

```json
{
  "visualizations": [
    {"id": "falling_blocks", "name": "Falling Blocks", "bestFor": ["playful", "nostalgic"]},
    {"id": "aurora", "name": "Aurora", "bestFor": ["dramatic", "mystical"]}
  ]
}
```

The CLI reads this manifest and injects it into the LLM prompt automatically.

## Adding New Visualizations

1. Create renderer file with metadata in `frontend/src/lib/visualizations/`
2. Register in `index.ts`
3. Rebuild frontend (generates manifest)
4. LLM automatically discovers new visualization

## Performance Considerations

- RequestAnimationFrame with delta timing
- Reduce intensity on low-power devices (`navigator.hardwareConcurrency`)
- Pause rendering when tab not visible
- Smooth crossfade transitions between slides

## Backend Changes

- New `theme` generator in `cli/src/last_wrapped/generators/theme.py`
- Reads visualization manifest from frontend
- Generates theme based on user's listening data and personality
