# Dynamic Theming Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add LLM-driven visual theming with WebGL animated backgrounds that vary per slide based on user's listening personality.

**Architecture:** CLI generates a `theme` object with palette and per-slide visualization configs. Frontend has a WebGL-based `VisualizationBackground` component that renders behind slides and transitions between visualization types. Visualizations are self-documenting via a manifest that the CLI reads to inform the LLM.

**Tech Stack:** Python (CLI), TypeScript/Svelte (frontend), WebGL (visualizations)

---

## Task 1: Create Visualization Types and Registry

**Files:**
- Create: `frontend/src/lib/visualizations/types.ts`

**Step 1: Write the types file**

```typescript
// ABOUTME: Type definitions for visualization system.
// ABOUTME: Defines renderer interface and metadata structure.

export interface Palette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
}

export interface SlideConfig {
  visualization: string;
  mood: string;
  intensity: number;
}

export interface ThemeData {
  palette: Palette;
  slides: Record<string, SlideConfig>;
}

export interface VisualizationMetadata {
  id: string;
  name: string;
  description: string;
  bestFor: string[];
}

export interface VisualizationRenderer {
  init(gl: WebGLRenderingContext, palette: Palette): void;
  update(deltaTime: number, mood: string, intensity: number): void;
  transition(toConfig: SlideConfig, progress: number): void;
  destroy(): void;
}
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/types.ts
git commit -m "feat: add visualization type definitions"
```

---

## Task 2: Create Base WebGL Utilities

**Files:**
- Create: `frontend/src/lib/visualizations/base.ts`

**Step 1: Write the base utilities**

```typescript
// ABOUTME: Shared WebGL utilities for visualization renderers.
// ABOUTME: Provides shader compilation and common helpers.

export function createShader(
  gl: WebGLRenderingContext,
  type: number,
  source: string
): WebGLShader | null {
  const shader = gl.createShader(type);
  if (!shader) return null;

  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error('Shader compile error:', gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }

  return shader;
}

export function createProgram(
  gl: WebGLRenderingContext,
  vertexShader: WebGLShader,
  fragmentShader: WebGLShader
): WebGLProgram | null {
  const program = gl.createProgram();
  if (!program) return null;

  gl.attachShader(program, vertexShader);
  gl.attachShader(program, fragmentShader);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error('Program link error:', gl.getProgramInfoLog(program));
    gl.deleteProgram(program);
    return null;
  }

  return program;
}

export function hexToRgb(hex: string): [number, number, number] {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [0, 0, 0];
  return [
    parseInt(result[1], 16) / 255,
    parseInt(result[2], 16) / 255,
    parseInt(result[3], 16) / 255,
  ];
}

export const FULLSCREEN_QUAD_VERTICES = new Float32Array([
  -1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1,
]);

export const DEFAULT_VERTEX_SHADER = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`;
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/base.ts
git commit -m "feat: add WebGL base utilities"
```

---

## Task 3: Create Gradient Blob Renderer

**Files:**
- Create: `frontend/src/lib/visualizations/gradient_blob.ts`

**Step 1: Write the gradient blob renderer**

```typescript
// ABOUTME: Gradient blob visualization renderer.
// ABOUTME: Soft circles with gaussian blur that slowly drift and morph.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'gradient_blob',
  name: 'Gradient Blob',
  description: 'Soft circles with gaussian blur that slowly drift and morph like a lava lamp',
  bestFor: ['warm', 'introspective', 'calm', 'reflective'],
};

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform float u_intensity;
  uniform vec3 u_color1;
  uniform vec3 u_color2;
  uniform vec3 u_color3;
  uniform vec3 u_bg;

  float blob(vec2 uv, vec2 center, float radius) {
    float d = length(uv - center);
    return smoothstep(radius, radius * 0.3, d);
  }

  void main() {
    vec2 uv = v_uv;
    float t = u_time * 0.1 * u_intensity;

    vec2 c1 = vec2(0.3 + sin(t * 0.7) * 0.2, 0.4 + cos(t * 0.5) * 0.2);
    vec2 c2 = vec2(0.7 + cos(t * 0.6) * 0.2, 0.6 + sin(t * 0.8) * 0.2);
    vec2 c3 = vec2(0.5 + sin(t * 0.9) * 0.2, 0.3 + cos(t * 0.4) * 0.2);

    float b1 = blob(uv, c1, 0.4);
    float b2 = blob(uv, c2, 0.35);
    float b3 = blob(uv, c3, 0.3);

    vec3 color = u_bg;
    color = mix(color, u_color1, b1 * 0.6);
    color = mix(color, u_color2, b2 * 0.5);
    color = mix(color, u_color3, b3 * 0.4);

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const GradientBlobRenderer: VisualizationRenderer = {
  gl: null as WebGLRenderingContext | null,
  program: null as WebGLProgram | null,
  buffer: null as WebGLBuffer | null,
  startTime: 0,
  palette: null as Palette | null,
  currentIntensity: 0.5,

  init(gl: WebGLRenderingContext, palette: Palette) {
    this.gl = gl;
    this.palette = palette;
    this.startTime = performance.now();

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, DEFAULT_VERTEX_SHADER);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
    if (!vertexShader || !fragmentShader) return;

    this.program = createProgram(gl, vertexShader, fragmentShader);
    if (!this.program) return;

    this.buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.bufferData(gl.ARRAY_BUFFER, FULLSCREEN_QUAD_VERTICES, gl.STATIC_DRAW);
  },

  update(deltaTime: number, mood: string, intensity: number) {
    const gl = this.gl;
    const program = this.program;
    if (!gl || !program || !this.palette) return;

    this.currentIntensity = intensity;
    const time = (performance.now() - this.startTime) / 1000;

    gl.useProgram(program);

    const posLoc = gl.getAttribLocation(program, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    gl.uniform1f(gl.getUniformLocation(program, 'u_time'), time);
    gl.uniform1f(gl.getUniformLocation(program, 'u_intensity'), intensity);
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color1'), hexToRgb(this.palette.primary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color2'), hexToRgb(this.palette.secondary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color3'), hexToRgb(this.palette.accent));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_bg'), hexToRgb(this.palette.background));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  },

  transition(toConfig: SlideConfig, progress: number) {
    this.currentIntensity = toConfig.intensity;
  },

  destroy() {
    if (this.gl && this.program) {
      this.gl.deleteProgram(this.program);
    }
    if (this.gl && this.buffer) {
      this.gl.deleteBuffer(this.buffer);
    }
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null; currentIntensity: number };
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/gradient_blob.ts
git commit -m "feat: add gradient blob visualization renderer"
```

---

## Task 4: Create Particles Renderer

**Files:**
- Create: `frontend/src/lib/visualizations/particles.ts`

**Step 1: Write the particles renderer**

```typescript
// ABOUTME: Particles visualization renderer.
// ABOUTME: Floating dots with subtle drift and twinkle effect.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'particles',
  name: 'Particles',
  description: 'Floating dots with subtle drift and twinkle like stars',
  bestFor: ['celebratory', 'reflective', 'dreamy', 'peaceful'],
};

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform float u_intensity;
  uniform vec3 u_color1;
  uniform vec3 u_color2;
  uniform vec3 u_bg;

  float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
  }

  void main() {
    vec2 uv = v_uv;
    vec3 color = u_bg;
    float t = u_time * 0.05 * u_intensity;

    for (int i = 0; i < 50; i++) {
      float fi = float(i);
      vec2 pos = vec2(
        fract(random(vec2(fi, 0.0)) + t * (0.02 + random(vec2(fi, 1.0)) * 0.03)),
        fract(random(vec2(fi, 2.0)) + t * (0.01 + random(vec2(fi, 3.0)) * 0.02))
      );

      float size = 0.003 + random(vec2(fi, 4.0)) * 0.005;
      float d = length(uv - pos);
      float brightness = smoothstep(size, size * 0.3, d);
      brightness *= 0.5 + 0.5 * sin(t * 2.0 + fi);

      vec3 particleColor = mix(u_color1, u_color2, random(vec2(fi, 5.0)));
      color = mix(color, particleColor, brightness * 0.8);
    }

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const ParticlesRenderer: VisualizationRenderer = {
  gl: null as WebGLRenderingContext | null,
  program: null as WebGLProgram | null,
  buffer: null as WebGLBuffer | null,
  startTime: 0,
  palette: null as Palette | null,

  init(gl: WebGLRenderingContext, palette: Palette) {
    this.gl = gl;
    this.palette = palette;
    this.startTime = performance.now();

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, DEFAULT_VERTEX_SHADER);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
    if (!vertexShader || !fragmentShader) return;

    this.program = createProgram(gl, vertexShader, fragmentShader);
    if (!this.program) return;

    this.buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.bufferData(gl.ARRAY_BUFFER, FULLSCREEN_QUAD_VERTICES, gl.STATIC_DRAW);
  },

  update(deltaTime: number, mood: string, intensity: number) {
    const gl = this.gl;
    const program = this.program;
    if (!gl || !program || !this.palette) return;

    const time = (performance.now() - this.startTime) / 1000;

    gl.useProgram(program);

    const posLoc = gl.getAttribLocation(program, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    gl.uniform1f(gl.getUniformLocation(program, 'u_time'), time);
    gl.uniform1f(gl.getUniformLocation(program, 'u_intensity'), intensity);
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color1'), hexToRgb(this.palette.primary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color2'), hexToRgb(this.palette.accent));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_bg'), hexToRgb(this.palette.background));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  },

  transition(toConfig: SlideConfig, progress: number) {},

  destroy() {
    if (this.gl && this.program) this.gl.deleteProgram(this.program);
    if (this.gl && this.buffer) this.gl.deleteBuffer(this.buffer);
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null };
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/particles.ts
git commit -m "feat: add particles visualization renderer"
```

---

## Task 5: Create Aurora Renderer

**Files:**
- Create: `frontend/src/lib/visualizations/aurora.ts`

**Step 1: Write the aurora renderer**

```typescript
// ABOUTME: Aurora visualization renderer.
// ABOUTME: Flowing horizontal bands with wave displacement like northern lights.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'aurora',
  name: 'Aurora',
  description: 'Flowing ribbons of color like northern lights',
  bestFor: ['dramatic', 'mystical', 'epic', 'transformative'],
};

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform float u_intensity;
  uniform vec3 u_color1;
  uniform vec3 u_color2;
  uniform vec3 u_color3;
  uniform vec3 u_bg;

  void main() {
    vec2 uv = v_uv;
    float t = u_time * 0.2 * u_intensity;

    float wave1 = sin(uv.x * 3.0 + t) * 0.1 + sin(uv.x * 7.0 - t * 0.5) * 0.05;
    float wave2 = sin(uv.x * 4.0 - t * 0.7) * 0.08 + sin(uv.x * 9.0 + t * 0.3) * 0.04;
    float wave3 = sin(uv.x * 5.0 + t * 0.4) * 0.07 + sin(uv.x * 11.0 - t * 0.6) * 0.03;

    float band1 = smoothstep(0.1, 0.0, abs(uv.y - 0.7 - wave1));
    float band2 = smoothstep(0.15, 0.0, abs(uv.y - 0.5 - wave2));
    float band3 = smoothstep(0.12, 0.0, abs(uv.y - 0.3 - wave3));

    vec3 color = u_bg;
    color = mix(color, u_color1, band1 * 0.7);
    color = mix(color, u_color2, band2 * 0.6);
    color = mix(color, u_color3, band3 * 0.5);

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const AuroraRenderer: VisualizationRenderer = {
  gl: null as WebGLRenderingContext | null,
  program: null as WebGLProgram | null,
  buffer: null as WebGLBuffer | null,
  startTime: 0,
  palette: null as Palette | null,

  init(gl: WebGLRenderingContext, palette: Palette) {
    this.gl = gl;
    this.palette = palette;
    this.startTime = performance.now();

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, DEFAULT_VERTEX_SHADER);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
    if (!vertexShader || !fragmentShader) return;

    this.program = createProgram(gl, vertexShader, fragmentShader);
    if (!this.program) return;

    this.buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.bufferData(gl.ARRAY_BUFFER, FULLSCREEN_QUAD_VERTICES, gl.STATIC_DRAW);
  },

  update(deltaTime: number, mood: string, intensity: number) {
    const gl = this.gl;
    const program = this.program;
    if (!gl || !program || !this.palette) return;

    const time = (performance.now() - this.startTime) / 1000;

    gl.useProgram(program);

    const posLoc = gl.getAttribLocation(program, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    gl.uniform1f(gl.getUniformLocation(program, 'u_time'), time);
    gl.uniform1f(gl.getUniformLocation(program, 'u_intensity'), intensity);
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color1'), hexToRgb(this.palette.primary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color2'), hexToRgb(this.palette.secondary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color3'), hexToRgb(this.palette.accent));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_bg'), hexToRgb(this.palette.background));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  },

  transition(toConfig: SlideConfig, progress: number) {},

  destroy() {
    if (this.gl && this.program) this.gl.deleteProgram(this.program);
    if (this.gl && this.buffer) this.gl.deleteBuffer(this.buffer);
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null };
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/aurora.ts
git commit -m "feat: add aurora visualization renderer"
```

---

## Task 6: Create Visualization Registry

**Files:**
- Create: `frontend/src/lib/visualizations/index.ts`

**Step 1: Write the registry**

```typescript
// ABOUTME: Visualization registry and exports.
// ABOUTME: Central hub for all visualization renderers and metadata.

export * from './types';
export * from './base';

import { GradientBlobRenderer, metadata as gradientBlobMeta } from './gradient_blob';
import { ParticlesRenderer, metadata as particlesMeta } from './particles';
import { AuroraRenderer, metadata as auroraMeta } from './aurora';
import type { VisualizationRenderer, VisualizationMetadata } from './types';

export const visualizations: Record<string, VisualizationRenderer> = {
  gradient_blob: GradientBlobRenderer,
  particles: ParticlesRenderer,
  aurora: AuroraRenderer,
};

export const visualizationMetadata: VisualizationMetadata[] = [
  gradientBlobMeta,
  particlesMeta,
  auroraMeta,
];

export type VisualizationType = keyof typeof visualizations;

export function getRenderer(type: string): VisualizationRenderer | null {
  return visualizations[type] || null;
}
```

**Step 2: Commit**

```bash
git add frontend/src/lib/visualizations/index.ts
git commit -m "feat: add visualization registry"
```

---

## Task 7: Create VisualizationBackground Component

**Files:**
- Create: `frontend/src/components/common/VisualizationBackground.svelte`

**Step 1: Write the component**

```svelte
<!-- ABOUTME: Full-screen WebGL visualization background. -->
<!-- ABOUTME: Renders animated backgrounds behind slide content. -->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getRenderer, type ThemeData, type SlideConfig, type Palette } from '../../lib/visualizations';

  export let theme: ThemeData | null = null;
  export let currentSlide: string = 'intro';

  let canvas: HTMLCanvasElement;
  let gl: WebGLRenderingContext | null = null;
  let currentRenderer: ReturnType<typeof getRenderer> = null;
  let animationId: number | null = null;
  let lastTime = 0;

  const defaultPalette: Palette = {
    primary: '#1DB954',
    secondary: '#191414',
    accent: '#1ed760',
    background: '#121212',
    text: '#ffffff',
  };

  const defaultSlideConfig: SlideConfig = {
    visualization: 'gradient_blob',
    mood: 'calm',
    intensity: 0.5,
  };

  $: palette = theme?.palette || defaultPalette;
  $: slideConfig = theme?.slides?.[currentSlide] || defaultSlideConfig;

  function initWebGL() {
    if (!canvas) return;
    gl = canvas.getContext('webgl');
    if (!gl) {
      console.error('WebGL not supported');
      return;
    }
    resizeCanvas();
  }

  function resizeCanvas() {
    if (!canvas || !gl) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl.viewport(0, 0, canvas.width, canvas.height);
  }

  function switchRenderer(vizType: string) {
    if (currentRenderer) {
      currentRenderer.destroy();
    }
    currentRenderer = getRenderer(vizType);
    if (currentRenderer && gl) {
      currentRenderer.init(gl, palette);
    }
  }

  function animate(time: number) {
    const deltaTime = time - lastTime;
    lastTime = time;

    if (gl && currentRenderer) {
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
      currentRenderer.update(deltaTime, slideConfig.mood, slideConfig.intensity);
    }

    animationId = requestAnimationFrame(animate);
  }

  $: if (gl && slideConfig.visualization) {
    switchRenderer(slideConfig.visualization);
  }

  onMount(() => {
    initWebGL();
    switchRenderer(slideConfig.visualization);
    animationId = requestAnimationFrame(animate);
    window.addEventListener('resize', resizeCanvas);
  });

  onDestroy(() => {
    if (animationId) cancelAnimationFrame(animationId);
    if (currentRenderer) currentRenderer.destroy();
    window.removeEventListener('resize', resizeCanvas);
  });
</script>

<canvas
  bind:this={canvas}
  class="fixed inset-0 w-full h-full -z-10"
/>
```

**Step 2: Commit**

```bash
git add frontend/src/components/common/VisualizationBackground.svelte
git commit -m "feat: add VisualizationBackground component"
```

---

## Task 8: Integrate Background into WrappedExperience

**Files:**
- Modify: `frontend/src/components/WrappedExperience.svelte`

**Step 1: Add theme prop and background component**

Add to imports at top:
```svelte
import VisualizationBackground from './common/VisualizationBackground.svelte';
```

Add theme to the data type and props:
```typescript
export let data: {
  // ... existing fields
  theme?: {
    palette: { primary: string; secondary: string; accent: string; background: string; text: string };
    slides: Record<string, { visualization: string; mood: string; intensity: number }>;
  };
};
```

Add background component after the opening div:
```svelte
<VisualizationBackground theme={data.theme} currentSlide={slides[currentSlide]} />
```

**Step 2: Commit**

```bash
git add frontend/src/components/WrappedExperience.svelte
git commit -m "feat: integrate visualization background into wrapped experience"
```

---

## Task 9: Create ThemeGenerator in CLI

**Files:**
- Modify: `cli/src/last_wrapped/ai/generators.py`
- Create test first: `cli/tests/test_ai/test_generators.py` (add to existing)

**Step 1: Write the failing test**

Add to `cli/tests/test_ai/test_generators.py`:

```python
class TestThemeGenerator:
    def test_generates_theme_with_palette_and_slides(self) -> None:
        """Theme generator creates palette and per-slide configs."""
        response = '''{
            "palette": {
                "primary": "#F39C12",
                "secondary": "#8E44AD",
                "accent": "#E74C3C",
                "background": "#1a1a2e",
                "text": "#ffffff"
            },
            "slides": {
                "intro": {"visualization": "aurora", "mood": "dramatic", "intensity": 0.8},
                "totalTime": {"visualization": "particles", "mood": "celebratory", "intensity": 0.6}
            }
        }'''
        provider = MockProvider(response)
        generator = ThemeGenerator(provider)

        result = generator.generate({"top_genres": ["hip-hop", "rap"]})

        assert provider.last_prompt is not None
        assert "visualization" in provider.last_prompt.lower()

    def test_prompt_includes_available_visualizations(self) -> None:
        """Prompt includes list of available visualization types."""
        provider = MockProvider('{"palette": {}, "slides": {}}')
        generator = ThemeGenerator(provider)

        generator.generate({})

        assert "gradient_blob" in provider.last_prompt
        assert "particles" in provider.last_prompt
        assert "aurora" in provider.last_prompt
```

**Step 2: Run test to verify it fails**

Run: `cd cli && uv run pytest tests/test_ai/test_generators.py::TestThemeGenerator -v`
Expected: FAIL with "cannot import name 'ThemeGenerator'"

**Step 3: Add ThemeGenerator to generators.py**

Add import at top:
```python
from last_wrapped.ai.generators import ThemeGenerator
```

Add class at end of `cli/src/last_wrapped/ai/generators.py`:

```python
class ThemeGenerator(BaseGenerator):
    """Generates visual theme with color palette and per-slide visualizations."""

    AVAILABLE_VISUALIZATIONS = [
        {"id": "gradient_blob", "name": "Gradient Blob", "bestFor": ["warm", "introspective", "calm"]},
        {"id": "particles", "name": "Particles", "bestFor": ["celebratory", "reflective", "dreamy"]},
        {"id": "aurora", "name": "Aurora", "bestFor": ["dramatic", "mystical", "epic"]},
    ]

    SLIDES = [
        "intro", "totalTime", "topArtist", "topTracks", "listeningClock",
        "quirkyStats", "personality", "aura", "roasts", "narrative", "share"
    ]

    def generate(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Generate theme from user stats."""
        viz_info = json.dumps(self.AVAILABLE_VISUALIZATIONS, indent=2)
        slides_list = json.dumps(self.SLIDES)

        prompt = f"""You are creating a visual theme for a Last.fm Wrapped experience based on the user's 2024 listening habits.

User Stats:
{json.dumps(stats, indent=2)}

Available Visualizations:
{viz_info}

Slides to configure: {slides_list}

Based on the user's music taste and personality, create:
1. A color palette (5 colors) that reflects their musical vibe
2. A visualization type and mood for each slide

Moods can be: dramatic, mystical, warm, introspective, celebratory, reflective, energetic, playful, chaotic, analytical, triumphant

Return ONLY valid JSON in this format:
{{
    "palette": {{
        "primary": "#hexcolor",
        "secondary": "#hexcolor",
        "accent": "#hexcolor",
        "background": "#hexcolor",
        "text": "#ffffff"
    }},
    "slides": {{
        "intro": {{"visualization": "aurora", "mood": "dramatic", "intensity": 0.8}},
        "totalTime": {{"visualization": "particles", "mood": "celebratory", "intensity": 0.6}},
        ... (all slides)
    }}
}}
"""

        response = self.provider.generate(prompt, max_tokens=2048)
        return self._parse_json(response)
```

**Step 4: Run test to verify it passes**

Run: `cd cli && uv run pytest tests/test_ai/test_generators.py::TestThemeGenerator -v`
Expected: PASS

**Step 5: Commit**

```bash
git add cli/src/last_wrapped/ai/generators.py cli/tests/test_ai/test_generators.py
git commit -m "feat: add ThemeGenerator for visual theming"
```

---

## Task 10: Wire ThemeGenerator into Orchestrator

**Files:**
- Modify: `cli/src/last_wrapped/orchestrator.py`

**Step 1: Find where AI generators are called and add ThemeGenerator**

Import ThemeGenerator and call it alongside other generators. Add theme to processed output.

**Step 2: Commit**

```bash
git add cli/src/last_wrapped/orchestrator.py
git commit -m "feat: wire ThemeGenerator into processing pipeline"
```

---

## Task 11: Update Astro Page to Pass Theme Data

**Files:**
- Modify: `frontend/src/pages/[user]/[year]/index.astro`

**Step 1: Add theme to data transformation**

Add after existing data transformations:
```javascript
theme: stats.ai_content?.theme || null,
```

**Step 2: Commit**

```bash
git add frontend/src/pages/[user]/[year]/index.astro
git commit -m "feat: pass theme data to WrappedExperience"
```

---

## Task 12: Generate Visualization Manifest

**Files:**
- Create: `frontend/scripts/generate-manifest.js`
- Modify: `frontend/package.json`

**Step 1: Write the manifest generator script**

```javascript
// ABOUTME: Generates visualization manifest for CLI consumption.
// ABOUTME: Run during build to export available visualizations.

import { writeFileSync } from 'fs';
import { visualizationMetadata } from '../src/lib/visualizations/index.js';

const manifest = {
  visualizations: visualizationMetadata,
  generatedAt: new Date().toISOString(),
};

writeFileSync(
  'dist/visualization-manifest.json',
  JSON.stringify(manifest, null, 2)
);

console.log('Generated visualization manifest');
```

**Step 2: Add script to package.json**

Add to scripts:
```json
"generate-manifest": "node scripts/generate-manifest.js",
"build": "astro build && npm run generate-manifest"
```

**Step 3: Commit**

```bash
git add frontend/scripts/generate-manifest.js frontend/package.json
git commit -m "feat: add visualization manifest generation"
```

---

## Task 13: End-to-End Test

**Step 1: Rebuild and re-process**

```bash
cd cli && uv run last-wrapped process
cd ../frontend && npm run build
npm run preview
```

**Step 2: Verify in browser**

- Open http://localhost:4321/Felix/2025/
- Check that background visualization appears
- Click through slides and verify transitions

**Step 3: Commit any fixes**

```bash
git add -A
git commit -m "fix: end-to-end integration fixes"
```
